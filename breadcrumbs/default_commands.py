"""
The default commands that are available.
"""
from datetime import datetime, timedelta
from breadcrumbs.loaf import Loaf
from pytodotxt import TodoTxt, Task
from breadcrumbs.display import crumb
from re import search, I
from itertools import filterfalse

def _add(loaf: Loaf, text: str) -> None:
    """
    Adds a crumb to the loaf.

    :param loaf: The loaf being edited.
    :param text: the text of the file in todo.txt format.
    """
    tmp = Task(text)
    loaf.crumbs.add(tmp)
    loaf.crumbs.save(safe=True)
    crumb(tmp)

def _archive(loaf: Loaf, crumb_id: str) -> None:
    """
    Archive a crumb from a loaf.

    :param loaf: The loaf being edited.
    :param crumb_id: the id of the crumb.
    """
    tmp = \
        lambda x : search(".*{search_str}.*", str(x))
    res = list(filterfalse(tmp, loaf.crumbs.tasks))
    crumb(res, "DELETE")
    for crumb in res:
        crumb.is_completed = True
        crumb.completion_date = datetime.now()
    loaf.crumbs.save(safe=True)

def _search(loaf: Loaf, search_str: str) -> None:
    """
    Searches (fuzzy, kinda) the loaf for a given query.

    :param loaf: The loaf being edited.
    :param search_str: the query.
    """
    _reg(loaf, f".*{search_str}.*")


def _reg(loaf: Loaf, search_str: str) -> None:
    """
    Searches the loaf for a given query WITH regex!

    :param loaf: The loaf being edited.
    :param search_str: the query.
    """
    tmp = \
        lambda x : search("{search_str}", str(x), I)
    res = list(filterfalse(tmp, loaf.crumbs.tasks))
    crumb(res, "SEARCH")

def _list(loaf: Loaf, count: str = "") -> None:
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
        tmp = \
            lambda x : (x.creation_date >= (datetime.now() - timedelta(days=1)))
        res = list(filterfalse(tmp, loaf.crumbs.tasks))
        crumb(res, "24hr OF CRUMBS")

