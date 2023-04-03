"""
The default commands that are available.
"""
from datetime import datetime
from pytodotxt import Task
from breadcrumbs.display import crumb, info, clear, figure, rule
from itertools import filterfalse
from rich.table import Table
from breadcrumbs.utils import add_task, archive, loaf_search, save, unarchive, undo, order_by_date
from breadcrumbs.metrics import collect_metrics

def check_future_cmd(loaf: object) -> None:
    """
    (CMD) Prints future casted items as a list.
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

def collect_metrics_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Finds all metrics in the loaf that need to be printed and prints them.
    """
    collect_metrics(loaf, True)

def add_cmd(loaf: object, text: str) -> None:
    """
    (CMD) Adds a crumb to the loaf.

    :param text: the text of the file in todo.txt format.
    """
    add_task(loaf, text)
    save(loaf)
    res = loaf_search(loaf, time_str="1d-~", archived=False)
    clear()
    crumb(res, "BEADCRUMB TRAIL")

def nop_cmd(loaf: object) -> None:
    """
    (CMD) Do nothing.
    """
    info("Use ?help to list commands")
    

def help_cmd(loaf: object) -> None:
    """
    (CMD) Print the available crumb commands.
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

def archive_cmd(loaf: object, search_str: str) -> None:
    """
    (CMD) Archive a crumb from a loaf.

    :param search_str: the id of the crumb.
    """
    res = loaf_search(loaf, regex_str=search_str)
    archive(res)
    save(loaf)
    clear()
    crumb(res, "ARCHIVED")
    info(f"Archived {len(res)} crumbs.")

def unarchive_cmd(loaf: object, search_str: str) -> None:
    """
    (CMD) UNarchive a crumb from a loaf.

    :param search_str: the id of the crumb.
    """
    res = loaf_search(loaf, regex_str=search_str)
    unarchive(res)
    save(loaf)
    clear()
    crumb(res, "UN-ARCHIVED")
    info(f"Un-Archived {len(res)} crumbs.")

def search_cmd(loaf: object, search_str: str) -> None:
    """
    (CMD) Searches the loaf for a given query WITH regex!

    :param search_str: the query.
    """
    res = loaf_search(loaf, regex_str=search_str)
    clear()
    crumb(res, "SEARCH")

def list_cmd(loaf: object, count: str = "") -> None:
    """
    (CMD) Show crumb trail view.

    :param count: Count of crumbs to show, defaults to last 24hr.
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

def debug_cmd(loaf: object) -> None:
    """
    (CMD) Enter a dbg session.
    """
    clear()
    rule("DEBUG MODE")
    breakpoint()

def undo_cmd(loaf: object) -> None:
    """
    (CMD) Undo a save.
    """
    clear()
    rule("UNDO")
    undo(loaf)
    info("Undo successful...")
