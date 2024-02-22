from appdirs import AppDirs
from pathlib import Path
import os
import inventory_manager.secrets as secret

app_dirs = AppDirs("Inventory Manager", "Shin Umeda", "1.0")
dir = app_dirs.user_config_dir

default_files = {
    "secrets.json": secret.secretjson
}


def getFile(filename: str) -> Path:
    if not os.path.exists(dir):
        os.makedirs(dir)
    return Path(dir) / filename


def loadFile(filename: str) -> Path:
    if not os.path.exists(dir):
        os.makedirs(dir)
    f = Path(dir) / filename
    if filename not in default_files:
        raise IndexError()
    if not f.exists():
        f.write_text(default_files[filename])
    return Path(dir) / filename
