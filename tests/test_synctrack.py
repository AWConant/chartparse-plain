import math
import pytest

from chart_intensity_rater.exceptions import RegexFatalNotMatchError
from chart_intensity_rater.synctrack import BPMEvent, TimeSignatureEvent, SyncTrack


class TestSyncTrack(object):
    def test_init(self, mock_parse_events_from_iterable, iterator_getter):
        sync_track = SyncTrack(iterator_getter)
        assert sync_track.time_signature_events == pytest.default_time_signature_event_list
        assert sync_track.bpm_events == pytest.default_bpm_event_list


class TestTimeSignatureEvent(object):
    def test_init(self, time_signature_event):
        assert time_signature_event.upper_numeral == pytest.default_upper_time_signature_numeral
        assert time_signature_event.lower_numeral == pytest.default_lower_time_signature_numeral

    def test_from_chart_line_short(self):
        line = generate_valid_time_signature_line()
        event = TimeSignatureEvent.from_chart_line(line)
        assert event.tick == pytest.default_tick
        assert event.upper_numeral == pytest.default_upper_time_signature_numeral

    def test_from_chart_line_long(self):
        line = generate_valid_time_signature_line(lower_numeral=pytest.default_lower_time_signature_numeral)
        event = TimeSignatureEvent.from_chart_line(line)
        assert event.tick == pytest.default_tick
        assert event.upper_numeral == pytest.default_upper_time_signature_numeral
        assert event.lower_numeral == pytest.default_lower_time_signature_numeral

    def test_from_chart_line_no_match(self):
        line = generate_valid_bpm_line()
        with pytest.raises(RegexFatalNotMatchError):
            _ = TimeSignatureEvent.from_chart_line(line)


class TestBPMEvent(object):
    def test_init(self, bpm_event):
        assert bpm_event.bpm == pytest.default_bpm

    def test_from_chart_line(self):
        line = generate_valid_bpm_line()
        event = BPMEvent.from_chart_line(line)
        assert event.tick == pytest.default_tick
        assert event.bpm == pytest.default_bpm

    def test_from_chart_line_no_match(self):
        line = generate_valid_time_signature_line()
        with pytest.raises(RegexFatalNotMatchError):
            _ = BPMEvent.from_chart_line(line)


def generate_valid_bpm_line(tick=pytest.default_tick, bpm=pytest.default_bpm):
    bpm_sans_decimal_point = int(bpm*1000)
    if bpm_sans_decimal_point != bpm*1000:
        raise ValueError(f"bpm {bpm} has more than 3 decimal places")
    return f"  {tick} = B {bpm_sans_decimal_point}"


def test_generate_valid_bpm_line():
    assert generate_valid_bpm_line(100, 120.000) == "  100 = B 120000"


def test_generate_valid_bpm_line_raises_ValueError():
    with pytest.raises(ValueError):
        _ = generate_valid_bpm_line(100, 120.5555)


def generate_valid_time_signature_line(
        tick=pytest.default_tick,
        upper_numeral=pytest.default_upper_time_signature_numeral,
        lower_numeral=None):
    if lower_numeral:
        return f"  {tick} = TS {upper_numeral} {int(math.log(lower_numeral, 2))}"
    else:
        return f"  {tick} = TS {upper_numeral}"
    

def test_generate_valid_time_signature_line_short():
    assert generate_valid_time_signature_line(100, 4) == "  100 = TS 4"


def test_generate_valid_time_signature_line_long():
    assert generate_valid_time_signature_line(100, 4, 8) == "  100 = TS 4 3"
