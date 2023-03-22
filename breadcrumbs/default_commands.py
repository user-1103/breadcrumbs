"""
The default commands that are available.
"""
from datetime import datetime, timedelta
from time import time
from pytodotxt import TodoTxt, Task
from breadcrumbs.display import crumb, console, info, clear, figure
from breadcrumbs.default_hooks import _check_future
from re import search, I
from itertools import dropwhile, filterfalse
from rich.table import Table
from hashlib import md5

def _add(loaf: object, text: str) -> None:
    """
    Adds a crumb to the loaf.

    :param loaf: The loaf being edited.
    :param text: the text of the file in todo.txt format.
    """
    tmp = Task(text)
    time = datetime.now().date()
    tmp_time = time.time().isoformat("minutes")
    tmp.add_attribute("TIME", tmp_time.replace(":","-"))
    tmp.creation_date= time
    loaf.crumbs.add(tmp)
    loaf.crumbs.save(safe=True)
    crumb([tmp])

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
    _check_future(loaf)

def _help(loaf: object) -> None:
    """
    Print the available crumb commands.

    :param loaf: The loaf being edited.
    """
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
    tmp = \
        lambda x : ((not bool(search(crumb_id, str(x)))) or bool(x.is_completed))
    res = list(filterfalse(tmp, loaf.crumbs.tasks))
    crumb(res, "ARCHIVED")
    for c in res:
        c.is_completed = True
        c.completion_date = datetime.now()
    loaf.crumbs.save(safe=True)
    info(f"Archived {len(res)} crumbs.")

def _unarchive(loaf: object, crumb_id: str) -> None:
    """
    UNarchive a crumb from a loaf.

    :param loaf: The loaf being edited.
    :param crumb_id: the id of the crumb.
    """
    tmp = \
        lambda x : ((not bool(search(crumb_id, str(x)))) or (not bool(x.is_completed)))
    res = list(filterfalse(tmp, loaf.crumbs.tasks))
    crumb(res, "UN-ARCHIVED")
    for c in res:
        c.is_completed = False
        c.completion_date = None
    loaf.crumbs.save(safe=True)
    info(f"Un-Archived {len(res)} crumbs.")

def _search(loaf: object, search_str: str) -> None:
    """
    Searches (fuzzy, kinda) the loaf for a given query.

    :param loaf: The loaf being edited.
    :param search_str: the query.
    """
    _reg(loaf, f".*{search_str}.*")

def _reg(loaf: object, search_str: str) -> None:
    """
    Searches the loaf for a given query WITH regex!

    :param loaf: The loaf being edited.
    :param search_str: the query.
    """
    tmp = \
        lambda x : not bool(search(search_str, str(x), I))
    res = list(filterfalse(tmp, loaf.crumbs.tasks))
    crumb(res, "SEARCH")

def _list(loaf: object, count: str = "") -> None:
    """
    Show data view.

    :param loaf: The loaf being edited.
    :param count: Count of crumbs to show.
    """
    try:
        count_int = int(count)
        res = loaf.breadcrumbs.tasks[(-1 * count):-1]
        crumb(res, f"{count_int} CRUMBS")
    except Exception as e:
        def day_parse(x: Task) -> bool:
            tmp = x.creation_date
            if (tmp is None):
                tmp = datetime.now().date()
            ret = (tmp <= (datetime.now() - timedelta(days=1)).date())
            ret = (ret or bool(x.is_completed))
            return ret
        res = list(filterfalse(day_parse, loaf.crumbs.tasks))
        clear()
        crumb(res, "24hr OF CRUMBS")

def _debug(loaf: object) -> None:
    """
    Show data view.

    :param loaf: The loaf being edited.
    """
    breakpoint()
