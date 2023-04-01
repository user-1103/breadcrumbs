"""
A module of default hooks.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Union

from pytodotxt import Task
from rich.table import Table
from re import search
from itertools import filterfalse, pairwise
from breadcrumbs.display import clear, crumb, easy_lex, figure, info
import time
import plotex as pt

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

def _print_span(data: List[str], span: int = 24) -> None:
    """
    Prints a span from data.

    :param data: The data to print.
    :param span: The length of span.
    """
    ret = list()
    for x in data:
        tmp = x[0].upper()
        ret.append(tmp)
    if (len(data) < span):
        tmp = "•" * (span - len(data))
        ret.extend(list(tmp))
    figure(["".join(ret)])

def _print_time_table(data: List[Tuple[str, datetime, datetime]]) -> None:
    """
    Prints a time table from data.

    :param data: The data to print.
    """
    a = data[0][1]
    b = data[-1][2]
    t = Table(title=f"Time Tracking: {a.isoformat(' ', 'minutes')} -"
              f" {b.isoformat(' ', 'minutes')}")
    t.add_column("Start")
    t.add_column("End")
    t.add_column("Task")
    t.add_column("Delta (m)")
    
    for task, start, end in data:
        delta = ((end - start).seconds) / 60
        s = start.isoformat(" ", "minutes")
        e = end.isoformat(" ", "minutes")
        t.add_row(s, e, task, str(delta))
    figure([t])
    
def _get_time_spans(data: List[Tuple[str, datetime]]) -> List[Tuple[str, datetime, datetime]]:
    """
    Generates span objects from raw data.

    :param data: The raw data.
    :return: Span tuples.
    """
    tmp = [x[1] for x in data]
    pairs = pairwise(tmp)
    names = [x[0] for x in data]
    names = names[:-1]
    ret = list()
    for name, p in zip(names, pairs):
        if ((name == "0") and (len(ret))):
                ret.pop()
        else:
            try:
                reset_time = datetime.fromisoformat(name)
                old = ret.pop()
                new = (old[0], old[1], reset_time)
                ret.append(new)
            except Exception as e:
                ret.append((name, *p))
    return ret

def _print_cat_ratio(data: List[Tuple[str, float]]) -> None:
    ...

def _print_running_total(data: List[Tuple[datetime, float]]) -> None:
    ...

def _print_value_table(data: List[Tuple[datetime, float]]) -> None:
    ...

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
    crumb(res, f"FUTURE CASTS FOR {datetime.now().isoformat(' ', 'minutes')}")
    if (not res):
        info("No casts to now...")
