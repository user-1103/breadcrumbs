"""
Module for displaying the data.
"""

from typing import List
from rich import print
from rich.panel import Panel
from pytodotxt import Task

# Wether to print in a undecorated form
SIMPLE = False

from rich.console import Console
console = Console()

def crumb(crumbs: List[Task]) -> None:
    """
    Prints the crumbs provided.

    :param crumbs: The list of crumbs to print.
    """
    to_print = list()
    for c in crumbs:
        tmp = "```markdown\n"
        is_arc = ""
        tmp += (f"# {
