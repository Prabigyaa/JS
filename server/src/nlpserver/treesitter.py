import pathlib
import os
from subprocess import CalledProcessError

from tree_sitter import Language, Parser

from pathlib import Path
import sys

from typing import Callable, Any
from concurrent.futures import Future

import asyncio

# adding src to path
module_path = Path(__file__).resolve()
src_path = module_path.parents[1]

if str(src_path) not in sys.path:
    sys.path.append(str(src_path))  # adding src folder to path

from utils.includes import SERVER_DIR


LANGUAGE_REPOS_DIR = pathlib.Path.joinpath(SERVER_DIR, "language_repos")

# creating the language repo dir if it doesn't exist
if not os.path.exists(LANGUAGE_REPOS_DIR):
    os.mkdir(LANGUAGE_REPOS_DIR)

BUILD_DIR = pathlib.Path.joinpath(SERVER_DIR, "build")

# creating the build dir if it doesn't exist
if not os.path.exists(BUILD_DIR):
    os.mkdir(BUILD_DIR)

# languages
LANGUAGES = ["python", "c"]
LANGUAGE_OBJECTS: list[Language] = []
LANGUAGES_BEING_PARSED: list[str] = []

# the parser
PARSER: Parser = Parser()

# base git url
BASE_URL = "https://github.com/tree-sitter"


async def create_language_objects(
    log_output: Callable[..., None] | None = None
) -> bool:
    """
    Expects a callback function for logging.

    Returns True if at least one language object could be created false otherwise
    """

    def language_to_process(language):
        if log_output is not None:
            log_output(
                f"Cloning {BASE_URL}/tree-sitter-{language} to {LANGUAGE_REPOS_DIR.__str__()}"
            )
        return asyncio.create_subprocess_exec(
            "git",
            "clone",
            f"{BASE_URL}/tree-sitter-{language}",
            cwd=LANGUAGE_REPOS_DIR.__str__(),
        )

    processes: list[asyncio.subprocess.Process | Exception] = await asyncio.gather(
        *map(language_to_process, LANGUAGES),
        return_exceptions=True,
    )

    # keeping track of failed processes
    failed: list[int] = []
    for i, process in enumerate(processes):
        if process is asyncio.subprocess.Process:
            return_code = await process.wait()

            # this isn't full proof (except POSIX)
            if return_code is not None and return_code > 0:
                if log_output is not None:
                    log_output(f"Completed cloning language repo for {LANGUAGES[i]}")
            else:
                failed.append(i)
                if log_output is not None:
                    log_output(
                        f"Failed cloning language repo for {LANGUAGES[i]}"
                    )

    succeded = [language for i, language in enumerate(LANGUAGES) if i not in failed]

    # exit if none of the processes succeded
    if not succeded.__len__() > 0:
        if log_output is not None:
            log_output("Couldn't create language object.")
        return False

    library_path = pathlib.Path.joinpath(BUILD_DIR, "languages.so")
    # building the language library
    Language.build_library(
        # Store the library in the `build` directory
        library_path.__str__(),
        # Include one or more languages
        [
            pathlib.Path.joinpath(
                LANGUAGE_REPOS_DIR, f"tree-sitter-{language}"
            ).__str__()
            for language in succeded
        ],
    )

    for language in succeded:
        LANGUAGE_OBJECTS.append(Language(library_path.__str__(), language))
        LANGUAGES_BEING_PARSED.append(language)

    return True


def set_parsing_language(language: str) -> bool:
    """
    Set the given language as the language being parsed.

    Returns True if the language object is present False otherwise
    """

    found: bool = False
    for lang in LANGUAGE_OBJECTS:
        if lang.name == language:
            found = True

            PARSER.set_language(lang)

            break

    return found


if __name__ == "__main__":
    asyncio.run(create_language_objects(print))
    set_parsing_language("c")
