"""
Contains Loaf based stuff.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Match, Tuple, Union
from pytodotxt import TodoTxt, Task
from argparse import ArgumentParser
from re import search, sub
from breadcrumbs.display import crumb, err, debug, clear
from datetime import datetime, timedelta
from itertools import filterfalse
from enum import Enum, auto
from functools import wraps
from breadcrumbs.configs import HookTypes, load_config

@dataclass
class Loaf():
    """
    Represents the entire log system as it is modified by the tool.
    """
    # Config from the config file
    config_data: Dict[str, Any]
    # The crumbs
    crumbs: TodoTxt = None

    def __post_init__(self) -> None:
        self.crumbs = TodoTxt(Path(self.config_data["loaf"]))
        self.crumbs.parse()
        def sort_days(x: Task) -> Tuple[int, int, int, int, int]:
            day = x.creation_date
            day_tup = tuple()
            if (day is None):
                day_tup = (1970, 1, 2)
            else:
                day_tup = day.timetuple()
            time_txt = x.attributes.get("TIME", ["01-01"])[0]
            time_list = time_txt.split("-")
            time_tup = (*day_tup, int(time_list[0]), int(time_list[1]))
            return time_tup
        self.crumbs.tasks.sort(key=sort_days)
        self.crumbs.save()
        def day_parse(x: Task) -> bool:
            tmp = x.creation_date
            if (tmp is None):
                tmp = datetime.now().date()
            ret = (tmp <= (datetime.now() - timedelta(days=1)).date())
            ret = (ret or bool(x.is_completed))
            return ret
        res = list(filterfalse(day_parse, self.crumbs.tasks))
        clear()
        crumb(res, "24hr OF CRUMBS")

def expand_macros(user_input: str) -> str:
    """
    Expand macros in the input text.

    :param user_input: The unprocessed user input.
    :return: The user_input with expanded macros.
    """
    for before, after in LOAF.config_data["macros"].items():
        tmp = search(before, user_input)
        if (tmp):
            user_input = sub(before, after, user_input)
    return user_input

def parse(user_input: str) -> None:
    """
    Takes a breadcrumb command and processes it.

    :param user_input: The unprocessed user input.
    """
    if (not user_input):
        return
    debug("STAGE 0:")
    debug(user_input)
    LOAF.config_data.update({"current_cmd": user_input})
    call_hooks(HookTypes.PREMACRO)
    user_input = LOAF.config_data["current_cmd"]
    debug("STAGE 1 (POST PREMACRO):")
    debug(user_input)
    user_input = expand_macros(user_input)
    LOAF.config_data.update({"expanded_cmd": user_input})
    debug("STAGE 2 (POST MACRO):")
    debug(user_input)
    args: Union[None, Match] = None
    cmd= lambda x,y: ...
    for reg, cmd in LOAF.config_data["cmds"].items():
        args = search(reg, user_input)
        if (args):
            break
    debug("STAGE 4 (POST CMD SEARCH):")
    debug(cmd)
    LOAF.config_data.update({"cmd_match_obj": args})
    call_hooks(HookTypes.PRE)
    args = LOAF.config_data["cmd_match_obj"]
    try:
        if (args):
            debug("STAGE 5 (POST PRE):")
            debug(args.groups())
            cmd(LOAF, *args.groups())
        else:
            raise Exception("Could not find a way to parse this :(")
    except Exception as e:
        call_hooks(HookTypes.ERR)
        err(e)
    else:
        call_hooks(HookTypes.OK)
    call_hooks(HookTypes.POST)

def call_hooks(hook: HookTypes) -> None:
    """
    Calls all hooks registered with a given name.

    :args hook: The type of the hook in it.
    """
    h = LOAF.config_data["hooks"].get(hook, None)
    if (not h):
        return
    debug(f"Calling internal hook {hook}")
    for hook_call in h:
        debug(f"Calling {hook_call.__name__}")
        hook_call(LOAF)

CONFIG = load_config()
LOAF = Loaf(config_data=CONFIG)
