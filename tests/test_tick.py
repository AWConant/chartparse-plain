import pytest

from chart_intensity_rater.event import Event


class TestEvent(object):
    def test_init(self, tick_having_event):
        assert tick_having_event.tick == pytest.default_tick
