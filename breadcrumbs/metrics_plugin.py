"""
Defines the metrics plugin for the breadcrumbs system.
"""

from json import loads
from typing import Union, List, Tuple, Any, Dict
from rich.align import Align
from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from breadcrumbs.utils import loaf_search, task_to_make_date
from re import search
from datetime import timedelta, datetime, date
import plotext as pt
from itertools import pairwise
from pytodotxt import TodoTxt

# Tracks the metrics
METRICS_CACHE = dict()
# Has metris run once
METRICS_FIRST_RUN = True
# Weeksdays as strings
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def span(loaf, tag: str, opt: Dict[str, Any]) -> Union[List[RenderableType], None]:
    """
    - <span> -> A span to collect the metric over.
    - Represents a metric that takes place a cross a span of time.
    - <tag>:<category> -> Marks that a new segment of time is being tracked
      under the <category> tag. If END or a date string, special procedures
      will be taken. (?h metrics/span).
    """
    span = opt.get("span", "1d-~")
    rec = loaf_search(loaf, span=span,
                      regex_str=(tag + r':\w*'), archived=False)
    tmp = list()
    for x in rec:
        m = search((tag + r':(\w*)'), x.description)
        if (m is None):
            continue
        tmp.append((m.groups()[0], task_to_make_date(x)))
    if (tmp == METRICS_CACHE.get(tag, list())):
        return None
    else:
        METRICS_CACHE[tag] = tmp
    time_spans = get_time_spans(tmp)
    if (not time_spans):
        return None
    ret = list()
    ret.append(make_time_table(time_spans))
    cat_data = [(x, ((z-y).seconds)/60) for x, y, z in time_spans]
    ret.append(make_cat_ratio(cat_data, f"Breakdown of {tag}", "Minutes", "Category"))
    return ret

def run_total(loaf, tag: str,
              opt: Dict[str, Any]) -> Union[List[RenderableType], None]:
    """
    - <time_limit> -> An int of how many days back to display.
    - Represents a metric that is a running total with catagories.
    - <tag>:<float>/<category>.
      - <float> -> The signed value to add to the total.
      - <category> -> A category to track the value in <float> to.
    """
    rec = loaf_search(loaf, archived=False,
                      regex_str=(tag + r':\w*'))
    tmp = list()
    for x in rec:
        m = search((tag + r':(\S*)/(\S*)'), x.description)
        if (m is None):
            continue
        tmp.append((float(m.groups()[0]), m.groups()[1], task_to_make_date(x)))
    if (tmp == METRICS_CACHE.get(tag, list())):
        return None
    else:
        METRICS_CACHE[tag] = tmp
    ret = list()
    cat_data = [(y, x) for x, y, z in tmp]
    ret.append(make_cat_ratio(cat_data, f"Heatmap of {tag} (All Time)", "Effect", "Source"))
    run_data = [(z, x) for x, y, z in tmp]
    time_limit = opt.get("time_limit", 40)
    ret.append(make_running_total(run_data, time_limit, "Time", "Net Total",
                                    f"Net Change Over Time of {tag}"))
    return ret


def total_table(loaf, tag: str, opt: Dict[str, Any]) -> Union[List[str], None]:
    """
    - <span> -> A span for which data in the table will be calculated for.
    - <good_is_low> -> True/false; If true, lower values will be colored.
      green. Otherwise higher values will be green.
    - <goal> -> A float; If this value is hit, a marker will be added.
    - <fail> -> A float; If this value is hit, a marker will be added.
    - <dont_do_streak> -> True/false; If true, don't calculate / mark streaks.
    - Represents a metric that is a total per day.
    - <tag>:<float> -> A value to record for that day. Multiple values in the
      day are summed.
    """
    span = opt.get("span", "40d-~")
    rec = loaf_search(loaf, span=span, archived=False,
                      regex_str=(tag + r':\w*'))
    tmp = list()
    for x in rec:
        m = search((tag + r':(\S*)'), x.description)
        if (m is None):
            continue
        tmp.append((float(m.groups()[0]), task_to_make_date(x)))
    if (tmp == METRICS_CACHE.get(tag, list())):
        return None
    else:
        METRICS_CACHE[tag] = tmp
    ret = list()
    value_data = [(y, x) for x, y in tmp]
    ret.append(make_value_table(value_data, f"Record of {tag} over {span}", opt))
    return(ret)

def make_time_table(data: List[Tuple[str, datetime, datetime]]) -> RenderableType:
    """
    Makes a time table from data.

    :param data: The data to print.
    :retrun: The printable.
    """
    a = data[0][1]
    b = data[-1][2]
    t = Table(title=f"Time Spans: {a.isoformat(' ', 'minutes')} -"
              f" {b.isoformat(' ', 'minutes')}")
    t.add_column("Start")
    t.add_column("End")
    t.add_column("Task")
    t.add_column("Delta (m)")
    t.add_column("Delta (h)")
    for task, start, end in data:
        delta = ((end - start).seconds) / 60
        h_delta = delta / 60
        s = start.isoformat(" ", "minutes")
        e = end.isoformat(" ", "minutes")
        t.add_row(s, e, task, str(delta), str(h_delta))
    return t

def get_time_spans(data: List[Tuple[str, datetime]]) -> List[Tuple[str, datetime, datetime]]:
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
        if ((name == "END") and (len(ret))):
                ret.pop()
        else:
            try:
                year, month, day, hour, minutes = name.split("-")
                reset_time = datetime(year=int(year), month=int(month),
                                      day=int(day), hour=int(hour), minute=int(minutes))
                old = ret.pop()
                new = (old[0], old[1], reset_time)
                ret.append(new)
            except Exception as e:
                ret.append((name, *p))
    return ret

def make_cat_ratio(data: List[Tuple[str, float]],
                     title: str,
                     x_text: str,
                     y_text: str) -> RenderableType:
    """
    Takes a set of values and names to make a simple histogram.

    :param data: The sets.
    :param title: The name of the graph.
    :param x_text: The x label
    :param y_text: The y label
    :retrun: The printable.
    """
    data_dict = dict()
    for name, value in data:
        tmp = data_dict.get(name, list())
        tmp.append(value)
        data_dict[name] = tmp
    data_dict = {k: sum(v) for k, v in data_dict.items()}
    data_tup = list(data_dict.items())
    data_tup.sort(key= lambda x: x[1])
    keys = [x[0] for x in data_tup]
    values = [x[1] for x in data_tup]
    pt.clf()
    pt.limit_size(True, True)
    pt.plot_size((pt.tw() // 2), (pt.th() // 3))
    pt.grid(True, False)
    pt.bar(keys, values, orientation="horizontal")
    t = Table(title=title)
    ret = Text.from_ansi(pt.build(), overflow="crop", no_wrap=True, justify="left")
    t.add_column(ret)
    t.add_row(f"Graph of {x_text} vs {y_text}")
    return t

def make_running_total(data: List[Tuple[datetime, float]],
                         time_limit: int,
                         x_text: str, y_text: str,
                         title: str) -> RenderableType:
    """
    Takes a set of datetimes and generates a running total graph.

    :param data: The sets.
    :param x_text: The x label
    :param y_text: The y label
    :param title: The name of the graph.
    :retrun: The printable.
    """
    times = list()
    values = list()
    lower_limit = datetime.now() - (timedelta(days=time_limit))
    running_total = 0
    for t, delta in data:
        running_total += delta
        if (t >= lower_limit):
            times.append(pt.datetime_to_string(t))
            values.append(running_total)
    pt.clf()
    pt.limit_size(True, True)
    pt.plot_size((pt.tw() // 2), (pt.th() // 3))
    pt.plot(times, values)
    t = Table(title=title)
    ret = Text.from_ansi(pt.build(), overflow="crop", no_wrap=True, justify="left")
    t.add_column(ret)
    t.add_row(f"Graph of {x_text} vs {y_text}")
    return t


def make_value_table(data: List[Tuple[datetime, float]],
                       title: str, opt: Dict[str, Any]) -> RenderableType:
    """
    Takes a set of datetimes and generates a per day table..

    :param data: The sets.
    :param title: The name of the graph.
    :retrun: The printable.
    """
    days = dict()
    for d, v in data:
        tmp = days.get(d.date(), 0)
        days[d.date()] = (tmp + v)
    comp_type = opt.get("good_is_low", False)
    if (comp_type):
        hi_color = ("[red]", "[/red]")
        low_color = ("[green]", "[/green]")
    else:
        low_color = ("[red]", "[/red]")
        hi_color = ("[green]", "[/green]")
    midpoint = sum(days.values()) // 2
    tmp_days = list(days.keys())
    tmp_days.sort()
    print_data = list()
    while (tmp_days[0].weekday() != 0):
        past_day = (tmp_days[0] - timedelta(days=1))
        tmp_days = [past_day, *tmp_days]
    day_count = tmp_days[0]
    day_start = tmp_days[0]
    while (tmp_days):
        value = days.get(day_count, None)
        if (value is None):
            print_data.append((day_count.isoformat(), "∅"))
        else:
            print_data.append((day_count.isoformat(), str(value)))
        try:
            tmp_days.remove(day_count)
        except Exception as e:
            # Porbs not the most elegent way to do this
            ...
        day_count += timedelta(days=1)
    rows  = list()
    tmp = list()
    streak = 0
    for i, v in enumerate(print_data):
        if ((not (i%7)) and (i != 0)):
            rows.append(tmp)
            tmp = list()
        try:
            comp = float(v[1])
        except Exception as e:
            comp = None
        if (comp is not None):
            marks = "\n"
            goal = opt.get("goal", None)
            if (v[0] == date.today().isoformat()):
                marks += ":ten-thirty: "
            if (goal is not None):
                if (int(goal) == int(comp)):
                    marks += ":white_check_mark: "
                    streak += 1
                else:
                    streak = 0
            fail = opt.get("fail", None)
            if (fail is not None):
                if (int(fail) == int(comp)):
                    marks += ":white_exclamation_mark: "
            dont_do_streek = opt.get("dont_do_streak", False)
            if (not dont_do_streek):
                if (streak >= 3):
                    marks += ":fast_forward: "
            if (marks[-1] == " "):
                marks = marks[:-1]
            if (comp >= midpoint):
                tmp.append(f"{v[0][5:]}\n{hi_color[0]}{v[1]}{hi_color[1]}{marks}")
            else:
                tmp.append(f"{v[0][5:]}\n{low_color[0]}{v[1]}{low_color[1]}{marks}")
        else:
            tmp.append(f"{v[0][5:]}\n{v[1]}\n ")
    rows.append(tmp)
    t = Table(title=title, show_edge=False)
    # t.add_column("🡣 ISO Week Number / Day 🡢 ")
    for x in range(7):
        day_delta = (timedelta(days=x) + day_start).weekday()
        t.add_column(WEEKDAYS[day_delta], justify="center", overflow="fold")
    for i, r in enumerate(rows):
        day_delta = (timedelta(weeks=i) + day_start).isocalendar()[1]
        text_list = [Text.from_markup(x, justify="left",
                                      overflow="crop") for x in r]
        t.add_row(*text_list)
    return t

def metrics_info_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - Takes no args.
    - List available metrics.
    - Never saves.
    """
    tmp = conf['plugins']['metrics']['lib']['metrics']
    t = Table(title="Programed Metrics")
    t.add_column("Tag")
    t.add_column("Type")
    for c in tmp:
        t.add_row(c[1], c[0].__name__)
    conf['log']['clear']()
    conf['log']['title']('METRICS INFO')
    conf['log']['figure'](t)
    return False

def collect_metrics_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <tag>/<option_json>.
      - <tag> -> Optional. If provided, only collect metrics for given tag.
      - <option_json> -> Optional but requires <tag>. If provided, overide metric options
      with the provided json. (?h metrics/option-json).
    - Collects available metrics.
    - Never saves.
    """
    if (args):
        try:
            tag, option_json = args.split("/")
            option_dict = loads(option_json)
        except Exception as e:
            tag = args
            option_dict = None
        collect_metrics(conf, loaf, tag, option_dict, cmd=True)
    else:
        collect_metrics(conf, loaf, cmd=True)
    return False

def check_metrics_hook(conf: Dict[str, Any], loaf: TodoTxt) -> None:
    """
    Informs the user about updated metrics.
    """
    global METRICS_FIRST_RUN
    if (METRICS_FIRST_RUN):
        collect_metrics(conf, loaf, cmd=False, do_print=False)
        METRICS_FIRST_RUN = False
    else:
        collect_metrics(conf, loaf, cmd=False)

def collect_metrics(conf: Dict[str, Any], loaf: TodoTxt, tag: Union[None, str] = None,
                    opt_overide: Union[Dict[str, Any], None] =  None,
                    cmd: bool = False, do_print: bool = True) -> None:
    """
    Finds all metrics in the loaf that need to be printed inline and prints them.

    :param conf: The final conf to process.
    :param loaf: The loaf to process.
    :param tag: If given, only process a specific metric.
    :param opt_overide: If given with a tag, overides the opt dictionary for a
    metric.
    :param cmd: Clear cache and print as a command.
    :param do_print: Print or just render.
    """
    print_data = list()
    tmp = conf['plugins']['metrics']['lib']['metrics']
    if (tag is not None):
        tmp = [x for x in tmp if (tag == x[1])]
    for c in tmp:
        if (cmd):
            METRICS_CACHE[c[1]] = list()
        try:
            if (cmd or c[3]):
                if ((opt_overide is not None) and (tag is not None)):
                    tmp_print = c[0](loaf, c[1], opt_overide | c[2])
                else:
                    tmp_print = c[0](loaf, c[1], c[2])
            else:
                continue
        except Exception as e:
            conf['log']['err']("Could not collect metric", e)
            continue
        if (tmp_print is None):
            continue
        else:
            print_data.extend(tmp_print)
    if (print_data and do_print):
        if (not cmd):
            for x in print_data:
                conf['log']['figure'](x)
        else:
            conf['log']['clear']()
            conf['log']['title']('METRICS')
            for x in print_data:
                conf['log']['figure'](x)

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
        "description": "Adds metrics and graphs.",
        "imports": [],
        "lib": {
            'metrics': [
            ]
        },
        "help": {
            "usage": ("If you are reading this, you are already using this"
                      " plugin")
        }
    }

    hooks = {
        "INIT": [check_metrics_hook],
        "PREMACRO": [],
        "PRECMD": [],
        "CMDERR": [],
        "CMDOK": [check_metrics_hook],
        "POSTCMD": [],
        "EXIT": [],
        "SAFEEXIT": [],
        "FATALEXIT": [],
        "PRINTCRUMB": [],
        "PRINTFIGURE": [],
        "PRINTFIGURE": [],
    }

    commands = {
        "m": collect_metrics_cmd,
        "im": metrics_info_cmd
    }

    config = {
        'plugins': {"metrics": plugin_data},
        "hooks": hooks,
        'commands': commands,
    }

    return config




