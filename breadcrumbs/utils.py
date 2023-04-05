"""
Module of common utilities for doing stuff.
"""

from datetime import date, datetime, time, timedelta
from itertools import filterfalse
from pathlib import Path
from re import search
from typing import List, Union, Tuple
from copy import deepcopy
from pytodotxt import Task
from breadcrumbs.display import debug

def time_str_to_delta(ts: str) -> timedelta:
    """
    Takes a time string and returns an equivalent time delta.

    :param ts: A sting of the form <int><m,h,d,w,y>
    :return: A time delta.
    """
    try:
        indicator = ts[-1].lower()
        value = float(ts[:-1])
    except Exception as e:
        raise Exception("Format not met <int><m,h,d,w,y>")
    if (indicator == "m"):
        tmp = {"minutes": value}
    elif (indicator == "h"):
        tmp = {"hours": value}
    elif (indicator == "w"):
        tmp = {"weeks": value}
    elif (indicator == "y"):
        tmp = {"days": value * 365}
    else:
        tmp = {"days": value}
    t = timedelta(**tmp)
    return t

def task_to_make_date(t: Task, d_tag: Union[None, str] = None,
                      t_tag: str = "TIME") -> datetime:
    """
    Creates a datetime from a non archived crumb, from a  given set of tags.

    :param t: the task to process.
    :param d_tag: The tag of the day component. If none, use make time.
    :param t_tag: The tag of the time component.
    :retrun: a new datetime object.
    """
    T = t.attributes.get(t_tag, [None])[0]
    if (T is None):
        T = "01-01"
    if (d_tag is None):
        D = t.creation_date
    else:
        D = t.attributes.get(d_tag, [None])[0]
    if (D is None):
        D = datetime.fromisoformat("1970-01-01")
    if (isinstance(D, str)):
        D = date.fromisoformat(D)
    h, m = T.split("-")
    ret = datetime.combine(D, time(hour=int(h), minute=int(m)))
    return ret

def task_to_archive_date(t: Task, d_tag: Union[None, str] = None,
                      t_tag: str = "ATIME") -> datetime:
    """
    Creates a datetime from an archived crumb, from a  given set of tags.

    :param t: the task to process.
    :param d_tag: The tag of the day component. If none, use make time.
    :param t_tag: The tag of the time component.
    :retrun: a new datetime object.
    """
    T = t.attributes.get(t_tag, [None])[0]
    if (T is None):
        T = "01-01"
    D = t.completion_date
    if (d_tag is None):
        D = t.creation_date
    else:
        D = t.attributes.get(d_tag, [None])[0]
    if (D is None):
        D = datetime.fromisoformat("1970-01-01")
    if (isinstance(D, str)):
        D = date.fromisoformat(D)
    h, m = T.split("-")
    ret = datetime.combine(D, time(hour=int(h), minute=int(m)))
    return ret

def parse_date_range(dr: str) -> Tuple[datetime, datetime]:
    """
    Takes a span of date specification.

    :param dr: A sting of A string of the format TIMEDATE-TIMEDATE where TIMEDATE
    can be ~ to indicate an open interval, or an int followed by m,h,d,w,y to
    specify minutes, hours, days, weeks, and years.
    :return: A tuple of the start date and end date of the span.
    """
    before, after = dr.split("-")
    if (before == "~"):
        before_t = datetime(1970, 1, 1)
    else:
        try:
            before_d = time_str_to_delta(before)
            before_t = datetime.now() - before_d
        except Exception as E:
            raise Exception("Invalid range.")
    if (after == "~"):
        after_t = datetime.now()
    else:
        try:
            after_d = time_str_to_delta(after)
            after_t = datetime.now() - after_d
        except Exception as E:
            raise Exception("Invalid range.")
    return (before_t, after_t)

def order_by_date(task_list: List[Task],
                  key: Union[str, None] = None) -> None:
    """
    Order a task list by date.

    :param task_list: The list to sort.
    :param key: An optional key, that when provided will be used as the source
    of the date. Otherwise the date used is the creation_date.
    """
    def sort_method(x: Task) -> Union[Tuple[int, int, int], Tuple[int, int, int, int, int]]:
        if (key is None):
            date_txt = task_to_make_date(x).timetuple()
            tmp = tuple(date_txt)
            return tmp
        else:
            date_txt = x.attributes.get(key, ["1970-01-01"])[0]
            tmp = tuple(date_txt.split("-"))
            tmp_2 = (int(tmp[0]), int(tmp[1]), int(tmp[2]))
            return tmp_2
    task_list.sort(key=sort_method)


def loaf_search(loaf: 'Loaf',
                regex_str: Union[str,None] = None,
                raw_text: bool = False,
                archived: Union[bool, None] = None,
                priority: Union[str, None] = None,
                time_str: Union[str, None] = None,
                archived_time_str: Union[str, None] = None) -> List[Task]:
    """
    Searches the provided loaf for a given set of paramters and returns a list
    of Task objects. If a parameter is set to None it will not be considered.
    If no paramters are set an empty list will be returned.

    :param loaf: The loaf to search through.
    :param regex_str: A py-regex string to search the raw text with.
    :param raw_text: If true, search the entire text of the object, otherwise
    just search the text with no priority, archive indicator, or create /
    archive dates.
    :param archive: Is the task arrived?
    :param priority: A-Z priority char, "" for no priority.
    :param time_str: A string of the format TIMEDATE-TIMEDATE where TIMEDATE
    can be ~ to indicate an open interval, or an int followed by m,h,d,w,y to
    specify minutes, hours, days, weeks, and years. This is used to filter the
    creation_date.
    :param archived_time_str: Same as the time_str, but filters the archive date.
    NOTE The m and h marks are meaningless for this field.
    :return: A list of matching tasks.
    """
    def filter_regex(x: Task) -> bool:
        # TODO could use a speedup with caching here
        nonlocal regex_str, raw_text
        if (raw_text):
            tex = str(x)
        else:
            tex = x.description
        if (tex is None):
            debug("No Description")
            debug(x)
            return True
        reg = search(regex_str, tex)
        if (reg is None):
            return True
        else:
            return False

    def filter_archive(x: Task) -> bool:
        nonlocal archived
        ret = not (archived == x.is_completed)
        return ret

    def filter_priority(x: Task) -> bool:
        nonlocal priority
        if (priority == ""):
            priority = None
        else:
            priority = priority.upper()
        ret = not (priority == x.priority)
        return ret

    def filter_time_str(x: Task) -> bool:
        nonlocal time_str
        before_t, after_t = parse_date_range(time_str)
        task_time = task_to_make_date(x)
        now = datetime.now()
        if ((before_t <= task_time) and (task_time <= after_t)):
            ret = False
        else:
            ret = True
        return ret

    def filter_archive_time_str(x: Task) -> bool:
        nonlocal archived_time_str
        before_t, after_t = parse_date_range(archived_time_str)
        task_time = task_to_archive_date(x)
        now = datetime.now()
        if ((before_t <= task_time) and (task_time <= after_t)):
            ret = False
        else:
            ret = True
        return ret

    res = list(loaf.crumbs.tasks)
    if (archived is not None):
        res = list(filterfalse(filter_archive, res))
    if (priority is not None):
        res = list(filterfalse(filter_priority, res))
    if (time_str is not None):
        res = list(filterfalse(filter_time_str, res))
    if (archived_time_str is not None):
        res = list(filterfalse(filter_archive_time_str, res))
    if (regex_str is not None):
        res = list(filterfalse(filter_regex, res))
    debug("Post Filter")
    debug(res)
    return res

def archive(task_list: List[Task]) -> None:
    """
    Takes a list of tasks and archives in the proper way.

    :param task_list: A list of tasks to archive.
    """
    for task in task_list:
        dt = datetime.now().time().isoformat("minutes")
        dt.replace(":", "-")
        task.add_attribute("ATIME", dt)
        task.is_completed = True

def unarchive(task_list: List[Task]) -> None:
    """
    Takes a list of tasks and de-archives in the proper way.

    :param task_list: A list of tasks to de-archive.
    """
    for task in task_list:
        task.remove_attribute("ATIME")
        task.is_completed = False

def add_task(loaf: 'Loaf', task: str) -> Task:
    """
    Adds a task in the right way!.

    :param loaf: The loaf to add to.
    :param task: The TodoTxt task text.
    :return: The newly created crumb.
    """
    dt = datetime.now().time().isoformat("minutes")
    dt = dt.replace(":", "-")
    tmp = Task(task)
    if (tmp.attributes):
        is_time = tmp.attributes.get("TIME", [dt])[0]
    else:
        is_time = dt
    tmp.add_attribute("TIME", is_time)
    if (tmp.creation_date is None):
        tmp.creation_date = datetime.now()
    loaf.crumbs.add(tmp)
    return tmp

def save(loaf: 'Loaf') -> None:
    """
    Saves the loaf in an undooable way.

    :param loaf: the loaf to save.
    """
    order_by_date(loaf.crumbs.tasks)
    loaf.crumbs.save(safe=True)

def undo(loaf: 'Loaf') -> None:
    """
    Undo the last save action.

    :param loaf: the loaf to save.
    """
    # TODO a more comprehensive undo / backup
    ...
