from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionList,
    CompletionParams,
    TEXT_DOCUMENT_DID_CHANGE,
    DidChangeTextDocumentParams,
    TEXT_DOCUMENT_DID_OPEN,
    DidOpenTextDocumentParams,
    INITIALIZED,
    InitializedParams,
)

import treesitter

import events

from comments_extraction_python import parse_document

server = LanguageServer("nlpserver", "v0.1")


@server.feature(TEXT_DOCUMENT_DID_OPEN)
def document_open(params: DidOpenTextDocumentParams):
    """
    On opening text document, the server should set the language for the parser
    """
    log(f"Opened text document of language {params.text_document.language_id}")

    language = params.text_document.language_id

    if treesitter.set_parsing_language(language=language):
        log(f"Successfully set the language to {language}.")


@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(params: CompletionParams):
    """
    Just for checking if the extension initialized successfully.

    When `hello.` is typed and `ctrl + space` is pressed,
    it should give completion options `world` and `friend`.
    """
    items = []
    document = server.workspace.get_document(params.text_document.uri)
    current_line = document.lines[params.position.line].strip()
    if current_line.endswith("hello."):
        items = [
            CompletionItem(label="world"),
            CompletionItem(label="friend"),
        ]
    return CompletionList(is_incomplete=False, items=items)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def add_quick_fix_required(params: DidChangeTextDocumentParams):
    document = server.workspace.get_document(params.text_document.uri)

    identifier_with_comments, identifier_with_points = parse_document(document)

    """
        TODO
    """


@events.on_event("log")
def log_to_output(message: str):
    server.show_message_log(message)


def log(message: str):
    events.post_event("log", message)


@server.feature(INITIALIZED)
async def after_initialized(params: InitializedParams):
    log("Attempting to create language objects.")

    succeded = await treesitter.create_language_objects()

    if succeded:
        log(
            f"Created Language objects for languages: {treesitter.LANGUAGES_BEING_PARSED}"
        )
    else:
        log("Failed to create language objects.")


def start_server():
    """
    Starts the server
    """
    server.start_io()

    # nothing after this will be executed as server runs on loop


if __name__ == "__main__":
    start_server()
