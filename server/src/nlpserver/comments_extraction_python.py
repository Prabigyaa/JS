from pygls.workspace import Document
from tree_sitter import Node

import treesitter

from pathlib import Path

from collections import defaultdict

import events

# paths
CURRENT_DIR = Path(__file__).parents[0]
COMMENTS_EXTRACTION_QUERY_FILE = CURRENT_DIR.joinpath("comments_extraction_python.scm")

# the current_document being parsed
DOCUMENT: Document | None = None


def set_document(document: Document):
    global DOCUMENT
    DOCUMENT = document


def read_callable(byte_offset, point) -> bytes | None:
    """
    Function for reading a document incrementally.
    """
    if DOCUMENT is None:
        return None

    row, column = point
    if row >= len(DOCUMENT.lines) or column >= len(DOCUMENT.lines[row]):
        return None
    return DOCUMENT.lines[row][column:].encode("utf8")


def get_query_from_file(file: Path) -> str | None:
    """
    To get the query as string
    """
    query_string: str | None = None
    try:
        with open(file=file, mode="r") as f:
            query_string = f.read()
    except FileNotFoundError:
        query_string = None

    return query_string


def associate_comment_with_identifier(
    node_types_and_nodes: dict[str, list[Node]], document: Document
):
    identifier_with_comment: dict[str, list[str]] = defaultdict(list)
    identifer_with_points: dict[str, list[tuple[tuple[int, int], tuple[int, int]]]] = defaultdict(list)

    docstrings: list[Node] = node_types_and_nodes["string"]
    identifiers: list[Node] = node_types_and_nodes["identifier"]
    comments: list[Node] = node_types_and_nodes["comment"]

    # checking identifiers after docstring
    for node in docstrings:
        end_line = node.end_point[0]
        valid_start_line = range(end_line, end_line+2)

        for identifier in identifiers:
            # if the identifier starts immediately after the docstring
            if identifier.start_point[0] in valid_start_line:
                identifier_name = document.source[identifier.start_byte: identifier.end_byte]
                identifer_with_points[identifier_name].append((identifier.start_point, identifier.end_point))
                identifier_with_comment[identifier_name].append(document.source[node.start_byte: node.end_byte])

    # checking docstring after function definition
    for node in identifiers:
        end_line = node.end_point[0]
        valid_start_line = range(end_line, end_line+2)

        for docstring in docstrings:
            # if the docstring starts immediately after the identifier
            if docstring.start_point[0] in valid_start_line:
                identifier_name = document.source[node.start_byte: node.end_byte]
                identifer_with_points[identifier_name].append((node.start_point, node.end_point))
                identifier_with_comment[identifier_name].append(document.source[docstring.start_byte: docstring.end_byte])

    # checking identifiers after comments
    for node in comments:
        end_line = node.end_point[0]
        valid_start_line = range(end_line, end_line+2)

        for identifier in identifiers:
            # if the docstring starts immediately after the identifier
            if identifier.start_point[0] in valid_start_line:
                identifier_name = document.source[identifier.start_byte: identifier.end_byte]
                identifer_with_points[identifier_name].append((identifier.start_point, identifier.end_point))
                identifier_with_comment[identifier_name].append(document.source[node.start_byte: node.end_byte])

    # associating lone comments with points
    lone_comment_with_point: dict[str, tuple[tuple[int, int], tuple[int, int]]] = defaultdict(tuple)

    identifier_comment_list: list[str] = []
    for identifier, comment in identifier_with_comment.items():
        identifier_comment_list.extend(comment)

    # for all comments not in any other categories
    for node in comments:
        comment = document.source[node.start_byte: node.end_byte]

        not_with_identifier = comment not in identifier_comment_list

        if not_with_identifier:
            lone_comment_with_point[comment] = (node.start_point, node.end_point)

    return (identifier_with_comment, identifer_with_points, lone_comment_with_point)


def parse_document(
    document: Document,
) -> tuple[
    dict[str, list[str]], dict[str, list[tuple[tuple[int, int], tuple[int, int]]]], dict[str, tuple[tuple[int, int], tuple[int, int]]]
]:
    """ """

    set_document(document)

    # associating node name with nodes
    node_name_and_nodes: dict[str, list[Node]] = defaultdict(list)

    # association node type with nodes
    node_types_and_nodes: dict[str, list[Node]] = defaultdict(list)

    # associating identifiers with comments
    identifier_with_comment: dict[str, list[str]] = defaultdict(list)

    # associating comments with points
    lone_comments_with_points: dict[str, tuple[tuple[int, int], tuple[int, int]]] = {}

    # associating identifiers with points
    # Point: ((start_line, start_char), (end_line, end_char))
    identifer_with_points: dict[str, list[tuple[tuple[int, int], tuple[int, int]]]] = defaultdict(list)

    tree = treesitter.PARSER.parse(read_callable)

    if treesitter.PROPERTIES["current-language"] is not None:
        query_str = get_query_from_file(COMMENTS_EXTRACTION_QUERY_FILE)

        if query_str is not None:
            query = treesitter.PROPERTIES["current-language"].query(query_str)
            captures = query.captures(tree.root_node)

            for node, node_name in captures:
                # removing the duplicate entries
                if node not in node_name_and_nodes[node_name]:
                    node_name_and_nodes[node_name].append(node)

                if node not in node_types_and_nodes[node.type]:
                    node_types_and_nodes[node.type].append(node)


            for node_type, nodes in node_types_and_nodes.items():
                events.post_event("log", f"\n{node_type}: {nodes}\n")

            for node_name, nodes in node_name_and_nodes.items():
                events.post_event("log", f"\n{node_name}: {nodes}\n")

            (
                identifier_with_comment,
                identifer_with_points,
                lone_comments_with_points
            ) = associate_comment_with_identifier(node_types_and_nodes, document)

            for identifier, comments in identifier_with_comment.items():
                points = identifer_with_points[identifier]
                events.post_event("log", f"{identifier}: {comments}, Points: {points}")

    return (identifier_with_comment, identifer_with_points, lone_comments_with_points)
