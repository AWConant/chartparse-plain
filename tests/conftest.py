import math
import pytest

from chart_intensity_rater.eventstrack import Events, EventsEvent
from chart_intensity_rater.synctrack import BPMEvent, TimeSignatureEvent
from chart_intensity_rater.tick import TickEvent


_default_tick = 100

_default_bpm = 120.000
_default_bpm_event = BPMEvent(_default_tick, _default_bpm)
_default_bpm_event_list = [_default_bpm_event]

_default_upper_time_signature_numeral = 4
_default_lower_time_signature_numeral = 8
_default_time_signature_event = TimeSignatureEvent(
        _default_tick, _default_upper_time_signature_numeral, _default_lower_time_signature_numeral)
_default_time_signature_event_list = [_default_time_signature_event]

_default_events_event_command = "lyric"
_default_events_event_params = "Break"
_default_events_event = EventsEvent(
        _default_tick, _default_events_event_command, _default_events_event_params)
_default_events_event_list = [_default_events_event]


def pytest_configure():
    pytest.default_tick = _default_tick

    pytest.default_bpm = _default_bpm
    pytest.default_bpm_event_list = _default_bpm_event_list

    pytest.default_upper_time_signature_numeral = _default_upper_time_signature_numeral
    pytest.default_lower_time_signature_numeral = _default_lower_time_signature_numeral
    pytest.default_time_signature_event_list = _default_time_signature_event_list

    pytest.default_events_event_command = _default_events_event_command
    pytest.default_events_event_params = _default_events_event_params
    pytest.default_events_event_list = _default_events_event_list


@pytest.fixture
def iterator_getter():
    return lambda: range(10)


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


@pytest.fixture(params=['tick_event', 'time_signature_event', 'bpm_event', 'events_event'])
def tick_having_event(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def mock_parse_events_from_iterable(mocker):
    return mocker.patch(
            'chart_intensity_rater.track.parse_events_from_iterable',
            side_effect=parse_events_from_iterable_side_effect)


def parse_events_from_iterable_side_effect(iterable, event_type): 
    if event_type is TimeSignatureEvent:
        return _default_time_signature_event_list
    elif event_type is BPMEvent:
        return _default_bpm_event_list
    elif event_type is EventsEvent:
        return _default_events_event_list


@pytest.fixture
def generate_valid_bpm_line():
    return generate_valid_bpm_line_fn


def generate_valid_bpm_line_fn(tick=_default_tick, bpm=_default_bpm):
    bpm_sans_decimal_point = int(bpm*1000)
    if bpm_sans_decimal_point != bpm*1000:
        raise ValueError(f"bpm {bpm} has more than 3 decimal places")
    return f"  {tick} = B {bpm_sans_decimal_point}"


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
