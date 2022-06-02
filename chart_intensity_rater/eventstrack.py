import re

import chart_intensity_rater.track

from chart_intensity_rater.exceptions import RegexFatalNotMatchError
from chart_intensity_rater.tick import TickEvent
from chart_intensity_rater.util import DictPropertiesEqMixin


class Events(object):
    def __init__(self, iterator_getter):
        self.events = chart_intensity_rater.track.parse_events_from_iterable(
                iterator_getter(), EventsEvent.from_chart_line)


class EventsEvent(TickEvent, DictPropertiesEqMixin):
    # Match 1: Tick
    # Match 2: Event command
    # Match 3: Event parameters (optional)
    _regex = r"^\s*?(\d+?)\s=\sE\s\"([a-z0-9_]+?)(?:\s(.+?))?\"\s*?$"
    _regex_prog = re.compile(_regex)

    def __init__(self, tick, command, params=None):
        super().__init__(tick)
        self.command = command
        self.params = params

    @classmethod
    def from_chart_line(cls, line):
        m = cls._regex_prog.match(line)
        if not m:
            raise RegexFatalNotMatchError(cls._regex, line)
        tick, command, params = int(m.group(1)), m.group(2), m.group(3)
        return cls(tick, command, params)

    def __str__(self):  # pragma: no cover
        to_join = [f"{type(self).__name__}(t@{self.tick:07}: {self.command}"]
        if self.params:
            to_join.append(f" [params={self.params}]")
        to_join.append(")")
        return ''.join(to_join)

    def __repr__(self):  # pragma: no cover
        return str(self.__dict__)
