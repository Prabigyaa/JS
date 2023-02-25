from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionList,
    CompletionParams,
)

from typing import Literal

VARIABLE_NAME_CHANGE: Literal = "variableName/change"

server = LanguageServer('nlpserver', 'v0.1')

@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(params: CompletionParams):
    items = []
    document = server.workspace.get_document(params.text_document.uri)
    current_line = document.lines[params.position.line].strip()
    if current_line.endswith("hello."):
        items = [
            CompletionItem(label="world"),
            CompletionItem(label="friend"),
        ]
    return CompletionList(is_incomplete=False, items=items)

@server.command(VARIABLE_NAME_CHANGE)
def change_variable_name(params: any):
    document = server.workspace.get_document(params.text_document.uri)

    comment_list = []
    line = 1
    while(line <= document.lines()):
        if(document.lines[line].strip().startswith('#')):
            comment_list.append(document.lines[line])
    
    server.send_notification(VARIABLE_NAME_CHANGE, comment_list)
    

server.start_io()
