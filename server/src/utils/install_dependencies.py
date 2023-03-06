"""
Exits with code 0 if dependency installation succeeds

Dumps the list of failed intallations to stderr
"""

import sys
import pip
from check_dependencies import get_install_required


def install_deps() -> bool:
    required_dependencies = get_install_required()
    success = True

    failed_deps = []

    for package in required_dependencies:
        try:
            pip.main(["install", package])
        except Exception:
            failed_deps.append(package)

            success = False
    print(failed_deps, file=sys.stderr)

    return success


if __name__ == "__main__":
    sys.exit(not install_deps())
