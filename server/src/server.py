
from pygls.server import LanguageServer

def start():
    server = LanguageServer('nlp-server', 'v0.1')

    server.start_io()

start()