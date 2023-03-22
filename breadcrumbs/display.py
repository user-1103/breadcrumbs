"""
Module for displaying the data.
"""

from typing import Any, List
from rich.panel import Panel
from pytodotxt import Task
from rich.syntax import Syntax
import pygments.lexers.textfmts.TodotxtLexer as lex

# Wether to print in a undecorated form
SIMPLE = False
# To print debug info
DEBUG = True

from rich.console import Console, RenderableType
console = Console()

def clear() -> None:
    """
    Clears output, depending on SIMPLE.
    """
    if (SIMPLE):
        return
    console.clear()

def crumb(crumbs: List[Task], title: str = '') -> None:
    """
    Prints the crumbs provided.

    :param crumbs: The list of crumbs to print.
    :param title: The title of the crumb group.
    """
    to_print = list()
    if (title):
        if (SIMPLE):
            print(f"[{title}]")
        else:
            console.rule(title)
    for c in crumbs:
        if (SIMPLE):
            print(str(c.description))
        else:
            tmp = Panel(Syntax(str(c.description), lexer="todotxt"))
            console.print(tmp)

def figure(figures: List[RenderableType], title: str = '') -> None:
    """
    Prints the figures provided.

    :param crumbs: The list of crumbs to print.
    :param title: The title of the crumb group.
    """
    to_print = list()
    if (title):
        if (SIMPLE):
            print(f"<{title}>")
        else:
            console.rule(title)
    for c in figures:
        if (SIMPLE):
            console.print(c)
        else:
            tmp = Panel(c, border_style="blue")
            console.print(tmp)

def debug(text: Any) -> None:
    """
    Prints debug info if enabled.

    :param text: The debug text.
    """
    if (not DEBUG):
        return
    console.log(text)

def err(e: Exception) -> None:
    """
    Prints a recoverable err.

    :param e: The recoverable err.
    """
    console.log(e)

def info(text: str)  -> None:
    """
    Print some info for the user.

    :param text: The debug text.
    """
    text = f"🡢 {text}"
    if (SIMPLE):
        print(text)
    else:
        console.print(text)

def prompt()  -> str:
    """
    Print some info for the user.

    :return: The picked choice.
    """
    return input(f"🡠 ")

