"""
The default commands that are available.
"""
from datetime import datetime
from typing import Tuple, Union
from pytodotxt import Task
from breadcrumbs.display import crumb, debug, info, clear, figure, prompt, rule
from itertools import filterfalse
from rich.table import Table
from breadcrumbs.utils import add_task, archive, loaf_search, save, unarchive, undo, order_by_date, task_to_make_date
from breadcrumbs.metrics import collect_metrics
from json import loads

def check_future_now_cmd(loaf: object) -> None:
    """
    (CMD) Prints future casted items as a list for NOW.
    """
    check_future_cmd(loaf, date_str=datetime.now().isoformat())

def check_future_cmd(loaf: 'Loaf', date_str: str) -> None:
    """
    (CMD) Prints future casted items as a list for a given date.

    :param date_str: An iso date to check for casts.
    """
    max_time = datetime.fromisoformat(date_str)
    def filter(x: Task) -> bool:
        nonlocal max_time
        tmp = x.attributes.get("FUTURE", None)
        if (tmp is None):
            return True
        t_time = task_to_make_date(x, d_tag="FUTURE")
        if (t_time > max_time):
            return True
        return False
    res = loaf_search(loaf, archived=False)
    res = list(filterfalse(filter, res))
    order_by_date(res, "FUTURE")
    clear()
    crumb(res, f"FUTURE CASTS FOR {datetime.now().isoformat(' ', 'minutes')}")
    loaf.set_buffer(res)
    if (not res):
        info("No casts to now...")

def list_metrics_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Lists all known metrics.
    """
    tmp = loaf.config_data.get("metrics", list())
    t = Table(title="Programed Metrics")
    t.add_column("Tag")
    t.add_column("Type")
    for c in tmp:
        t.add_row(c[1], c[0].__name__)
    clear()
    figure([t], "METRICS LIST")

def list_buffer_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Prints the current buffer.
    """
    res = loaf.get_buffer()
    exp_time = datetime.fromtimestamp(loaf.buffer_time)
    clear()
    crumb(res, "BUFFER CONTENT")
    if (not res):
        info("Buffer is empty...")
    else:
        info(f"Buffer auto-expires at {exp_time}.")

def collect_all_metrics_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Finds all metrics in the loaf that need to be printed and prints them.
    """
    collect_metrics(loaf, None, None, True)

def collect_metrics_cmd(loaf: 'Loaf', opt: str) -> None:
    """
    (CMD) Finds all metrics in the loaf that need to be printed and prints them.

    :param tag: The metric tag to collect.
    :param opt_overide: An optional JSON of settings to pass to the
    metric collector.
    """
    try:
        tag, opt_overide = opt.split()
        opt_overide_dict = loads(opt_overide)
    except Exception as e:
        breakpoint()
        tag = opt
        opt_overide_dict = None
    collect_metrics(loaf, tag, opt_overide_dict, True)

def raw_add_cmd(loaf: 'Loaf', text: str) -> None:
    """
    (CMD) Adds a crumb to the loaf RAW, no additional info added.
    USE WITH CARE!

    :param text: the text of the file in todo.txt format.
    """
    tmp = Task(text)
    loaf.crumbs.add(tmp)
    save(loaf)
    res = loaf_search(loaf, time_str="1d-~", archived=False)
    clear()
    crumb(res, "BEADCRUMB TRAIL")
    loaf.set_buffer([res])

def add_cmd(loaf: 'Loaf', text: str) -> None:
    """
    (CMD) Adds a crumb to the loaf.

    :param text: the text of the file in todo.txt format.
    """
    add_task(loaf, text)
    save(loaf)
    res = loaf_search(loaf, time_str="1d-~", archived=False)
    clear()
    crumb(res, "BEADCRUMB TRAIL")
    loaf.set_buffer([res])

def block_cmd(loaf: 'Loaf', mod_str: str) -> None:
    """
    (CMD) Start / end a block edit. Crumbs entered in the block will be
    prefixed/postfixed With TEXTA/TEXTB as found in the mod_str.

    :param mod_str: A string of the form TEXTA/TEXTB or TEXTA.
    """
    try:
        prefix_str, postfix_str = mod_str.split("/")
    except Exception as e:
        prefix_str = ""
        postfix_str = mod_str
    clear()
    t = Table(title="Editing in block mode using:",
              caption="(Type END to finish block edit)")
    t.add_column("Prefix")
    t.add_column("Postfix")
    t.add_row(prefix_str, postfix_str)
    figure([t], "BLOCK EDIT")
    add_text = ""
    tmp = list()
    while (True):
        add_text = prompt()
        if (add_text == "END"):
            break
        tmp.append(add_task(loaf, f"{prefix_str} {add_text} {postfix_str}"))
        clear()
        figure([t], "BLOCK EDIT")
        crumb(tmp)
    clear()
    figure([t], "BLOCK EDIT")
    crumb(tmp)
    info("Saving Block")
    save(loaf)
    loaf.set_buffer(tmp)

def nop_cmd(loaf: object) -> None:
    """
    (CMD) Do nothing.
    """
    info("Use ?h to list commands")
    

def help_cmd(loaf: object) -> None:
    """
    (CMD) Print the available crumb commands.
    """
    clear()
    rule("HELP")
    t = Table(title="Crumb Commands.")
    t.add_column("Regex Of What You Type...")
    t.add_column("What Happens...")
    t.add_column("Command Or Macro?")
    for k, v in loaf.config_data["cmds"].items():
        t.add_row(k, v.__doc__, "Command")
    for k, v in loaf.config_data["macros"].items():
        t.add_row(k, v, "Macro")
    figure([t])

def archive_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Archive a crumbs in buffer from a loaf.
    """
    res = loaf.get_buffer()
    archive(res)
    save(loaf)
    clear()
    crumb(res, "ARCHIVED")
    info(f"Archived {len(res)} crumbs.")

def unarchive_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Un-Archive a crumbs in buffer from a loaf.
    """
    res = loaf.get_buffer()
    unarchive(res)
    save(loaf)
    clear()
    crumb(res, "UN-ARCHIVED")
    info(f"Un-Archived {len(res)} crumbs.")

def search_cmd(loaf: 'Loaf', search_str: str) -> None:
    """
    (CMD) Searches the loaf for a given query WITH regex!

    :param search_str: the query.
    """
    res = loaf_search(loaf, regex_str=search_str,
                      archived=False)
    loaf.set_buffer(res)
    clear()
    crumb(res, "SEARCH")

def search_archive_cmd(loaf: 'Loaf', search_str: str) -> None:
    """
    (CMD) Searches the loaf for a given query WITH regex WITH archive!

    :param search_str: the query.
    """
    res = loaf_search(loaf, regex_str=search_str)
    loaf.set_buffer(res)
    clear()
    crumb(res, "SEARCH (WITH ARCHIVE)")

def advanced_search_cmd(loaf: 'Loaf', search_str: str) -> None:
    """
    (CMD) Searches the loaf for a given query with search json!

    :param search_str: the query.
    """
    search_json = loads(search_str)
    debug("Advanced search with:")
    debug(search_json)
    res = loaf_search(loaf, **search_json)
    loaf.set_buffer(res)
    clear()
    crumb(res, "ADVANCED SEARCH")

def list_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Show crumb trail view for the past 24hr.
    """
    res = loaf_search(loaf, time_str="1d-~", archived=False)
    loaf.set_buffer(res)
    clear()
    crumb(res, "BEADCRUMB TRAIL")

def debug_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Enter a dbg session.
    """
    clear()
    rule("DEBUG MODE")
    breakpoint()

def undo_cmd(loaf: 'Loaf') -> None:
    """
    (CMD) Undo. As of right now this just arcives the last crumb.
    """
    tmp = loaf.crumbs.tasks[-1]
    tmp.is_completed = True
    save(loaf)
    list_cmd(loaf)
    info("Undo successful...")
