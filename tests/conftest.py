import math
import pytest

from chart_intensity_rater.enums import Instrument, Difficulty, Note
from chart_intensity_rater.eventstrack import Events, EventsEvent
from chart_intensity_rater.instrumenttrack import (
        InstrumentTrack, NoteEvent, StarPowerEvent, _min_note_instrument_track_index)
from chart_intensity_rater.synctrack import SyncTrack, BPMEvent, TimeSignatureEvent
from chart_intensity_rater.tick import TickEvent


_default_tick = 100

_default_bpm = 120.000
_default_bpm_event = BPMEvent(_default_tick, _default_bpm)
_default_bpm_event_list = [_default_bpm_event]


@pytest.fixture
def generate_valid_bpm_line():
    return generate_valid_bpm_line_fn


def generate_valid_bpm_line_fn(tick=_default_tick, bpm=_default_bpm):
    bpm_sans_decimal_point = int(bpm*1000)
    if bpm_sans_decimal_point != bpm*1000:
        raise ValueError(f"bpm {bpm} has more than 3 decimal places")
    return f"  {tick} = B {bpm_sans_decimal_point}"


_default_upper_time_signature_numeral = 4
_default_lower_time_signature_numeral = 8
_default_time_signature_event = TimeSignatureEvent(
        _default_tick, _default_upper_time_signature_numeral, _default_lower_time_signature_numeral)
_default_time_signature_event_list = [_default_time_signature_event]


@pytest.fixture
def generate_valid_long_time_signature_line():
    def generate_valid_long_time_signature_line_fn():
        return generate_valid_time_signature_line_fn(lower_numeral=_default_lower_time_signature_numeral)
    return generate_valid_long_time_signature_line_fn


@pytest.fixture
def generate_valid_short_time_signature_line():
    return generate_valid_time_signature_line_fn


def generate_valid_time_signature_line_fn(
        tick=_default_tick,
        upper_numeral=_default_upper_time_signature_numeral,
        lower_numeral=None):
    if lower_numeral:
        return f"  {tick} = TS {upper_numeral} {int(math.log(lower_numeral, 2))}"
    else:
        return f"  {tick} = TS {upper_numeral}"


_default_events_event_command = "test_command"
_default_events_event_params = "test_param"
_default_events_event = EventsEvent(
        _default_tick, _default_events_event_command, _default_events_event_params)
_default_events_event_list = [_default_events_event]


@pytest.fixture
def generate_valid_events_line():
    return generate_valid_events_line_fn


def generate_valid_events_line_fn(
        tick=_default_tick,
        command=_default_events_event_command,
        params=None):
    to_join = [f"  {tick} = E \"{command}"]
    if params:
        to_join.append(f" {params}")
    to_join.append("\"")
    return ''.join(to_join)


_default_difficulty = Difficulty.EXPERT
_default_instrument = Instrument.GUITAR
_default_duration = 100  # ticks

_default_note = Note.G
_default_note_instrument_track_index = _min_note_instrument_track_index


@pytest.fixture
def generate_valid_note_line():
    return generate_valid_note_line_fn


def generate_valid_note_line_fn(
        tick=_default_tick,
        note=_default_note_instrument_track_index,
        duration=0):
    return f"  {tick} = N {note} {duration}"


_default_note_line = generate_valid_note_line_fn()
_default_note_event = NoteEvent(_default_tick, _default_note)
_default_note_event_list = [_default_note_event]


_default_star_power_event = StarPowerEvent(_default_tick, _default_duration)
_default_star_power_event_list = [_default_star_power_event]


@pytest.fixture
def generate_valid_star_power_line():
    return generate_valid_star_power_line_fn


def generate_valid_star_power_line_fn(tick=_default_tick, duration=_default_duration):
    return f"  {tick} = S 2 {duration}"


def pytest_configure():
    pytest.default_tick = _default_tick
    pytest.default_duration = _default_duration

    pytest.default_bpm = _default_bpm
    pytest.default_bpm_event = _default_bpm_event
    pytest.default_bpm_event_list = _default_bpm_event_list

    pytest.default_upper_time_signature_numeral = _default_upper_time_signature_numeral
    pytest.default_lower_time_signature_numeral = _default_lower_time_signature_numeral
    pytest.default_time_signature_event_list = _default_time_signature_event_list

    pytest.default_events_event_command = _default_events_event_command
    pytest.default_events_event_params = _default_events_event_params
    pytest.default_events_event_list = _default_events_event_list

    pytest.default_instrument = _default_instrument
    pytest.default_difficulty = _default_difficulty

    pytest.default_note = _default_note
    pytest.default_note_event_list = _default_note_event_list

    pytest.default_star_power_event_list = _default_star_power_event_list


@pytest.fixture
def invalid_chart_line():
    return "this_line_is_invalid"


@pytest.fixture
def garbage_string_iterator_getter(invalid_chart_line):
    return lambda: [invalid_chart_line]


@pytest.fixture
def unmatchable_regex():
    # https://stackoverflow.com/a/1845097
    return r"(?!x)x"


@pytest.fixture
def tick_event():
    return TickEvent(_default_tick)


@pytest.fixture
def time_signature_event():
    return _default_time_signature_event


@pytest.fixture
def bpm_event():
    return _default_bpm_event


@pytest.fixture
def events_event():
    return _default_events_event


# TODO: ... why does coverage care about this fixture?
@pytest.fixture
def note_event():  # pragma: no cover
    return _default_note_event


@pytest.fixture
def note_event_with_all_optionals_set():
    return NoteEvent(
            _default_tick, _default_note, duration=_default_duration,is_forced=True, is_tap=True)


@pytest.fixture
def star_power_event():
    return _default_star_power_event


# TODO: ... why does coverage care about this fixture?
@pytest.fixture
def note_lines():  # pragma: no cover
    return [_default_note_line]


@pytest.fixture
def events_track_invalid_lines(mock_parse_events_from_iterable, garbage_string_iterator_getter):
    return Events(garbage_string_iterator_getter)


@pytest.fixture
def sync_track_invalid_lines(mock_parse_events_from_iterable, garbage_string_iterator_getter):
    return SyncTrack(garbage_string_iterator_getter)


@pytest.fixture
def instrument_track_invalid_lines(
        mocker, mock_parse_events_from_iterable, garbage_string_iterator_getter):
    mocker.patch(
            'chart_intensity_rater.instrumenttrack.InstrumentTrack._parse_note_events_from_iterable',
            return_value=pytest.default_note_event_list)
    return InstrumentTrack(
            pytest.default_instrument, pytest.default_difficulty, garbage_string_iterator_getter)


@pytest.fixture(params=['tick_event', 'time_signature_event', 'bpm_event', 'events_event'])
def tick_having_event(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def mock_parse_events_from_iterable_with_return(mocker, request):  # pragma: no cover
    return mocker.patch(
            'chart_intensity_rater.track.parse_events_from_iterable',
            return_value=request.param)


@pytest.fixture
def mock_parse_events_from_iterable(mocker):
    return mocker.patch(
            'chart_intensity_rater.track.parse_events_from_iterable',
            side_effect=parse_events_from_iterable_side_effect)


def parse_events_from_iterable_side_effect(iterable, from_chart_line_fn):  # pragma: no cover
    event_type = from_chart_line_fn.__self__
    if event_type is TimeSignatureEvent:
        return _default_time_signature_event_list
    elif event_type is BPMEvent:
        return _default_bpm_event_list
    elif event_type is EventsEvent:
        return _default_events_event_list
    elif event_type is NoteEvent:
        return _default_note_event_list
    elif event_type is StarPowerEvent:
        return _default_star_power_event_list
    else:
        raise ValueError(f"event_type {event_type} not handled")
