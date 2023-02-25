import venv
import sys, pathlib

def get_server_directory() -> pathlib.Path:
    return pathlib.Path(__file__).parents[2]

def create_venv():
    server_dir = get_server_directory().__str__()
    try:
        venv.create(server_dir, with_pip=True, system_site_packages=True, upgrade_deps=True, symlinks=True)
    except Exception as e:
        print('Error: %s' % e, file=sys.stderr)
        print('Virtual Environment might already be present')

create_venv()