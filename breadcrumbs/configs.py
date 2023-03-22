"""
Module for loading in the loaf config.
"""

from enum import Enum, auto
from pathlib import Path
from typing import Dict, Any
import breadcrumbs.default_commands as dc
import importlib.util
import sys

from breadcrumbs.display import debug

class HookTypes(Enum):
    """
    The types of hooks that can be hooked.
    """
    INIT = auto()
    EXIT = auto()
    PREMACRO = auto()
    PRE = auto()
    POST = auto()
    OK = auto()
    ERR = auto()

def collect_config(path: Path) -> Dict[str, Any]:
    """
    Loads the API objects described in the given file.

    :param path: The path to load the 'api.py' from.
    :return: The user config.
    """
    try:
        spec = importlib.util.spec_from_file_location("user_conf", path)
        user_conf = importlib.util.module_from_spec(spec)
        sys.modules["user_conf"] = user_conf
        spec.loader.exec_module(user_conf)
        ret = user_conf.CONFIG
    except Exception as e:
        ret = dict()
    return ret

DEFAULT_PATH = (".breadbox")
DEFAULT_CONFIG_PATH = Path(f"{DEFAULT_PATH}/config.py")
DEFAULT_LOAF_PATH = Path(f"{DEFAULT_PATH}/default.loaf")

DEFAULT_CONFIG = {
    "hooks": {
        HookTypes.INIT: [
        ],
        HookTypes.EXIT: [
        ],
        HookTypes.PRE: [
        ],
        HookTypes.POST: [
        ],
        HookTypes.ERR: [
        ]
    },
    "cmds": {
        r"^\?\?r (.*)": dc._reg,
        r"^\?\?d": dc._debug,
        r"^\?\?f (.*)": dc._search,
        r"^\?\?l ?(.*)": dc._list,
        r"^\?\?a (.*)": dc._archive,
        r"^\?\?.*": dc._nop,
        r"^(.*)": dc._add
    },
    "macros": {
        r"\.\.test (.*), (.*)\.": r"TEST \2 \1"
    },
    "loaf": DEFAULT_LOAF_PATH,
    "config": DEFAULT_CONFIG_PATH
}

def load_config() -> Dict[str, Any]:
    """
    Load the user config from the breadbox and merges it with the default.

    :return: The user config.
    """
    user_conf = collect_config(DEFAULT_CONFIG_PATH)
    ret = DEFAULT_CONFIG | user_conf
    debug(ret)
    return ret
