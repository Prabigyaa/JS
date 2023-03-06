from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionList,
    CompletionParams,
    TEXT_DOCUMENT_DID_CHANGE,
    DidChangeTextDocumentParams,
)

from comment_parser import comment_parser

server = LanguageServer("nlpserver", "v0.1")


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

    mime = None
    language_id = document.language_id

    if language_id == "python":
        mime = "text/x-python"
    elif language_id == "javascript":
        mime = "application/javascript"
    elif language_id == "c++":
        mime = "text/x-c++"
    elif language_id == "c":
        mime = "text/x-c"
    elif language_id == "html":
        mime = "text/html"
    elif language_id == "java":
        mime = "text/x-java-source"
    elif language_id == "shell":
        mime = "text/x-shellscript"

    comments = comment_parser.extract_comments(document.path, mime=mime)

    # making a list
    comments_list = []
    for comment in comments:
        comments_list.append(
            [comment.line_number(), comment.text(), comment.is_multiline()]
        )

    server.show_message_log(comments_list.__str__())


def start_server():
    server.start_io()


if __name__ == "__main__":
    start_server()
