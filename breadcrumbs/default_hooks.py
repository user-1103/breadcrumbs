"""
A module of default hooks.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

from pytodotxt import Task
from rich.table import Table
from re import search
from itertools import filterfalse
from breadcrumbs.display import clear, crumb, easy_lex, figure
import time

from breadcrumbs.utils import loaf_search, order_by_date

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
    _check_future_inline(loaf)


def _check_future_inline(loaf: object) -> None:
    """
    Checks to see if there are any tasks cast to now.
    """
    res = loaf_search(loaf, time_str="1d-~")
    def filter(x: Task) -> bool:
        tmp = x.attributes.get("FUTURE", None)
        if (tmp is None):
            return True
        else:
            return False
    res = list(filterfalse(filter, loaf.crumbs.tasks))
    order_by_date(res, "FUTURE")
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

def _check_future_list(loaf: object) -> None:
    """
    Prints future casted items as a list.
    """
    res = loaf_search(loaf, time_str="1d-~")
    def filter(x: Task) -> bool:
        tmp = x.attributes.get("FUTURE", None)
        if (tmp is None):
            return True
        else:
            return False
    res = list(filterfalse(filter, loaf.crumbs.tasks))
    order_by_date(res, "FUTURE")
    clear()
    crumb(res, f"FUTURE CASTS FOR {datetime.now().isoformat(timespec='minutes')}")
