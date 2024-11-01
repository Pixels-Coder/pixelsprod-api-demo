import re
from .constants import WORK_DAY_DURATION
from pydantic import BaseModel
from typing import Optional
import threading
from contextlib import contextmanager

WORK_TIME_REG = re.compile(r"^(?:(\d+\.?\d*)\s*(days?|d)\s*)?(?:(\d+\.?\d*)\s*(hours?|h)\s*)?(?:(\d+\.?\d*)\s*(minutes?|min)\s*)?$")

context_work_day_duration = threading.local()

class Duration(BaseModel):
    total_hours: float
    work_day_duration: Optional[float] = None



    @staticmethod
    def push_context_work_day_duration(work_day_duration: float):
        if not hasattr(context_work_day_duration, "stack"):
            context_work_day_duration.stack = []
        context_work_day_duration.stack.append(work_day_duration)

    @staticmethod
    def pop_context_work_day_duration():
        if not hasattr(context_work_day_duration, "stack") or not context_work_day_duration.stack:
            raise ValueError("No work day duration in stack")
        return context_work_day_duration.stack.pop()

    @staticmethod
    def get_context_work_day_duration():
        if not hasattr(context_work_day_duration, "stack"):
            raise Exception("No work day duration in context")
        return context_work_day_duration.stack[-1]

    @staticmethod
    @contextmanager
    def work_day_duration_context(work_day_duration: float):
        Duration.push_context_work_day_duration(work_day_duration)
        size = len(context_work_day_duration.stack)
        yield
        if len(context_work_day_duration.stack) != size:
            raise ValueError("Stack size changed during context")
        Duration.pop_context_work_day_duration()

    @staticmethod
    def string_to_hours(value: str, work_day_duration: Optional[float]=None):
        if work_day_duration is None:
            work_day_duration = Duration.get_context_work_day_duration()
        try:
            return float(value)
        except ValueError:
            pass
        value = value.strip()
        m = WORK_TIME_REG.match(value)
        if not m:
            raise ValueError(f"Invalid work time string: {value}")
        days = m.group(1)
        hours = m.group(3)
        minutes = m.group(5)
        total_hours = 0
        if days:
            total_hours += float(days) * work_day_duration
        if hours:
            total_hours += float(hours)
        if minutes:
            total_hours += float(minutes) / 60.0
        return total_hours

    def __init__(self, value: str|float|int, work_day_duration: Optional[float]=None):
        if isinstance(value, str):
            value = Duration.string_to_hours(value)
        work_day_duration = work_day_duration
        super(Duration, self).__init__(total_hours=value, work_day_duration=work_day_duration)

    def days(self):
        work_day_duration = self.work_day_duration or Duration.get_context_work_day_duration()
        return self.total_hours // work_day_duration

    def hours(self):
        work_day_duration = self.work_day_duration or Duration.get_context_work_day_duration()
        return (self.total_hours % work_day_duration) // 1

    def minutes(self):
        return (self.total_hours % 1) * 60

    def to_string(self):
        days = self.days()
        hours = self.hours()
        minutes = self.minutes()
        value = ""
        if days:
            if days == 1:
                value += "1 day "
            else:
                value += f"{days:.4g} days "
        if hours:
            if hours == 1:
                value += "1 hour "
            else:
                value += f"{hours:.4g} hours "
        if minutes:
            if minutes == 1:
                value += "1 minute"
            else:
                value += f"{minutes:.4g} minutes"
        return value.strip()

    def __repr__(self):
        return f"Duration(\"{self.to_string()}\")"
