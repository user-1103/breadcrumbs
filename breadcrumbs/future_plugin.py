"""
Defines future casting plugin for the breadcrumbs system.
"""
from datetime import date, datetime
from itertools import filterfalse
from typing import Dict, Any
from time import time

from pytodotxt import Task, TodoTxt
from rich.table import Table

from breadcrumbs.utils import easy_lex, loaf_search, order_by_date, set_buffer, task_to_make_date


def check_future(conf: Dict[str, Any], loaf: TodoTxt, date_str: str, cmd: bool = False) -> None:
    """
    Prints future casted items as a list for a given date.

    :param date_str: An iso date to check for casts.
    :param cmd: Wether to run as a command or a hook.
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
    span_text = max_time.isoformat(' ', 'minutes')
    if (cmd):
        order_by_date(res, "FUTURE")
        conf['log']['clear']()
        conf['log']['title'](f"FUTURE CASTS FOR {span_text}")
        for x in res:
            conf['log']['crumb'](x)
        set_buffer(conf, res)
        if (not res):
            conf['log']['info'](f"No casts to {span_text}...")
    else:
        last_future = conf['plugins']['future']['lib']['last_future']
        future_wait = conf['plugins']['future']['lib']['future_wait']
        if (time() < (last_future + future_wait)):
            return
        else:
            conf['plugins']['future']['lib']['last_future'] = time()
            t = Table(title=f"Future Casts For {span_text}")
            t.add_column("Cast Date")
            t.add_column("Crumb Info")
            if (not res):
                return
            for x in res:
                date_txt = x.attributes["FUTURE"]
                des = x.description
                if (not des):
                    des = "<empty>"
                t.add_row(date_txt[0], easy_lex(des))
            conf['log']['figure'](t)

def check_future_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <date_str> -> Optional. If provied, this date will be used instead of today.
    - Checks to see if there are any future casts to today.
    - Never saves. Sets selection buffer.
    """
    try:
        check_date = date.fromisoformat(args)
    except Exception as e:
        check_date = date.today()
    check_str = check_date.isoformat()
    check_future(conf, loaf, check_str, cmd=True)
    return False

def check_future_hook(conf: Dict[str, Any], loaf: TodoTxt) -> None:
    """
    Reminds the user every 30 minutes about items that have been future cast to
    now.
    """
    check_str = date.today().isoformat()
    check_future(conf, loaf, check_str)

def load_plugin() -> Dict[str, Any]:
    """
    This is a function that will do what it need to to load the 'plugin' and
    return a string keyed dictionary that will be merged with all other plugins
    to form the final running config.

    :return: The configuration of the plugin.
    """


    plugin_data = {
        "author": "USER 1103",
        "website": "https://github.com/user-1103/breadcrumbs",
        "version": "0.1",
        "description": "Adds future casting to crumbs.",
        "imports": [],
        "lib": {
            "last_future": 0.0,
            "future_wait": (60 * 30)
        },
        "help": {
            "usage": ("If you are reading this, you are already using this"
                      " plugin")
        }
    }

    hooks = {
        "INIT": [],
        "PREMACRO": [],
        "PRECMD": [],
        "CMDERR": [],
        "CMDOK": [check_future_hook],
        "POSTCMD": [],
        "EXIT": [],
        "SAFEEXIT": [],
        "FATALEXIT": [],
        "PRINTCRUMB": [],
        "PRINTFIGURE": [],
        "PRINTFIGURE": [],
    }

    commands = {
        "f": check_future_cmd
    }

    config = {
        'plugins': {"future": plugin_data},
        "hooks": hooks,
        'commands': commands,
    }

    return config




