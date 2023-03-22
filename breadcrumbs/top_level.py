"""
Module that orchestrates the other modules.
"""

from argparse import ArgumentParser
from breadcrumbs.configs import HookTypes, load_config
from signal import SIGINT, signal
from sys import exit

from breadcrumbs.display import SIMPLE, DEBUG, info, prompt
from breadcrumbs.loaf import Loaf, call_hooks, parse

def on_exit(signum, stack) -> None:
    """
    Calls the redigested EXIT hooks on kill signal
    """
    info("Mañana")
    call_hooks(HookTypes.EXIT)
    exit(0)


signal(SIGINT, on_exit)

def run() -> None:
    """
    Loads a loaf, and allows the user to modify it.
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

    :params loaf: The loaf to edit in the repl.
    """
    while True:
        tmp = prompt()
        parse(tmp)



