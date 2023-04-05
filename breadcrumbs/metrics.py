"""
Stuff for collecting metrics.
"""
from typing import Union, List, Tuple, Any, Dict
from rich.align import Align
from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from breadcrumbs.display import err, clear, figure
from breadcrumbs.utils import loaf_search, task_to_make_date
from re import search
from datetime import timedelta, datetime
import plotext as pt
from itertools import pairwise

# Tracks the metrics
METRICS_CACHE = dict()
# Has metris run once
METRICS_FIRST_RUN = True
# Weeksdays as strings
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def span(loaf, tag: str, opt: Dict[str, Any]) -> Union[List[RenderableType], None]:
    """
    (METIRC) Represents a metric that takes place a cross a span of time.

    'time_str': time_str; A time string for which the span will be calculated for.
    """
    time_str = opt.get("time_str", "1d-~")
    rec = loaf_search(loaf, time_str=time_str,
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
    (METRIC) Represents a metric that is a running total.

    'time_limit': int; How many days back to display.
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
    (METRIC) Represents a metric that is a total.

    'time_str': time_str; A time string for which the table will be calculated for.
    'good_is_low': true/false; If true, lower values will be colored
    green. Otherwise higher values will be green.
    'goal': float; If this value is hit, a marker will be added.
    'fail': float; If this value is hit, a marker will be added.
    'dont_do_streak': true/false; If true, don't calculate / mark streaks.
    """
    time_str = opt.get("time_str", "40d-~")
    rec = loaf_search(loaf, time_str=time_str, archived=False,
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
    ret.append(make_value_table(value_data, f"Record of {tag} over {time_str}", opt))
    return(ret)

def make_span(data: List[str], span: int = 24) -> str:
    """
    Makes a  printable span from data.

    :param data: The data to print.
    :param span: The length of span.
    :retrun: The printable.
    """
    ret = list()
    for x in data:
        tmp = x[0].upper()
        ret.append(tmp)
    if (len(data) < span):
        tmp = "•" * (span - len(data))
        ret.extend(list(tmp))
    return ("".join(ret))

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
    pt.bar(keys, values)
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
    t.add_column("🡣 ISO Week Number / Day 🡢 ")
    for x in range(7):
        day_delta = (timedelta(days=x) + day_start).weekday()
        t.add_column(WEEKDAYS[day_delta], justify="center")
    for i, r in enumerate(rows):
        day_delta = (timedelta(weeks=i) + day_start).isocalendar()[1]
        t.add_row(*[str(day_delta), *[Align(x, vertical="middle") for x in r]])
    return t

def collect_metrics(loaf: 'Loaf', tag: Union[None, str] = None,
                    opt_overide: Union[Dict[str, Any], None] =  None,
                    cmd: bool = False, do_print: bool = True) -> None:
    """
    Finds all metrics in the loaf that need to be printed inline and prints them.

    :param loaf: The loaf to process.
    :param tag: If given, only process a specific metric.
    :param opt_overide: If given with a tag, overides the opt dictionary for a
    metric.
    :param cmd: Clear cache and print as a command.
    :param do_print: Print or just render.
    """
    print_data = list()
    tmp = loaf.config_data.get("metrics", list())
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
            err(e)
            continue
        if (tmp_print is None):
            continue
        else:
            print_data.extend(tmp_print)
    if (print_data and do_print):
        if (not cmd):
            figure(print_data)
        else:
            clear()
            figure(print_data, "METRICS")

