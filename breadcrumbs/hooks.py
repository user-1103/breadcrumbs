"""
A module of default hooks.
"""
from datetime import date
from typing import Dict, List
from pytodotxt import Task
from rich.table import Table
from itertools import filterfalse
from breadcrumbs.display import crumb, easy_lex, figure, debug
from breadcrumbs.loaf import LOAF, Loaf
import time
from breadcrumbs.utils import loaf_search, order_by_date
from enum import Enum, auto
from breadcrumbs.metrics import collect_metrics, METRICS_FIRST_RUN

# Tracks the money in an account
PAY: Dict[str, List[float]] = dict()

# How long to wait between figs
FUTURE_WAIT = (60 * 30)
# Stops the spaming of future figs
LAST_FUTURE = time.time() - FUTURE_WAIT

class HookTypes(Enum):
    """
    The types of hooks that can be hooked.
    """
    INIT = auto()
    EXIT = auto()
    PREMACRO = auto()
    PRE = auto()
    POST = auto()
    OK = auto()
    ERR = auto()

def call_hooks(hook: HookTypes) -> None:
    """
    Calls all hooks registered with a given name.

    :args hook: The type of the hook in it.
    """
    h = LOAF.config_data["hooks"].get(hook, None)
    if (not h):
        return
    debug(f"Calling internal hook {hook}.")
    for hook_call in h:
        debug(f"Calling {hook_call.__name__}")
        hook_call(LOAF)

def future_cast_hook(loaf: Loaf) -> None:
    """
    (HOOK) Checks if the future should be scried.
    """
    global LAST_FUTURE
    if (time.time() < (LAST_FUTURE + FUTURE_WAIT)):
        return
    else:
        LAST_FUTURE = time.time()
    check_future_inline(loaf)


def check_future_inline(loaf: object) -> None:
    """
    (INLINE) Checks to see if there are any tasks cast to now.
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

def collect_metrics_hook(loaf: 'Loaf') -> None:
    """
    (HOOK) Finds all metrics in the loaf that need to be printed and prints them.
    """
    global METRICS_FIRST_RUN
    if (METRICS_FIRST_RUN):
        collect_metrics(loaf, True, False)
        METRICS_FIRST_RUN = False
    else:
        collect_metrics(loaf)
