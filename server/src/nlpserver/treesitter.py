import pathlib
import os

from tree_sitter import Language, Parser

from pathlib import Path
import sys

from typing import Callable

import asyncio

# adding src to path
module_path = Path(__file__).resolve()
src_path = module_path.parents[1]

if str(src_path) not in sys.path:
    sys.path.append(str(src_path))  # adding src folder to path

# importing only after src is in system path (python paths)
from utils.includes import SERVER_DIR


# the directory in which the language repositories will be downloaded
LANGUAGE_REPOS_DIR = pathlib.Path.joinpath(SERVER_DIR, "language_repos")

# creating the language repo dir if it doesn't exist
if not os.path.exists(LANGUAGE_REPOS_DIR):
    os.mkdir(LANGUAGE_REPOS_DIR)

# output folder for .so file created by build_library function
BUILD_DIR = pathlib.Path.joinpath(SERVER_DIR, "build")

# creating the build dir if it doesn't exist
if not os.path.exists(BUILD_DIR):
    os.mkdir(BUILD_DIR)

# languages
LANGUAGES = ["python", "c"]

# updated only after the language library is built
LANGUAGE_OBJECTS: list[Language] = []
LANGUAGES_BEING_PARSED: list[str] = []

# the language parser
PARSER: Parser = Parser()

# base git url containing the language repos
BASE_URL = "https://github.com/tree-sitter"


async def create_language_objects(
    log_output: Callable[..., None] | None = None
) -> bool:
    """
    Expects a callback function for logging.

    Returns True if at least one language object could be created false otherwise
    """

    def language_to_process(language):
        """
        Useful for mapping each language to process in which it is being cloned.

        Returns Coroutines conatining the processes
        """
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

    # the processes being executed or done executing
    processes: list[asyncio.subprocess.Process | Exception] = await asyncio.gather(
        *map(language_to_process, LANGUAGES),
        return_exceptions=True,
    )

    # keeping track of failed processes
    failed: list[int] = []
    for i, process in enumerate(processes):
        if isinstance(process, asyncio.subprocess.Process):
            return_code = await process.wait()

            # this isn't full proof (except POSIX)
            if return_code is not None and return_code > -1:
                if log_output is not None:
                    log_output(f"Completed cloning language repo for {LANGUAGES[i]}")
            else:
                failed.append(i)
                if log_output is not None:
                    log_output(
                        f"Failed cloning language repo for {LANGUAGES[i]}, Error Code: {return_code}"
                    )

    # if it didn't fail then it probably succeeded
    succeded = [language for i, language in enumerate(LANGUAGES) if i not in failed]

    # exit if none of the processes succeded
    if not succeded.__len__() > 0:
        if log_output is not None:
            log_output("Couldn't create language object.")
        return False

    library_path = pathlib.Path.joinpath(BUILD_DIR, "languages.so")
    # building the language library
    if Language.build_library(
        # Store the library in the `build` directory
        library_path.__str__(),
        # Include one or more languages
        [
            pathlib.Path.joinpath(
                LANGUAGE_REPOS_DIR, f"tree-sitter-{language}"
            ).__str__()
            for language in succeded
        ],
    ):
        if log_output is not None:
            log_output(f"Built library with languages {succeded}")

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
        if lang.name.lower() == language.lower():
            found = True

            PARSER.set_language(lang)

            break

    return found


if __name__ == "__main__":
    asyncio.run(create_language_objects(print))
    set_parsing_language("c")
