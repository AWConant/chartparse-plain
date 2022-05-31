import collections
import re

import chart_intensity_rater.track

from chart_intensity_rater.enums import Note
from chart_intensity_rater.exceptions import RegexFatalNotMatchError
from chart_intensity_rater.tick import TickEvent


_min_note_instrument_track_index = 0
_max_note_instrument_track_index = 4
_open_instrument_track_index     = 7
_forced_instrument_track_index   = 5
_tap_instrument_track_index      = 6


class InstrumentTrack(object):
    def __init__(self, instrument, difficulty, iterator_getter):
        self.instrument = instrument
        self.difficulty = difficulty
        self.note_events = self._parse_note_events_from_iterable(iterator_getter())
        self.star_power_events = chart_intensity_rater.track.parse_events_from_iterable(
                iterator_getter(), StarPowerEvent)

    def __str__(self):  # pragma: no cover
        return (
                f"Instrument: {self.instrument}\n"
                f"Difficulty: {self.difficulty}\n"
                f"Note count: {len(self.note_events)}\n"
                f"Star power phrase count: {len(self.star_power_events)}")

    @staticmethod
    def _parse_note_events_from_iterable(iterable):
        tick_to_note_array = collections.defaultdict(lambda: bytearray(5))
        tick_to_duration_list = collections.defaultdict(lambda: [0]*5)
        tick_to_is_tap = collections.defaultdict(bool)
        tick_to_is_forced = collections.defaultdict(bool)
        for line in iterable:
            m = NoteEvent._regex_prog.match(line)
            if not m:
                continue
            tick, note_index, duration = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if _min_note_instrument_track_index <= note_index <= _max_note_instrument_track_index:
                tick_to_note_array[tick][note_index] = 1
                tick_to_duration_list[tick][note_index] = duration
            elif note_index == _tap_instrument_track_index:
                tick_to_is_tap[tick] = True
            elif note_index == _forced_instrument_track_index:
                tick_to_is_forced[tick] = True
            else:
                # TODO: Log unhandled instrument track note index.
                pass

        def all_same(durations):
            return durations.count(durations[0]) == len(durations)

        events = []
        for tick in tick_to_note_array.keys():
            note = Note(tick_to_note_array[tick])
            duration_list = tick_to_duration_list[tick]
            duration = duration_list[0] if all_same(duration_list) else duration_list
            event = NoteEvent(tick, note, duration, tick_to_is_forced[tick], tick_to_is_tap[tick])
            events.append(event)
        events.sort(key=lambda e: e.tick)

        return events


class NoteEvent(TickEvent):
    # This regex matches a single "N" line within a instrument track section,
    # but this class should be used to represent all of the notes at a
    # particular tick. This means that you might need to consolidate multiple
    # "N" lines into a single NoteEvent, e.g. for chords.
    # Match 1: Tick
    # Match 2: Note index
    # Match 3: Duration (ticks)
    _regex = r"^\s*?(\d+?)\s=\sN\s([0-7])\s(\d+?)\s*?$"
    _regex_prog = re.compile(_regex)

    def __init__(self, tick, note, duration=None, is_forced=False, is_tap=False):
        super().__init__(tick)
        self.note = note
        # duration can be either integer or tuple(5). tuple is for ticks with
        # notes of independent durations.
        self.duration = duration if duration else 0
        self.is_forced = is_forced
        self.is_tap = is_tap

    def __str__(self):  # pragma: no cover
        to_join = [f"{type(self).__name__}(t@{self.tick:07}: {self.note}"]
        flags = []
        if self.is_forced:
            flags.append("F")
        if self.is_tap:
            flags.append("T")
        if flags:
            to_join.extend([" [flags=", ''.join(flags), "]"])
        to_join.append(')')
        return ''.join(to_join)

    def __repr__(self):  # pragma: no cover
        return str(self.__dict__)


class StarPowerEvent(TickEvent):
    # Match 1: Tick
    # Match 2: Note index (Might be always 2? Not sure what this is, to be honest.)
    # Match 3: Duration (ticks)
    _regex = r"^\s*?(\d+?)\s=\sS\s(\d+?)\s(\d+?)\s*?$"
    _regex_prog = re.compile(_regex)

    def __init__(self, tick, duration):
        super().__init__(tick)
        self.duration = duration

    @classmethod
    def from_chart_line(cls, line):
        m = cls._regex_prog.match(line)
        if not m:
            raise RegexFatalNotMatchError(cls._regex, line)
        tick, duration = int(m.group(1)), int(m.group(3))
        return cls(tick, duration)
