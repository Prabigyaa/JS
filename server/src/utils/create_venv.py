"""
    Exits with exit code 0 if virtual environment is already present or
    has been created successfully.

    Outputs the python executable path to stdout

    Dumps error to stderr if some error is encounterd.
"""

import venv
import sys
import json
import platform

from includes import SERVER_DIR, PYTHON_EXECUTABLE, set_python_executable


def is_virtual_env_available() -> bool:
    """
    Returns true if the python installation corresponds to a virtual environment.
    """
    real_prefix = getattr(sys, "real_prefix", None)  # fallback for virtualenv < 20
    base_prefix = getattr(sys, "base_prefix", sys.prefix)

    return (base_prefix or real_prefix) != sys.prefix


def create_venv() -> bool:
    try:
        # difficult to create symlinks in windows
        use_symlinks = not platform.system() == "Windows"
        env_builder = venv.EnvBuilder(
            with_pip=True,
            system_site_packages=use_symlinks,  # if windows, there is no point in copying whole lot of packages
            upgrade_deps=True,
            symlinks=use_symlinks,  # difficult to create symlinks in windows
        )
        env_builder.create(SERVER_DIR)
        set_python_executable(
            env_builder.ensure_directories(SERVER_DIR).__getattribute__("env_exec_cmd")
        )
        return True
    except Exception as e:
        print("Error: %s" % e, file=sys.stderr)
        return False


if __name__ == "__main__":
    creation_required = not is_virtual_env_available()
    exit_code = 0

    if creation_required:  # virtual environment might already be present
        exit_code = not create_venv()  # ensuring same exit code

    output = {
        # the python executable path might be useful for subsequent dependencies installation and others
        "PYTHON_EXECUTABLE": PYTHON_EXECUTABLE.__str__()
    }

    print(json.dumps(output), file=sys.stdout)

    sys.exit(exit_code)
