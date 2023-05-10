"""
The lsp server

TODO make the server logic abstract and implement this for multiple languages
TODO Link diagnostic, code actions and quick fixes.

For now, the logic for diagnostic, code action and fixes are not linked.
For proper handling of diagnostic and creating code action and fixes based on the diagnostics
these things should be properly linked and made dynamic as to scale properly if new features are added

Also, the language supported is only python for now.

"""


import events
import treesitter
from comments_extraction_python import parse_document
from lsprotocol.types import (
    INITIALIZE,
    INITIALIZED,
    TEXT_DOCUMENT_CODE_ACTION,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    CodeAction,
    CodeActionKind,
    CodeActionParams,
    Command,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    InitializedParams,
    InitializeParams,
    Position,
    Range,
    ServerCapabilities,
    TextDocumentContentChangeEvent_Type1,
    TextDocumentEdit,
    TextDocumentIdentifier,
    TextEdit,
    VersionedTextDocumentIdentifier,
    WorkspaceEdit,
)
from pygls.protocol import _dict_to_object
from pygls.server import LanguageServer

from collections import defaultdict, Counter

from predict_variables import initalize_model, get_variable_name, MODEL, TOKENIZER
from variable_conventions import VariableConventions, get_convention
from convert import set_convention


server = LanguageServer("nlpserver", "v0.1")

# setting these global as these are updated on each document update
IDENTIFIER_WITH_COMMENTS: dict[str, set[str]] = defaultdict(set)
IDENTIFIER_WITH_POINTS: dict[
    str, set[tuple[tuple[int, int], tuple[int, int]]]
] = defaultdict(set)
# Empty dict
ALL_LONE_COMMENTS: dict[str, tuple[tuple[int, int], tuple[int, int]]] = {}

# keeping track of previous inferences
COMMENTS_AND_VARIABLE_NAME: dict[str, set[str]] = defaultdict(set)

# the convention begin followed up to now
FOLLOWED_CONVENTION: VariableConventions = VariableConventions.Undefined


def get_variable_name_with_cache(comment: str, force_regenerate=False, **kwargs):
    """
    Returns the variable from cache if available if not
    gets the variable name from model
    """
    global COMMENTS_AND_VARIABLE_NAME

    if len(comment) < 1:  # not a empty string
        return

    # the set keeps one variable name, i.e. whole name not the parts
    if not force_regenerate and len(COMMENTS_AND_VARIABLE_NAME[comment]) > 0:
        variable_set = COMMENTS_AND_VARIABLE_NAME[comment].copy()
    else:
        var_name = get_variable_name(comment, **kwargs)
        variable_set = set()
        if var_name is not None:

            #TODO the logic needs to change based on the type of identifier
            var_with_convention = set_convention(var_name.split(), FOLLOWED_CONVENTION)

            variable_set.add(var_with_convention)


            COMMENTS_AND_VARIABLE_NAME[comment].add(var_with_convention)
    
    yield variable_set.pop()


@server.feature(TEXT_DOCUMENT_DID_OPEN)
def document_open(params: DidOpenTextDocumentParams):
    """
    On opening text document, the server should set the language for the parser

    Also, publish warnings like some text document has changed
    """
    log(f"Opened text document of language {params.text_document.language_id}")

    language = params.text_document.language_id

    if treesitter.set_parsing_language(language=language):
        log(f"Successfully set the language to {language}.")

    # just a hack, needs change or different diagnostic method on initialization
    create_warnings(  # create warning on first initialization
        DidChangeTextDocumentParams(
            VersionedTextDocumentIdentifier(
                0
                if params.text_document.version is None
                else params.text_document.version,
                params.text_document.uri,
            ),
            [
                TextDocumentContentChangeEvent_Type1(
                    Range(Position(0, 0), Position(0, 0)), text=""
                )
            ],
        )
    )


@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(params: CompletionParams):
    """
    Suggest completions for variable names

    TODO get variable names based on the comments

    Doesn't work properly

    TODO create a way to suggest variable name right after comment
    """
    document = server.workspace.get_document(params.text_document.uri)
    current_line_number = params.position.line
    current_line_start_index = document.offset_at_position(
        Position(current_line_number, 0)
    )
    current_pos_index = document.offset_at_position(params.position)

    completion_items = []

    # give completion suggestion if it's a variable name after comment
    for (
        identifier,
        comments,
    ) in IDENTIFIER_WITH_COMMENTS.items():  # checking for all the comments

        for comment in comments:
            for (start, end) in IDENTIFIER_WITH_POINTS[identifier]:
                if (current_line_number == start[0]) or (current_line_number == end[0]):

                    if TOKENIZER is not None:
                        force_words_ids = TOKENIZER(identifier, add_special_tokens=False).input_ids
                        
                        # passing the already present incomplete identifier/ not sure if this works
                        var_names = get_variable_name_with_cache(comment, force_regenerate=True, force_words_ids=force_words_ids)
                    else:
                        var_names = get_variable_name_with_cache(comment)

                    for var_name in var_names:
                        if var_name is not None:
                            completion_items.append(
                                CompletionItem(
                                    var_name, kind=CompletionItemKind.Keyword, filter_text=identifier # hack for vscode filtering out variable not containing the already typed characters.
                                )
                            )

    return CompletionList(is_incomplete=False, items=completion_items)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def create_warnings(params: DidChangeTextDocumentParams):
    """
    Create warnings for incorrect variable names

    TODO check incorrect/ non-optimal variable names
    """
    global IDENTIFIER_WITH_COMMENTS, IDENTIFIER_WITH_POINTS, ALL_LONE_COMMENTS, FOLLOWED_CONVENTION

    document = server.workspace.get_document(params.text_document.uri)

    IDENTIFIER_WITH_COMMENTS, IDENTIFIER_WITH_POINTS, ALL_LONE_COMMENTS = parse_document(document)
    warnings_list: list[Diagnostic] = []

    for identifer, points in IDENTIFIER_WITH_POINTS.items():
        
        if IDENTIFIER_WITH_COMMENTS[identifer] is not None:
            severity = DiagnosticSeverity.Hint
            variable_name = next(get_variable_name_with_cache(" ".join(IDENTIFIER_WITH_COMMENTS[identifer])), None)

            # don't create hints if it's the same name
            if variable_name == identifer:
                continue

            if variable_name is not None:
                message = f"Change to variable name {variable_name}"

                for start, end in points:
                    warnings_list.append(
                        Diagnostic(
                            Range(Position(*start), Position(*end)),
                            message,
                            severity=severity,
                            source="NLP Comment Naming Extension",
                            code="WN_100",  # wrong name
                        )
                    )
    FOLLOWED_CONVENTION = get_major_conventions()

    server.publish_diagnostics(document.uri, warnings_list)


@server.command("nlp-bridge.rename_identifier")
def rename_identifier(ls: LanguageServer, *args):
    """ "
    Rename the identifier on rename request

    TODO get new identifier name based on the comments
    """
    list_args = args[0]

    """
    This is very static, may fail if parameters are changed in any way.
    TODO change this
    """
    text_document = TextDocumentIdentifier(_dict_to_object(list_args[0]).uri)
    range = Range(
        _dict_to_object(list_args[1]).start, _dict_to_object(list_args[1]).end
    )

    # TODO change this to not use any hacks
    if (
        isinstance(list_args, list)
        and isinstance(text_document, TextDocumentIdentifier)
        and isinstance(range, Range)
    ):
        range = Range(Position(range.start.line, range.start.character),
                      Position(range.end.line, range.end.character))
        document = ls.workspace.get_document(text_document.uri)
        problem_start = document.offset_at_position(range.start)
        problem_end = document.offset_at_position(range.end)

        old_identifier = document.source[problem_start:problem_end]

        comments = IDENTIFIER_WITH_COMMENTS[old_identifier]
        if len(comments) > 0:
            new_identifier = next(get_variable_name_with_cache(" ".join(comments)), None)

            if new_identifier is not None:
                versioned_text_document = VersionedTextDocumentIdentifier(
                    document.version or 0, document.uri
                )
                edits = [TextEdit(range=range, new_text=new_identifier)]

                other_locations = IDENTIFIER_WITH_POINTS.get(old_identifier)

                if other_locations is not None:
                    for start, end in other_locations:
                        _range = Range(Position(*start), Position(*end))
                        # if hasn't been edited
                        if _range != range:
                            edits.append(TextEdit(range=_range, new_text=new_identifier))

                workspacedit = WorkspaceEdit(
                    document_changes=[
                        TextDocumentEdit(text_document=versioned_text_document, edits=edits)
                    ]
                )

                ls.apply_edit(workspacedit)


@server.feature(TEXT_DOCUMENT_CODE_ACTION)
def on_code_action(params: CodeActionParams) -> list[CodeAction] | None:
    """
    Publish rename Identifier code action

    """

    document = params.text_document
    range = params.range

    # check if code action are available for given range

    # checking if variable name can be improved

    improvable = False

    for identifier, _ranges in IDENTIFIER_WITH_POINTS.items():

        # if the variable doens't have an associated comment/s
        # we cannot suggest a name
        # TODO suggest convention change based on the overall project/ files
        if len(IDENTIFIER_WITH_COMMENTS[identifier]) < 1:
            continue

        for (start, end) in _ranges:
            if (
                range.start.line >= start[0] and range.end.line <= end[0]
            ):  # if in between the lines of identifer
                if (
                    range.start.character >= start[1] and range.end.character <= end[1]
                ):  # if in between the characters of identifer
                    improvable = True
                    break

    return (
        [
            CodeAction(
                "Rename Identifier",
                CodeActionKind.QuickFix,
                command=Command(
                    title="rename_identifer",
                    # the way it's implemented in other projects is not to give command here but handle that in CODE_ACTION_RESOLVE
                    command="nlp-bridge.rename_identifier",
                    arguments=[document, range],
                ),
            )
        ]
        if improvable
        else None
    )


def get_major_conventions() -> VariableConventions:
    global IDENTIFIER_WITH_POINTS

    all_conventions: list[VariableConventions] = []

    for identifier, _ in IDENTIFIER_WITH_POINTS.items():
        all_conventions.append(*get_convention(identifier))

    counter = Counter(all_conventions)

    most_common_convention: VariableConventions = counter.most_common(1)[0][0]

    if most_common_convention is None:
        return VariableConventions.Undefined
    else:
        return most_common_convention


@server.feature(INITIALIZE)
def on_initialize(params: InitializeParams) -> ServerCapabilities:
    """
    Register server capabilities on initialization

    TODO properly set all the server capabilities
    """

    return ServerCapabilities(
        code_action_provider=True,
        completion_provider=CompletionOptions(resolve_provider=True),
    )


@server.feature(INITIALIZED)
async def after_initialized(params: InitializedParams):
    """
    Setup tree_sitter after initialization
    """

    log("Attempting to create language objects.")

    succeded = await treesitter.create_language_objects()

    if succeded:
        log(
            "Created Language objects for languages:"
            + str(treesitter.LANGUAGES_BEING_PARSED)
        )
    else:
        log("Failed to create language objects.")

    log("Initializing model")

    initalize_model(use_local=True)  


@events.on_event("log")
def log_to_output(message: str):
    server.show_message_log(message)


def log(message: str):
    events.post_event("log", message)


def start_server():
    """
    Starts the server
    """
    server.start_io()

    # nothing after this will be executed as server runs on loop


if __name__ == "__main__":
    start_server()
