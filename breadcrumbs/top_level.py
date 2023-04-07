"""
Module that orchestrates the other modules.
"""
from argparse import ArgumentParser, Namespace
from pathlib import Path
from re import Match, search, sub
from signal import SIGINT, signal
from sys import exit
from typing import Dict, Union, Any

from pytodotxt import TodoTxt

from breadcrumbs.root_plugin import collect_config
from breadcrumbs.utils import save
import readline

# The global config state
CONFIG: Union[None, Dict[str, Any]] = None
# The current load being managed
LOAF: Union[None, TodoTxt] = None

def call_hooks(hook: str) -> None:
    """
    Calls all hooks registered with a given name.

    :args hook: The type of the hook to call.
    """
    h = CONFIG["hooks"].get(hook, None)
    if (not h):
        return
    CONFIG['log']['debug'](f"Calling internal hook {hook}.")
    for hook_call in h:
        CONFIG['log']['debug'](f"Calling {hook_call.__name__}")
        hook_call(CONFIG, LOAF)

def on_exit(signum, stack) -> None:
    """
    Calls the redigested EXIT hooks on kill signal.
    """
    CONFIG['log']['fatal'](" Mañana")
    call_hooks("SAFEEXIT")
    call_hooks("EXIT")
    exit(0)

def parse_cli_args() -> Namespace:
    """
    Parses the CLI arguments and returns a namespace of args.

    :returns: The parsed args.
    """
    parser = ArgumentParser(
                    prog='bc',
                    description=('A stream based todo list for confused people.'
                                 ' When a crumb command is provided, it will be'
                                 ' executed. Otherwise a REPL will be started'
                                 ' where you can send many commands.'))
    parser.add_argument('-d', "--debug", action="store_true",
                    help='Be chatty...')
    parser.add_argument('-s', "--simple", action="store_true",
                    help='Be less fancy when printing...')
    parser.add_argument('-j', "--json", action="store_true",
                    help='Talk json to me...')
    parser.add_argument('crumb_command',
                        metavar='[C]',
                        nargs='?',
                        default="",
                        help='The crumb command to run.')
    args = parser.parse_args()
    return args

def merge_cli_config(conf: Dict[str, Any], cli: Namespace) -> None:
    """
    Modify the final config with the given cli arguments.

    :param conf: The final config.
    :param cli: The parsed arg namespace.
    """
    if (cli.debug):
        conf['log'] = conf['display']['debug']
    if (cli.simple):
        conf['log'] = conf['display']['simple']
    if (cli.json):
        conf['log'] = conf['display']['json']

def init_loaf() -> None:
    """
    Sets up the global LOAF and CONFIG vars so they may be used.
    MUST BE CALLED BEFORE LOAF  / CONFIG USAGE!
    """
    global LOAF, CONFIG
    CONFIG = collect_config()
    loaf = TodoTxt(Path(CONFIG["breadbox"] + "/default.loaf"))
    loaf.parse()
    CONFIG["buffers"]["loaf"] = loaf
    LOAF = loaf

def expand_macros(user_input: str) -> str:
    """
    Expands macros in the input text.

    :param user_input: The unprocessed user input.
    :return: The user_input with expanded macros.
    """
    for name, (before, after) in CONFIG["macros"].items():
        user_input = sub(before, after, user_input)
    return user_input

def parse(user_input: str) -> None:
    """
    Takes a breadcrumb command and processes it.

    :param user_input: The unprocessed user input.
    """
    if (not user_input):
        return
    debug = CONFIG['log']['debug']
    err = CONFIG['log']['err']
    buffers = CONFIG['buffers']
    debug("STAGE 0 (RAW TEXT):")
    debug(user_input)
    buffers["input_raw"] = user_input
    call_hooks('PREMACRO')
    user_input = buffers["input_raw"]
    debug("STAGE 1 (POST PREMACRO):")
    debug(user_input)
    user_input = expand_macros(user_input)
    buffers["input_post_macro"] = user_input
    debug("STAGE 2 (POST MACRO):")
    debug(user_input)
    args: Union[None, Match] = None
    for reg, possible_cmd in CONFIG["commands"].items():
        reg = (r'^\?' + reg + r'((?:\s.*)|(?:$))')
        args = search(reg, user_input)
        if (args):
            buffers["cmd"] = possible_cmd
            buffers["args"] = args
            break
    call_hooks('PRECMD')
    do_save = False
    try:
        if (args):
            cmd = buffers["cmd"]
            args = buffers["args"]
            debug("STAGE 4 (POST CMD SEARCH):")
            debug(cmd)
            debug("STAGE 5 (POST PRE):")
            debug(args.groups())
            tmp_arg = args.groups()[0]
            if (tmp_arg.startswith(" ") and (len(tmp_arg) >= 2)):
                trim_arg = tmp_arg[1:]
            else:
                trim_arg = tmp_arg
            do_save = cmd(CONFIG, LOAF, trim_arg)
        else:
            if (user_input.startswith("?")):
                CONFIG['default_command'](CONFIG, LOAF, user_input)
            elif (len(user_input)):
                CONFIG['null_command'](CONFIG, LOAF, user_input)
    except Exception as e:
        buffers["err"] =  e
        call_hooks('CMDERR')
        err("Failed To Run Command.", e)
    else:
        call_hooks('CMDOK')
    call_hooks('POSTCMD')
    if (do_save):
        save(LOAF)

def run() -> None:
    """
    Loads a loaf in a cli, and allows the user to modify it.
    """
    signal(SIGINT, on_exit)
    args = parse_cli_args()
    init_loaf()
    call_hooks("INIT")
    merge_cli_config(CONFIG, args)
    if (args.crumb_command):
        parse(args.crumb_command)
    else:
        repl()
    on_exit(None, None)

def repl() -> None:
    """
    Runs a repl to manage the crumbs.
    """
    CONFIG['log']['clear']()
    while True:
        tmp = CONFIG['log']['prompt']()
        parse(tmp)
