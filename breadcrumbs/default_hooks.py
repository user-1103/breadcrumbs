"""
A module of default hooks.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Union

from pytodotxt import Task
from rich.align import Align
from rich.console import RenderableType
from rich.table import Table
from re import search
from itertools import filterfalse, pairwise

from rich.text import Text
from breadcrumbs.display import clear, crumb, easy_lex, err, figure, info
import time
import plotext as pt

from breadcrumbs.utils import loaf_search, order_by_date, task_to_make_date

# Tracks the money in an account
PAY: Dict[str, List[float]] = dict()

# How long to wait between figs
FUTURE_WAIT = (60 * 30)
# Stops the spaming of future figs
LAST_FUTURE = time.time() - FUTURE_WAIT
# Tracks the metrics
METRICS_CACHE = dict()
# Has metris run once
METRICS_FIRST_RUN = True

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

def _collect_metrics_cmd(loaf: 'Loaf') -> None:
    """
    Finds all metrics in the loaf that need to be printed inline and prints them.
    """
    _collect_metrics(loaf, True)

def _collect_metrics_inline(loaf: 'Loaf') -> None:
    """
    Finds all metrics in the loaf that need to be printed inline and prints them.
    """
    global METRICS_FIRST_RUN
    if (METRICS_FIRST_RUN):
        _collect_metrics(loaf, True, False)
        METRICS_FIRST_RUN = False
    else:
        _collect_metrics(loaf)

def _collect_metrics(loaf: 'Loaf', cmd: bool = False, do_print: bool = True) -> None:
    """
    Finds all metrics in the loaf that need to be printed inline and prints them.
    """
    print_data = list()
    if (cmd):
        METRICS_CACHE.clear()
    for c in loaf.config_data.get("metrics", list()):
        try:
            tmp = c[0](loaf, c[1])
        except Exception as e:
            err(e)
            continue
        if (tmp is None):
            continue
        else:
            print_data.extend(tmp)
    if (print_data and do_print):
        if (not cmd):
            figure(print_data)
        else:
            clear()
            figure(print_data, "METRICS")

def _span(loaf, tag: str) -> Union[List[RenderableType], None]:
    """
    Represents a metric that takes place a cross a span of time.
    """
    rec = loaf_search(loaf, time_str="1d-~",
                      regex_str=(tag + r':\w*'))
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
    time_spans = _get_time_spans(tmp)
    if (not time_spans):
        return None
    s1 = [x[0] for x in time_spans]
    if (len(s1) > 24):
        s1 = s1[:23]
    ret = list()
    ret.append(_print_time_table(time_spans))
    cat_data = [(x, ((z-y).seconds)/60) for x, y, z in time_spans]
    ret.append(_print_cat_ratio(cat_data, f"Breakdown of {tag}", "Minutes", "Category"))
    # ret.append(_print_span(s1))
    return ret

def _run_total(loaf, tag: str, time_limit: int = 40) -> Union[List[RenderableType], None]:
    """
    Represents a metric that is a running total.
    """
    rec = loaf_search(loaf,
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
    ret.append(_print_cat_ratio(cat_data, f"Heatmap of {tag} (All Time)", "Effect", "Source"))
    run_data = [(z, x) for x, y, z in tmp]
    ret.append(_print_running_total(run_data, time_limit, "Time", "Net Total",
                                    f"Net Change Over Time of {tag}"))
    return ret

def _total_table(loaf, tag: str, time_limit: str = "20d-~") -> Union[List[str], None]:
    """
    Represents a metric that is a total.
    """
    rec = loaf_search(loaf, time_str=time_limit,
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
    ret.append(_print_value_table(value_data, f"Record of {tag} over {time_limit}"))
    return(ret)

def _print_span(data: List[str], span: int = 24) -> str:
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
    return ("".join(ret))

def _print_time_table(data: List[Tuple[str, datetime, datetime]]) -> RenderableType:
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
    return t
    
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

def _print_cat_ratio(data: List[Tuple[str, float]],
                     title: str,
                     x_text: str,
                     y_text: str) -> RenderableType:
    """
    Takes a set of values and names to make a simple histogram.

    :param data: The sets.
    :param title: The name of the graph.
    """
    data_dict = dict()
    for name, value in data:
        tmp = data_dict.get(name, list())
        tmp.append(value)
        data_dict[name] = tmp
    data_dict = {k: sum(v) for k, v in data_dict.items()}
    pt.clf()
    pt.limit_size(True, True)
    pt.plot_size((pt.tw() // 2), (pt.th() // 3))
    pt.bar(data_dict.keys(), data_dict.values())
    t = Table(title=title)
    ret = Text.from_ansi(pt.build(), overflow="crop", no_wrap=True, justify="left")
    t.add_column(ret)
    t.add_row(f"Graph of {x_text} vs {y_text}")
    return t

def _print_running_total(data: List[Tuple[datetime, float]],
                         time_limit: int,
                         x_text: str, y_text: str,
                         title: str) -> RenderableType:
    """
    Takes a set of datetimes and generates a running total graph.

    :param data: The sets.
    :param x_text: The x label
    :param y_text: The y label
    :param title: The name of the graph.
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


def _print_value_table(data: List[Tuple[datetime, float]],
                       title: str) -> RenderableType:
    """
    Takes a set of datetimes and generates a per day table..

    :param data: The sets.
    :param title: The name of the graph.
    """
    days = dict()
    for d, v in data:
        tmp = days.get(d.date(), 0)
        days[d.date()] = (tmp + v)
    tmp_days = list(days.keys())
    tmp_days.sort()
    print_data = list()
    day_count = tmp_days[0]
    while (tmp_days):
        value = days.get(day_count, None)
        if (value is None):
            print_data.append((day_count.isoformat(), "∅"))
        else:
            print_data.append((day_count.isoformat(), str(value)))
            tmp_days.remove(day_count)
        day_count += timedelta(days=1)
    rows  = list()
    tmp = list()
    for i, v in enumerate(print_data):
        if ((not (i%7)) and (i != 0)):
            rows.append(tmp)
            tmp = list()
        tmp.append(f"{v[0]}\n{v[1]}")
    rows.append(tmp)
    t = Table(title=title, show_edge=False)
    for x in range(7):
        t.add_column(str(x), justify="center")
    for r in rows:
        t.add_row(Align(*r, vertical="middle"))
    return t


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
