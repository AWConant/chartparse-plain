from chart_intensity_rater.exceptions import RegexFatalNotMatchError


def parse_events_from_iterable(iterable, event_type):
    events = []
    for line in iterable:
        try:
            event = event_type.from_chart_line(line)
        except RegexFatalNotMatchError:
            continue
        events.append(event)
    return events
