import atexit
from datetime import datetime
import json
import logging
from appdirs import AppDirs
from pathlib import Path
import os

app_dirs = AppDirs("Inventory Manager", "Shin Umeda", "1.0")
dir = app_dirs.user_config_dir
logs = app_dirs.user_log_dir

default_files = {
    "config.json": "{}",
}


def getLogpath() -> Path:
    if not os.path.exists(logs):
        os.makedirs(logs)
    return Path(logs) / f"log-{datetime.now()}.txt".replace(" ", "-")


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


gconfig = json.loads(loadFile("config.json").read_text())


def write_config():
    f = loadFile("config.json")
    f.write_text(json.dumps(gconfig))


atexit.register(write_config)
