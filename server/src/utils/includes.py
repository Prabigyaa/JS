import pathlib
import platform

SERVER_DIR: pathlib.Path = pathlib.Path(__file__).parents[2]
PYTHON_EXECUTABLE: pathlib.Path = pathlib.Path.joinpath(
    SERVER_DIR, "Scripts" if platform.system() == "Windows" else "bin", "python"
)


def set_server_dir(new_dir: str):
    global SERVER_DIR

    SERVER_DIR = pathlib.Path(new_dir)


def set_python_executable(new_path: str):
    global PYTHON_EXECUTABLE

    PYTHON_EXECUTABLE = pathlib.Path(new_path)


def print_all():
    print({"SERVER_DIR": SERVER_DIR, "PYTHON_EXECUTABLE": PYTHON_EXECUTABLE})


if __name__ == "__main__":
    print_all()
