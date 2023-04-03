"""
Module that orchestrates the other modules.
"""
from argparse import ArgumentParser, Namespace
from signal import SIGINT, signal
from sys import exit

from breadcrumbs.display import SIMPLE, DEBUG, clear, debug, info, prompt
from breadcrumbs.loaf import init_loaf, parse, call_hooks
from breadcrumbs.config import HookTypes

def on_exit(signum, stack) -> None:
    """
    Calls the redigested EXIT hooks on kill signal.
    """
    info(" Mañana")
    call_hooks(HookTypes.EXIT)
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
    parser.add_argument('crumb_command',
                        metavar='[C]',
                        nargs='?',
                        default="",
                        help='The crumb command to run.')
    args = parser.parse_args()
    return args

def run() -> None:
    """
    Loads a loaf in a cli, and allows the user to modify it.
    """
    global DEBUG, SIMPLE
    signal(SIGINT, on_exit)
    args = parse_cli_args()
    init_loaf()
    debug("Parsed args, loaded Loaf, and registered signals.")
    # TODO should these be moved into the loaf config?
    if (args.simple):
        SIMPLE = True
    if (args.debug):
        DEBUG = True
    call_hooks(HookTypes.INIT)
    if (args.crumb_command):
        parse(args.crumb_command)
    else:
        repl()

def repl() -> None:
    """
    Runs a repl to manage the crumbs.
    """
    clear()
    while True:
        tmp = prompt()
        parse(tmp)
