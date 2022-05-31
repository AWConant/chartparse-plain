import pytest

from chart_intensity_rater.tick import TickEvent


class TestTickEvent(object):
    def test_init(self, tick_having_event):
        assert tick_having_event.tick == pytest.default_tick
