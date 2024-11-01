import datetime
import workalendar.europe
from workalendar.core import Calendar
from typing import List
import pytimeparse

def is_working_hour(hour: int, work_day_hours: List[List[int]] = [[9, 12], [13, 17]]) -> bool:
    """
    Check if the hour is a working hour.
    """
    for interval in work_day_hours:
        if hour >= interval[0] and hour < interval[1]:
            return True
    return False

def get_next_work_hour(current_date: datetime.datetime, work_day_hours: List[List[int]] = [[9, 12], [13, 17]], calendar: Calendar = workalendar.europe.France()) -> datetime.datetime:
    """
    Get the next work hour based on the current date.
    France Calendar is used to check if the day is a working day.
    """
    while True:
        if calendar.is_working_day(current_date):
            for interval in work_day_hours:
                if current_date.hour < interval[0]:
                    return current_date.replace(hour=interval[0], minute=0, second=0, microsecond=0)
                elif current_date.hour < interval[1]:
                    return current_date
                elif current_date.hour >= interval[1]:
                    continue
                else:
                    current_date = current_date.replace(hour=interval[1], minute=0, second=0, microsecond=0)
        current_date += datetime.timedelta(days=1)
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)

def count_work_hours(start_date: datetime.datetime, end_date: datetime.datetime, work_day_hours: List[List[int]] = [[9, 12], [13, 17]], calendar: Calendar = workalendar.europe.France()) -> float:
    """
    Count the number of work hours between the start date and the end date.
    France Calendar is used to check if the day is a working day.
    """
    # copy start_date using timestamp
    current_date = datetime.datetime.fromtimestamp(start_date.timestamp(), datetime.timezone.utc)
    work_hours = 0
    while current_date < end_date:
        if calendar.is_working_day(current_date):
            for interval in work_day_hours:
                interval_start = current_date.replace(hour=interval[0], minute=0, second=0, microsecond=0)
                interval_end = current_date.replace(hour=interval[1], minute=0, second=0, microsecond=0)
                if interval_end <= current_date:
                    continue
                if interval_start >= end_date:
                    break
                if current_date <= interval_start:
                    work_start = interval_start
                else:
                    work_start = current_date
                work_end = interval_end
                if end_date < work_end:
                    work_end = end_date
                work_duration = (work_end - work_start).total_seconds() / 3600
                if work_duration < 0:
                    print("  start_date: {} end_date: {}".format(start_date, end_date))
                    print("  Negative work duration: current_date: {} i_start: {} i_end: {} duration: {}".format(current_date, interval_start, interval_end, work_duration))
                    print("  work_start: {} work_end: {}".format(work_start, work_end))
                    raise Exception("Negative work duration")

                work_hours += work_duration
                current_date = work_end
        current_date += datetime.timedelta(days=1)
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return work_hours

def get_due_date(start_date: datetime.datetime, duration: int|float, work_day_hours: List[List[int]] = [[9, 12], [13, 17]], calendar: Calendar = workalendar.europe.France()) -> datetime.datetime:
    """
    Calculate the due date based on the start date and the duration.
    France Calendar is used to check if the day is a working day.
    The duration is in hours.
    """
    # print(f"get_due_date: start_date: {start_date} duration: {duration}")
    # current_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
    # Copy start_date
    current_date = datetime.datetime.fromtimestamp(start_date.timestamp(), datetime.timezone.utc)

    hours_remaining = duration
    while hours_remaining > 0:
        if calendar.is_working_day(current_date):
            for interval in work_day_hours:
                interval_start = current_date.replace(hour=interval[0], minute=0, second=0, microsecond=0)
                interval_end = current_date.replace(hour=interval[1], minute=0, second=0, microsecond=0)
                if current_date <= interval_start:
                    work_start = interval_start
                else:
                    work_start = current_date
                work_end = interval_end
                work_duration = (work_end - work_start).total_seconds() / 3600
                if work_duration > 0:
                    if hours_remaining <= work_duration:
                        due_date = work_start + datetime.timedelta(hours=hours_remaining)
                        return due_date
                    else:
                        hours_remaining -= work_duration
                        current_date = work_end
        current_date += datetime.timedelta(days=1)
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return current_date

def topological_sort(source):
    """perform topo sort on elements.

    :arg source: list of ``(name, [list of dependancies])`` pairs
    :returns: list of names, with dependancies listed first
    """
    pending = [(name, set(deps)) for name, deps in source] # copy deps so we can modify set in-place
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            name, deps = entry
            deps.difference_update(emitted) # remove deps we emitted last pass
            if deps: # still has deps? recheck during next pass
                next_pending.append(entry)
            else: # no more deps? time to emit
                yield name
                emitted.append(name) # <-- not required, but helps preserve original ordering
                next_emitted.append(name) # remember what we emitted for difference_update() in next pass
        if not next_emitted: # all entries have unmet deps, one of two things is wrong...
            raise ValueError("cyclic or missing dependancy detected: %r" % (next_pending,))
        pending = next_pending
        emitted = next_emitted


def timedelta_to_string(td: datetime.timedelta) -> str:
    """
    Convert a timedelta to a string.
    """
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


def string_to_timedelta(s: str) -> datetime.timedelta:
    """
    Convert a string to a timedelta.
    """
    seconds = pytimeparse.parse(s)
    if seconds is None:
        raise Exception(f"Invalid duration string: {s}")
    return datetime.timedelta(seconds=seconds)

def number_to_timedelta(nhours: int|float) -> datetime.timedelta:
    """
    Convert a number to a timedelta.
    """
    return datetime.timedelta(hours=nhours)

def import_object(object_path):
    """
    Import and object from a dotted string path. Use single colon ':' to separate module and object.
    ex: mymodule.mysubmodule:MyClass
    """
    module_path, object_name = object_path.rsplit(":", 1)
    module = __import__(module_path, fromlist=[object_name])
    current = module
    for part in object_name.split("."):
        try:
            current = getattr(current, part)
        except AttributeError:
            raise ImportError(f"Object {object_name} not found in module {module_path}")
    return current
