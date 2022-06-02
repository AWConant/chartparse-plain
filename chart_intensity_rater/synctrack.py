import re

import chart_intensity_rater.track

from chart_intensity_rater.exceptions import RegexFatalNotMatchError
from chart_intensity_rater.tick import TickEvent
from chart_intensity_rater.util import DictPropertiesEqMixin


class SyncTrack(object):
    def __init__(self, iterator_getter):
        self.time_signature_events = chart_intensity_rater.track.parse_events_from_iterable(
                iterator_getter(), TimeSignatureEvent.from_chart_line)
        self.bpm_events = chart_intensity_rater.track.parse_events_from_iterable(
                iterator_getter(), BPMEvent.from_chart_line)
        # TODO: Validate that there is a time signature event at tick 0.
        # TODO: Validate that there is a BPM event at tick 0.


class TimeSignatureEvent(TickEvent, DictPropertiesEqMixin):
    # Match 1: Tick
    # Match 2: Upper numeral
    # Match 3: Lower numeral (optional; assumed to be 4 if absent)
    _regex = r"^\s\s(\d+?)\s=\sTS\s(\d+?)(?:\s(\d+?))?$"
    _regex_prog = re.compile(_regex)

    def __init__(self, tick, upper_numeral, lower_numeral):
        super().__init__(tick)
        self.upper_numeral = upper_numeral
        self.lower_numeral = lower_numeral

    @classmethod
    def from_chart_line(cls, line):
        m = cls._regex_prog.match(line)
        if not m:
            raise RegexFatalNotMatchError(cls._regex, line)
        tick, upper_numeral = int(m.group(1)), int(m.group(2))
        # For some reason, the lower number is written by Moonscraper as the
        # exponent of whatever power of 2 it is.
        lower_numeral = 2**int(m.group(3)) if m.group(3) else 4
        return cls(tick, upper_numeral, lower_numeral)

    def __str__(self):
        return f"{type(self).__name__}(t@{self.tick:07}: {self.upper_numeral}/{self.lower_numeral})"  # pragma: no cover

    def __repr__(self):
        return str(self.__dict__)  # pragma: no cover


class BPMEvent(TickEvent):
    # Match 1: Tick
    # Match 2: BPM (the last 3 digits are the decimal places)
    _regex = r"^\s*?(\d+?)\s=\sB\s(\d+?)\s*?$"
    _regex_prog = re.compile(_regex)

    def __init__(self, tick, bpm):
        super().__init__(tick)
        self.bpm = bpm

    @classmethod
    def from_chart_line(cls, line):
        m = cls._regex_prog.match(line)
        if not m:
            raise RegexFatalNotMatchError(cls._regex, line)
        tick, raw_bpm = int(m.group(1)), m.group(2)
        bpm_whole_part_str, bpm_decimal_part_str = raw_bpm[:-3], raw_bpm[-3:]
        bpm_whole_part = int(bpm_whole_part_str) if bpm_whole_part_str != "" else 0
        bpm_decimal_part = int(bpm_decimal_part_str)/1000
        bpm = bpm_whole_part + bpm_decimal_part
        return cls(tick, bpm)

    def __str__(self):
        return f"{type(self).__name__}(t@{self.tick:07}: {self.bpm})"  # pragma: no cover

    def __repr__(self):
        return str(self.__dict__)  # pragma: no cover


