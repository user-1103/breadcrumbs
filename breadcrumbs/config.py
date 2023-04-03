"""
Module for loading in the loaf config.
"""
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Any
import breadcrumbs.commands as dc
import breadcrumbs.hooks as dh
from os.path import isdir, isfile
from os import mkdir
import importlib.util
import sys
from breadcrumbs.metrics import span, run_total, total_table

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

def ensure_breadbox() -> str:
    """
    Ensures that a breadbox is present and retruns its location.
    Will check the current directory and then ~/.breadbox .
    If it is not found create a ~/.breadbox with a default.loaf

    :return: The location of the breadbox.
    """
    if (isdir(Path(".breadbox"))):
        if (not isfile(Path(".breadbox/default.loaf"))):
            Path(".breadbox/default.loaf").touch()
        return ".breadbox"
    else:
        home = Path.home()
        if (not isdir(Path(f"{home}/.breadbox"))):
            mkdir(Path(f"{home}/.breadbox"))
        if (not isfile(Path(f"{home}/.breadbox/default.loaf"))):
            Path(f"{home}/.breadbox/default.loaf").touch()
        return f"{home}/.breadbox"

DEFAULT_PATH = ensure_breadbox()
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
            dh.future_cast_hook,
            dh.collect_metrics_hook
        ],
        HookTypes.PREMACRO: [
        ],
        HookTypes.OK: [
        ],
        HookTypes.ERR: [
        ]
    },
    "cmds": {
        r"^\?help": dc.help_cmd,
        r"^\?debug": dc.debug_cmd,
        r"^\?l ?(.*)": dc.list_cmd,
        r"^\?f": dc.check_future_cmd,
        r"^\?m": dc.collect_metrics_cmd,
        r"^\?s (.*)": dc.search_cmd,
        r"^\?a (.*)": dc.archive_cmd,
        r"^\?A (.*)": dc.unarchive_cmd,
        r"^\?.*": dc.nop_cmd,
        r"^(.*)": dc.add_cmd
    },
    "macros": {
        r"\.\.t (.*)\.?": r"TRACK:\1", # start a tracking session
        r"\.\.m (.*)\.?": r"MOOD:\1", # start a tracking session
        r"\.\.f (.*)\.?": r"FUTURE:\1", # Mark for the future
        r"\.\.n (.*)\.?": r"\1:1", # Genaric metric note
        r"\.\.c (.*)\s(.*)\.?": r"COST:\1/\2" # Cost str
    },
    "metrics": [
        (span, "TRACK"),
        (span, "MOOD"),
        (run_total, "COST"),
        (total_table, "brush"),
        (total_table, "teeth"),
        (total_table, "mwash"),
        (total_table, "shavef"),
        (total_table, "shaveb"),
        (total_table, "showere"),
        (total_table, "showern"),
        (total_table, "vit"),
        (total_table, "zol"),
        (total_table, "thy"),
        (total_table, "laundry"),
        (total_table, "sclean"),
        (total_table, "fclean"),
        (total_table, "exe"),
        (total_table, "stretch"),
        (total_table, "wake"),
        (total_table, "sleep")
    ],
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
