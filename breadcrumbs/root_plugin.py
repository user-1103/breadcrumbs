"""
A module that defines the root plugin (which defines the defaults) and the
method for loading plugins.
"""

from typing import Dict, Any
from pathlib import Path
from os.path import isdir, isfile
from os import mkdir

from pytodotxt import TodoTxt

class UnsetConfig():
    """
    Dummy class to identify unset config issues better than with None.
    """
    ...

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

def null_function(*args, name:str = "<unknown>", **argd) -> None:
    """
    This should never be called and is a placeholer.

    :param name: Which config value is this standing in for.
    """
    raise Exception(f"Required config value {name} never set!")

def ping_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Returns with 'pong' with no display magic. Used for debuging.
    - Does not save under any condition.
    """
    print("...pong")
    return False

def enter_debug_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Drops the user into a PDB shell. Used for debuging.
    - Does not save under any condition.
    """
    breakpoint()
    return False

def load_plugin() -> Dict[str, Any]:
    """
    This is a function that will do what it need to to load the 'plugin' and
    return a string keyed dictionary that will be merged with all other plugins
    to form the final running config.

    :return: The configuration of the plugin.
    """

    breadbox = ensure_breadbox()
    user_conf = Path(breadbox + "/config.py")
    breadbox_path = Path(breadbox)

    plugin_data = {
        "author": "USER 1103",
        "website": "https://github.com/user-1103/breadcrumbs",
        "version": "0.1",
        "description": "The root plugin.",
        "imports": [user_conf],
        "lib": {},
        "help": {
            "usage": ("If you are reading this, you are already using this"
                      " plugin")
        }
    }

    display_settings = {
        "debug": {
            "crumb": null_function(name="display_settings.debug.crumb"),
            "figure": null_function(name="display_settings.debug.figure"),
            "info": null_function(name="display_settings.debug.info"),
            "warn": null_function(name="display_settings.debug.warn"),
            "err": null_function(name="display_settings.debug.err"),
            "fatal": null_function(name="display_settings.debug.fatal"),
            "clear": null_function(name="display_settings.debug.clear"),
            "title": null_function(name="display_settings.debug.title"),
            "prompt": null_function(name="display_settings.debug.prompt")
        },
        "normal": {
            "crumb": null_function(name="display_settings.normal.crumb"),
            "figure": null_function(name="display_settings.normal.figure"),
            "info": null_function(name="display_settings.normal.info"),
            "warn": null_function(name="display_settings.normal.warn"),
            "err": null_function(name="display_settings.normal.err"),
            "fatal": null_function(name="display_settings.normal.fatal"),
            "clear": null_function(name="display_settings.normal.clear"),
            "title": null_function(name="display_settings.normal.title"),
            "prompt": null_function(name="display_settings.normal.prompt")
        },
        "json": {
            "crumb": null_function(name="display_settings.json.crumb"),
            "figure": null_function(name="display_settings.json.figure"),
            "info": null_function(name="display_settings.json.info"),
            "warn": null_function(name="display_settings.json.warn"),
            "err": null_function(name="display_settings.json.err"),
            "fatal": null_function(name="display_settings.json.fatal"),
            "clear": null_function(name="display_settings.json.clear"),
            "title": null_function(name="display_settings.json.title"),
            "prompt": null_function(name="display_settings.json.prompt")
        },
        "simple": {
            "crumb": null_function(name="display_settings.simple.crumb"),
            "figure": null_function(name="display_settings.simple.figure"),
            "info": null_function(name="display_settings.simple.info"),
            "warn": null_function(name="display_settings.simple.warn"),
            "err": null_function(name="display_settings.simple.err"),
            "fatal": null_function(name="display_settings.simple.fatal"),
            "clear": null_function(name="display_settings.simple.clear"),
            "title": null_function(name="display_settings.simple.title"),
            "prompt": null_function(name="display_settings.simple.prompt")
        }
    }

    hooks = {
        "INIT": [],
        "PREMACRO": [],
        "PRECMD": [],
        "CMDERR": [],
        "CMDOK": [],
        "POSTCMD": [],
        "EXIT": [],
        "SAFEEXIT": [],
        "FATALEXIT": [],
        "PRINTCRUMB": [],
        "PRINTFIGURE": [],
        "PRINTFIGURE": [],
    }

    commands = {
        "ping": ping_cmd,
        "debug": enter_debug_cmd
    }

    buffers = {
        'loaf': UnsetConfig(),
        'selection_buffer': [],
        'selection_buffer_exp': 0.0,
        'input_raw': "",
        'input_post_macro': "",
        'cmd': "",
        'args': "",
        'err': Exception("If you are seeing this, something has gone *very* wrong.")
    }

    macros = {}

    config = {
        "root_plugin": plugin_data,
        "breadbox": breadbox_path,
        "display": display_settings,
        "hooks": hooks,
        'commands': commands,
        'default_command': null_function(name="default_command"),
        'null_command': null_function(name="null_command"),
        'default_date': '1989-04-15',
        'default_time': '06-28',
        'default_span': '1d-~',
        'default_sequence': 'n-1d',
        'buffers': buffers,
        'editor': "vim %P",
        'log': display_settings["normal"],
        'macros': macros
    }

    return config




