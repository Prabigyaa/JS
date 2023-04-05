"""
The lsp server

TODO make the server logic abstract and implement this for multiple languages
TODO Link diagnostic, code actions and quick fixes.

For now, the logic for diagnostic, code action and fixes are not linked.
For proper handling of diagnostic and creating code action and fixes based on the diagnostics
these things should be properly linked and made dynamic as to scale properly if new features are added

Also, the language supported is only python for now.

"""


import random

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

server = LanguageServer("nlpserver", "v0.1")


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
    """
    document = server.workspace.get_document(params.text_document.uri)
    current_line_number = params.position.line

    identifier_with_comments, identifier_with_points = parse_document(document)

    completion_items = []

    for identifier, comments in identifier_with_comments.items():
        for (start, end) in identifier_with_points[identifier]:
            if (current_line_number == start[0]) or (current_line_number == end[0]):
                # TODO Variable naming logic goes here
                # var_name = get_variable_name_from_comments(comments)

                completion_items.append(CompletionItem("variable_name_1"))
                completion_items.append(
                    CompletionItem("Variable_name_2", kind=CompletionItemKind.Variable)
                )

    return CompletionList(is_incomplete=False, items=completion_items)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def create_warnings(params: DidChangeTextDocumentParams):
    """
    Create warnings for incorrect variable names

    TODO check incorrect/ non-optimal variable names
    """
    document = server.workspace.get_document(params.text_document.uri)

    identifier_with_comments, identifier_with_points = parse_document(document)
    warnings_list: list[Diagnostic] = []

    for identifer, points in identifier_with_points.items():

        # randomly setting the hint for now
        if random.randint(0, 1):
            severity = DiagnosticSeverity.Hint
            message = f"Change to Variable Name: {random.random() * 100}"
        else:
            severity = DiagnosticSeverity.Warning
            message = "Variable Name Change Required"

        for start, end in points:
            warnings_list.append(
                Diagnostic(
                    Range(Position(*start), Position(*end)),
                    message,
                    severity=severity,
                    source="NLP Comment Naming Extension",
                )
            )

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

        document = ls.workspace.get_document(text_document.uri)
        problem_start = document.offset_at_position(range.start)
        problem_end = document.offset_at_position(range.end)

        old_identifier = document.source[problem_start:problem_end]

        # TODO new_identifier_logic
        new_identifier = f"{old_identifier}_{random.randint(0, 10)}"

        versioned_text_document = VersionedTextDocumentIdentifier(
            document.version or 0, document.uri
        )
        edits = [TextEdit(range=range, new_text=new_identifier)]

        workspacedit = WorkspaceEdit(
            document_changes=[
                TextDocumentEdit(text_document=versioned_text_document, edits=edits)
            ]
        )

        ls.apply_edit(workspacedit)


@server.feature(TEXT_DOCUMENT_CODE_ACTION)
def on_code_action(params: CodeActionParams) -> list[CodeAction]:
    """
    Publish rename Identifier code action

    """

    return [
        CodeAction(
            "Rename Identifier",
            CodeActionKind.QuickFix,
            command=Command(
                title="rename_identifer",
                # the way it's implemented in other projects is not to give command here but handle that in CODE_ACTION_RESOLVE
                command="nlp-bridge.rename_identifier",
                arguments=[params.text_document, params.range],
            ),
        )
    ]


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
            "Created Language objects for languages:" +
            str(treesitter.LANGUAGES_BEING_PARSED)
        )
    else:
        log("Failed to create language objects.")


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
