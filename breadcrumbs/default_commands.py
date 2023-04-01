"""
The default commands that are available.
"""
from datetime import datetime, timedelta
from time import time
from pytodotxt import TodoTxt, Task
from breadcrumbs.display import crumb, console, info, clear, figure, rule
from breadcrumbs.default_hooks import _check_future_list
from re import search, I
from itertools import dropwhile, filterfalse
from rich.table import Table
from hashlib import md5

from breadcrumbs.utils import add_task, archive, loaf_search, save, unarchive, undo

def _add(loaf: object, text: str) -> None:
    """
    Adds a crumb to the loaf.

    :param loaf: The loaf being edited.
    :param text: the text of the file in todo.txt format.
    """
    add_task(loaf, text)
    save(loaf)
    res = loaf_search(loaf, time_str="1d-~", archived=False)
    clear()
    crumb(res, "BEADCRUMB TRAIL")

def _nop(loaf: object) -> None:
    """
    Do nothing.

    :param loaf: The loaf being edited.
    """
    info("Use ?help to list commands")
    
def _show_future(loaf: object) -> None:
    """
    See the future.

    :param loaf: The loaf being edited.
    """
    _check_future_list(loaf)

def _help(loaf: object) -> None:
    """
    Print the available crumb commands.

    :param loaf: The loaf being edited.
    """
    clear()
    rule("HELP")
    t = Table(title="Crumb Commands.", expand=True)
    t.add_column("Regex Of What You Type...")
    t.add_column("What Happens...")
    t.add_column("Command Or Macro?")
    for k, v in loaf.config_data["cmds"].items():
        t.add_row(k, v.__doc__, "Command")
    for k, v in loaf.config_data["macros"].items():
        t.add_row(k, v, "Macro")
    figure([t])

def _archive(loaf: object, crumb_id: str) -> None:
    """
    Archive a crumb from a loaf.

    :param loaf: The loaf being edited.
    :param crumb_id: the id of the crumb.
    """
    res = loaf_search(loaf, regex_str=crumb_id)
    archive(res)
    save(loaf)
    clear()
    crumb(res, "ARCHIVED")
    info(f"Archived {len(res)} crumbs.")

def _unarchive(loaf: object, crumb_id: str) -> None:
    """
    UNarchive a crumb from a loaf.

    :param loaf: The loaf being edited.
    :param crumb_id: the id of the crumb.
    """
    res = loaf_search(loaf, regex_str=crumb_id)
    unarchive(res)
    save(loaf)
    clear()
    crumb(res, "UN-ARCHIVED")
    info(f"Un-Archived {len(res)} crumbs.")

def _search(loaf: object, search_str: str) -> None:
    """
    Searches the loaf for a given query WITH regex!

    :param loaf: The loaf being edited.
    :param search_str: the query.
    """
    res = loaf_search(loaf, regex_str=search_str)
    clear()
    crumb(res, "SEARCH")

def _list(loaf: object, count: str = "") -> None:
    """
    Show data view.

    :param loaf: The loaf being edited.
    :param count: Count of crumbs to show.
    """
    try:
        #TODO Shou,d probably remove this branch
        count_int = int(count)
        res = loaf.breadcrumbs.tasks[(-1 * count):-1]
        crumb(res, f"{count_int} CRUMBS")
    except Exception as e:
        res = loaf_search(loaf, time_str="1d-~", archived=False)
        clear()
        crumb(res, "BEADCRUMB TRAIL")

def _debug(loaf: object) -> None:
    """
    Show data view.

    :param loaf: The loaf being edited.
    """
    clear()
    rule("DEBUG MODE")
    breakpoint()

def _undo(loaf: object) -> None:
    """
    Undo a save.

    :param loaf: The loaf being edited.
    """
    clear()
    rule("UNDO")
    undo(loaf)
    info("Undo successful...")
