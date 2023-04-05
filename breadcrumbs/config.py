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
            dh.collect_metrics_hook
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
        # Arguments
        r"^\?m (.*)": dc.collect_metrics_cmd,
        r"^\?v (.*)": dc.search_cmd,
        r"^\?v! (.*)": dc.search_archive_cmd,
        r"^\?vv (.*)": dc.advanced_search_cmd,
        r"^\?f (.*)": dc.check_future_cmd,
        r"^\?b (.*)": dc.block_cmd,
        r"^\?e (.*)": dc.add_cmd,
        r"^\?e! (.*)": dc.raw_add_cmd,
        # No arguments
        r"^\?a": dc.archive_cmd,
        r"^\?A": dc.unarchive_cmd,
        r"^\?hm": dc.list_metrics_cmd,
        r"^\?hv": dc.list_buffer_cmd,
        r"^\?h": dc.help_cmd,
        r"^\?u": dc.undo_cmd,
        r"^\?debug": dc.debug_cmd,
        r"^\?l": dc.list_cmd,
        r"^\?f": dc.check_future_now_cmd,
        r"^\?m": dc.collect_all_metrics_cmd,
        # Defaults
        r"^\?.*": dc.nop_cmd,
        r"^(.*)": dc.add_cmd
    },
    "macros": {
        r"\.\.t (\S*)": r"TRACK:\1", # start a tracking session
        r"\.\.m (\S*)": r"MOOD:\1", # start a tracking session
        r"\.\.f (\S*)": r"FUTURE:\1", # Mark for the future
        r"\.\.n (\S*)": r"\1:1", # Genaric metric note
        r"\.\.c (\S*) (\S*)\.?": r"COST:\1/\2" # Cost str
    },
    "metrics": [
        (span,        "TRACK",        {},         True),
        (span,        "MOOD",         {},         True),
        (run_total,   "COST",         {},         True),
        (total_table, "brush",        {},         True),
        (total_table, "floss",        {},         True),
        (total_table, "mwash",        {},         True),
        (total_table, "shavef",       {},         True),
        (total_table, "shaveb",       {},         True),
        (total_table, "showere",      {},         True),
        (total_table, "showern",      {},         True),
        (total_table, "vit",          {},         True),
        (total_table, "zol",          {},         True),
        (total_table, "thy",          {},         True),
        (total_table, "laundry",      {},         True),
        (total_table, "sclean",       {},         True),
        (total_table, "fclean",       {},         True),
        (total_table, "exe",          {},         True),
        (total_table, "str",          {},         True),
        (total_table, "wake",         {},         True),
        (total_table, "meal",         {},         True),
        (total_table, "sleep",        {},         True)
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
