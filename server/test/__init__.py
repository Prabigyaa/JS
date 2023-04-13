import pathlib
import sys

SERVER_DIR = pathlib.Path(__file__).parents[1]

# adding the server dir to paths
if str(SERVER_DIR) not in sys.path:
    sys.path.append(str(SERVER_DIR))
