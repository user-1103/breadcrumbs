"""
A module of default hooks.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

from pytodotxt import Task
from rich.table import Table
from re import search
from itertools import filterfalse
from breadcrumbs.display import easy_lex, figure
import time

# Tracks the money in an account
PAY: Dict[str, List[float]] = dict()

# How long to wait between figs
FUTURE_WAIT = (60 * 30)
# Stops the spaming of future figs
LAST_FUTURE = time.time() - FUTURE_WAIT

def _check_time(loaf: object) -> None:
    """
    Checks if the future should be scried.
    """
    global LAST_FUTURE
    if (time.time() < (LAST_FUTURE + FUTURE_WAIT)):
        return
    else:
        LAST_FUTURE = time.time()
    _check_future(loaf)

def _check_future(loaf: object) -> None:
    """
    Checks to see if there are any tasks cast to now.
    """
    def filter(x: Task) -> bool:
        tmp = x.attributes
        if (x.is_completed):
            return True
        if (tmp is None):
            return True
        date_txt = tmp.get("FUTURE", None)
        if (date_txt is None):
            return True
        date_txt = date_txt[0]
        tmp_date = date.fromisoformat(date_txt)
        if (date.today() >= tmp_date):
            return False
        else:
            return True
    def sort_method(x: Task) -> Tuple[int]:
        date_txt = x.attributes["FUTURE"][0]
        tmp = tuple(date_txt.split("-"))
        return tmp
    res = list(filterfalse(filter, loaf.crumbs.tasks))
    res.sort(key=sort_method)
    if (not res):
        return
    t = Table(title=f"Future Casts For {date.today().isoformat()}",
                     expand=True)
    t.add_column("Cast Date")
    t.add_column("Crumb Info")
    for x in res:
        date_txt = x.attributes["FUTURE"]
        des = x.description
        if (not des):
            des = "<empty>"
        t.add_row(date_txt[0], easy_lex(des))
    figure([t])


