"""
A module that defines the root plugin (which defines the defaults) and the
method for loading plugins.
"""

from typing import Callable, Dict, Any, List
from pathlib import Path
from os.path import isdir, isfile
from os import mkdir

from rich.progress import Progress
from rich import print
from breadcrumbs.plugin_dir import directory
import importlib.util
import sys

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

def null_function(*args, name:str = "<unknown>", **argd) -> Callable:
    """
    This should never be called and is a placeholer.

    :param name: Which config value is this standing in for.
    """
    def null():
        raise Exception(f"Required config value {name} never set!")
    return null

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
        "imports": ['display', 'core', 'future',
                    'metrics', 'default_macros', 'fun'],
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
            "debug": null_function(name="display_settings.debug.debug"),
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
            "debug": null_function(name="display_settings.normal.debug"),
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
            "debug": null_function(name="display_settings.json.debug"),
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
            "debug": null_function(name="display_settings.simple.debug"),
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
        "MOTD": [],
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
        'plugins': {"root": plugin_data},
        "breadbox": breadbox,
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

directory["root"] = load_plugin

def recurse_plugins(config_array: List[Dict[str, Any]], plugin: str,
                    p: Progress) -> None:
    """
    Recursively searches and loads each found config to the config_array.

    :param config_array: Collection of loaded plugins.
    :param plugin: Ether a path to find the plugin file or a name in the plugin
    directory.
    :param p: The progress display object.
    """
    t2 = p.add_task(f" ⮡ Loading Plugin: [bold]{plugin}[/bold].", total=100)
    plug_location = directory.get(plugin, None)
    if (plug_location is None):
        plug_path = Path(plugin)
        spec = importlib.util.spec_from_file_location(plugin, plug_path)
        tmp = importlib.util.module_from_spec(spec)
        sys.modules[plugin] = tmp
        spec.loader.exec_module(tmp)
        ret = tmp.load_plugin()
        p.advance(t2, 20)
    else:
        ret = plug_location()
        p.advance(t2, 20)
    config_array.append(ret)
    imports = ret['plugins'][plugin]["imports"]
    if (imports):
        t2_left = (100-20)/len(imports)
    else:
        t2_left = (100-20)
        p.advance(t2, t2_left)
    for x in imports:
        recurse_plugins(config_array, x, p)
        p.advance(t2, t2_left)
    p.update(t2, description=f" ⮡ Loaded Plugin: [bold]{plugin}[/bold].")

def merge_config(a: Dict[str, Any], b: Dict[str, Any]) -> None:
    """
    Merges two dictionaries nix style, recursively. Dictionaries will be recursed
    and lists will be appended. Everything else is sourced from a or b. Preference
    is given to a. Elements will be taken from b and put in a.

    :param a: The (overriding) dict.
    :param b: The other dict.
    """
    for k, v in a.items():
        if (k in b.keys()):
            if (isinstance(b[k], type(v))):
                if (isinstance(b[k], dict)):
                    merge_config(a[k], b[k])
                elif (isinstance(b[k], list)):
                    a[k] += b[k]
                else:
                    a[k] = b[k]
            else:
                a[k] = b[k]
    for k, v in b.items():
        if (k not in a.keys()):
            a[k] = v


def collect_config(p: Progress) -> Dict[str, Any]:
    """
    Starting from the root plugin, collects all plugins and returns the final
    config.

    :param p: The progress display object.
    """
    t3 = p.add_task("⮡ Loading Config.", total=100)
    config_array = list()
    recurse_plugins(config_array, "root", p)
    p.advance(t3, 20)
    final_conf = config_array[0]
    if (config_array):
        t3_left = (100-20)/len(config_array[1:])
    else:
        t3_left = (100-20)
        p.advance(t3, t3_left)
    for c in config_array[1:]:
        merge_config(final_conf, c)
        p.advance(t3, t3_left)
    p.update(t3, description="⮡ Loaded Config.")
    return final_conf

