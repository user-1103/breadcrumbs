"""
Contains basic Loaf based stuff.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Match, Union, List
from pytodotxt import TodoTxt, Task
from re import search, sub
from breadcrumbs.display import err, debug, info
from breadcrumbs.config import collect_config, HookTypes, load_config
from breadcrumbs.utils import save
from enum import Enum, auto
from time import time

# The global config state
CONFIG: Union[None, Dict[str, Any]] = None
# The current load being managed
LOAF: Union[None, 'Loaf'] = None

@dataclass
class Loaf():
    """
    Represents a collection of crumbs.
    """
    # Config from the config file
    config_data: Dict[str, Any]
    # The crumbs
    crumbs: Union[TodoTxt, None] = None
    # selection.buffer
    buffer: Union[List[Task], None] = None
    # selection.buffer timeout time
    buffer_time: float = 0

    def __post_init__(self) -> None:
        """
        Actually loads in a loaf from disk form the config path.
        """
        self.crumbs = TodoTxt(Path(self.config_data["loaf"]))
        self.crumbs.parse()
        if (self.crumbs.tasks is not None):
            save(self)

    def get_buffer(self) -> List[Task]:
        """
        Gets the active buffer, returns an empty buffer if it has timed out.

        :returns: The active buffer.
        """
        if ((self.buffer_time <= time()) or (self.buffer is None)):
            self.buffer_time = (time() + 30)
            self.buffer = list()
        else:
            self.buffer_time += 30
        return self.buffer

    def set_buffer(self, data: List[Task]) -> None:
        """
        Sets the active buffer, resets the timeout.

        :param data: The value to set the buffer to.
        """
        self.buffer_time = (time() + 30)
        self.buffer = data

def expand_macros(user_input: str) -> str:
    """
    Expands macros in the input text.

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
    debug("STAGE 0 (RAW TEXT):")
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
        LOAF.config_data.update({"cmd_err_obj": e})
        call_hooks(HookTypes.ERR)
        err(e)
    else:
        call_hooks(HookTypes.OK)
    call_hooks(HookTypes.POST)

def init_loaf() -> None:
    """
    Sets up the global LOAF and CONFIG vars so they may be used.
    MUST BE CALLED BEFORE LOAF USAGE!
    """
    global LOAF, CONFIG
    CONFIG = load_config()
    LOAF = Loaf(config_data=CONFIG)
    debug(f"Loaded Loaf {LOAF}.")

def call_hooks(hook: HookTypes) -> None:
    """
    Calls all hooks registered with a given name.

    :args hook: The type of the hook in it.
    """
    h = LOAF.config_data["hooks"].get(hook, None)
    if (not h):
        return
    debug(f"Calling internal hook {hook}.")
    for hook_call in h:
        debug(f"Calling {hook_call.__name__}")
        hook_call(LOAF)

