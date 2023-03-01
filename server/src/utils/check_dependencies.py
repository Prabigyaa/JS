'''
    Outputs the serialized dictionary of 'found' and 'not_found' dependencies
'''

import sys
import pathlib
import importlib
import typing
import json

from includes import SERVER_DIR

REQUIREMENTS_FILE = pathlib.Path.joinpath(SERVER_DIR, "requirements.txt")

def get_both() -> dict[str, list]:
    '''
    Returns dictionary containing keys "found" and "not_found".

    The lists might be empty.
    '''
    deps_found = []
    deps_required = []

    with open(REQUIREMENTS_FILE) as req_f:

        # iterating over the lines to find the installed and not installed dependencies
        for line in req_f.readlines():
            package = line.strip()
            if package != "": # if not empty
                try:
                    importlib.import_module(package)
                    deps_found.append(package)
                except ImportError :
                    deps_required.append(package)

    output = {
        "found": deps_found,
        "not_found": deps_required
    }

    return output

def get_install_required() -> typing.List:
    '''
    Returns the list of packages which are required to be installed.

    This list might be empty
    '''
    return get_both().get("not_found", [])

if __name__=="__main__":
    print(json.dumps(get_both()), file=sys.stdout)