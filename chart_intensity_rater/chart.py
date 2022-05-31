import collections
import itertools
import re

from chart_intensity_rater.enums import Difficulty, Instrument
from chart_intensity_rater.eventstrack import Events
from chart_intensity_rater.instrumenttrack import InstrumentTrack
from chart_intensity_rater.properties import Properties
from chart_intensity_rater.synctrack import SyncTrack


class Chart(object):
    _required_sections = ("Song", "SyncTrack")
    _instrument_track_name_to_instrument_difficulty_pair = {
            d+i: (Instrument(i), Difficulty(d)) for i, d in itertools.product(
                Instrument.all_values(), Difficulty.all_values())}

    def __init__(self, fp):
        lines = fp.read().splitlines()
        sections = self._find_sections(lines)
        if not all(section in sections for section in self._required_sections):
            raise ValueError(f"parsed section list {list(sections.keys())} does not contain all "
                             f"required sections {self._required_sections}")

        self.instrument_tracks = collections.defaultdict(dict)
        for section_name, iterator_getter in sections.items():
            if section_name == "Song":
                self.properties = Properties(iterator_getter)
            elif section_name == "Events":
                self.events_track = Events(iterator_getter)
            elif section_name == "SyncTrack":
                self.sync_track = SyncTrack(iterator_getter)
            elif section_name in self._instrument_track_name_to_instrument_difficulty_pair:
                instrument, difficulty = self._instrument_track_name_to_instrument_difficulty_pair[section_name]
                track = InstrumentTrack(instrument, difficulty, iterator_getter)
                self.instrument_tracks[instrument][difficulty] = track
            else:
                # TODO: Log unhandled section.
                pass

    _section_name_regex_prog = re.compile(r"^\[(.+?)\]$")

    @classmethod
    def _find_sections(cls, lines):
        sections = dict()
        curr_section_name = None
        curr_first_line_idx = None
        curr_last_line_idx = None
        for i, line in enumerate(lines):
            if curr_section_name is None:
                m = cls._section_name_regex_prog.match(line)
                if not m:
                    raise ValueError(f"could not parse section name from line '{line}'")
                curr_section_name = m.group(1)
            elif line == "{":
                curr_first_line_idx = i+1
            elif line == "}":
                curr_last_line_idx = i-1
                # Set default values for x and y so their current values are
                # captured, rather than references to these local variables.
                iterator_getter = lambda x=curr_first_line_idx, y=curr_last_line_idx: itertools.islice(lines, x, y+1)
                sections[curr_section_name] = iterator_getter
                curr_section_name = None
                curr_first_line_idx = None
                curr_last_line_idx = None
        return sections

