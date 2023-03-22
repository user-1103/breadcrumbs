"""
A module of default hooks.
"""

from datetime import date
from typing import Dict, List

from pytodotxt import Task
from rich.table import Table
from breadcrumbs.loaf import Loaf
from re import search
from itertools import filterfalse
from breadcrumbs.display import figure

# Tracks the money in an account
PAY: Dict[str, List[float]] = dict()

def _check_future(loaf: Loaf) -> None:
    """
    Checks to see if there are any tasks cast to now.
    """
    def filter(x: Task) -> bool:
        tmp = x.attributes
        if (tmp is None):
            return True
        date_txt = tmp.get("FUTURE", None)[0]
        if (date_txt is None):
            return True
        tmp_date = date.fromisoformat(date_txt)
        if (date.today() >= tmp_date):
            return False
        else:
            return True
    res = list(filterfalse(filter, loaf.crumbs.tasks))
    t = Table(title=f"Future Casts For {date.today().isoformat()}")
    t.add_column("Cast Date", "Crumb")
    for x in res:
        t.add_row(x.get("FUTURE", None)[0], x.description)
    figure([t])


