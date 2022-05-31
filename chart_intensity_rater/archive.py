import io
import json
import operator
import re
import sys
import types


DEFAULT_DIFFICULTY = "ExpertSingle"

HEADING_REGEX = r"^\[(.+)\]$"
OPEN_REGEX = r"^\{$"
CLOSE_REGEX = r"^\}$"
HEADING_ELEMENT_REGEX = r"^\s*(.+)\s=\s(.+)$"

TIME_SIGNATURE_REGEX = r"^TS\s(\d+)$"
BPM_REGEX = r"^B\s(\d+)$"

NOTE_REGEX = r"^N\s(\d)\s\d$"

MAX_NOTE = 4
MIN_NOTE = 7
NOTE_TO_POS = {
    0: 23,
    1: 41,
    2: 59,
    3: 77,
    4: 95,
    7: 5,
}

NOTES_PER_SECOND_CEILING = 10


class BPMEvent(object):
    def __init__(self, tick, bpm):
        self.tick = tick
        self.bpm = bpm

    def __repr__(self):
        return f"BPMEvent({self.tick}, {self.bpm})"


class Note(object):
    def __init__(self, tick, index):
        self.tick = tick
        self.index = index

    def __repr__(self):
        return f"Note({self.tick}, {self.index})"

    def to_chart_string(self):
        return f"{self.tick} = N {self.index} 0"


def pos_to_note_index(lookup_pos):
    closest_note = None
    minimum_pos_delta = float('inf')
    for note_index, pos in NOTE_TO_POS.items():
        delta = abs(lookup_pos-pos)
        if delta < minimum_pos_delta:
            closest_note = note_index
            minimum_pos_delta = delta
    return closest_note


# in: 12345; out: 12.345
def five_digit_bpm_to_real_bpm(bpm):
    whole_part = bpm//1000
    decimal_part = (bpm - whole_part*1000)/1000
    return whole_part + decimal_part


def build_tempo_history(chart):
    history = [(0, 0)]
    for i, bpm_event in enumerate(chart.sync_track):
        if i == 0:
            continue
        prev_bpm_event = chart.sync_track[i-1]
        prev_ticks_since_start, prev_millis_since_start = history[i-1]

        ticks_since_last_event = bpm_event.tick-prev_bpm_event.tick
        ticks_since_start = prev_ticks_since_start + ticks_since_last_event

        millis_since_last_event = chart.ticks_to_millis(ticks_since_last_event, prev_bpm_event.bpm)
        millis_since_start = millis_since_last_event + prev_millis_since_start

        history.append((ticks_since_start, millis_since_start))
    return history


def millis_since_start_at_tick(tick, chart, tempo_history):
    current_event_index = None
    current_event_tick = None
    for i, bpm_event in reversed(list(enumerate(chart.sync_track))):
        if tick >= bpm_event.tick:
            current_event_index = i
            current_event_tick = bpm_event.tick
            break

    ticks_since_current_event = tick-current_event_tick
    current_bpm = chart.sync_track[current_event_index].bpm
    millis_since_current_event = chart.ticks_to_millis(ticks_since_current_event, current_bpm)
    _, millis_before_current_event = tempo_history[i]
    return millis_since_current_event + millis_before_current_event


class Chart(object):
    def __init__(self, fp):
        '''
        @fp: an open file of type .chart
        '''
        self.raw_lines = fp.read().splitlines()

        chart_dict = self.__parse_lines_to_dict(self.raw_lines)
        self.offset = chart_dict["Song"]["Offset"]
        self.resolution = chart_dict["Song"]["Resolution"]
        self.player2 = chart_dict["Song"]["Player2"]
        self.difficulty = chart_dict["Song"]["Difficulty"]
        self.preview_start = chart_dict["Song"]["PreviewStart"]
        self.preview_end = chart_dict["Song"]["PreviewEnd"]
        self.genre = chart_dict["Song"]["Genre"]
        self.media_type = chart_dict["Song"]["MediaType"]
        self.music_stream = chart_dict["Song"]["MusicStream"]

        self.sync_track = self.__parse_sync_track(chart_dict)

        self.notes = self.__parse_notes_from_chart_dict(chart_dict, DEFAULT_DIFFICULTY)

        ticks_with_notes = set()
        for note in self.notes:
            if note.tick in ticks_with_notes:
                print(f"Note already present at tick {note.tick}")
            ticks_with_notes.add(note.tick)

    def dump_to_string(self):
        notes_section_header_index = 0
        section_header = f"[{DEFAULT_DIFFICULTY}]"
        for notes_section_header_index, _ in enumerate(self.raw_lines):
            if self.raw_lines[notes_section_header_index] == section_header:
                break
        if notes_section_header_index == len(self.raw_lines)-1:
            self.raw_lines.append(section_header)
            self.raw_lines.append("{")
            self.raw_lines.append("}")
            notes_section_header_index += 1
        notes_section_open_index = notes_section_header_index + 1

        notes_section_close_index = notes_section_open_index + 1
        while self.raw_lines[notes_section_close_index] != "}":
            notes_section_close_index += 1

        lines_head = self.raw_lines[:notes_section_open_index+1]

        note_lines = []
        for note in self.notes:
            note_lines.append(f"  {note.to_chart_string()}")

        lines_tail = self.raw_lines[notes_section_close_index:]

        lines = lines_head + note_lines + lines_tail
        return "\n".join(lines)

    def ticks_to_millis(self, ticks, bpm):
        ticks_per_minute = self.resolution * bpm
        ticks_per_second = ticks_per_minute/60
        ticks_in_seconds = ticks/ticks_per_second
        return ticks_in_seconds*1000

    def millis_to_ticks(self, millis, bpm):
        ticks_per_minute = self.resolution * bpm
        ticks_per_second = ticks_per_minute/60
        ticks_per_milli = ticks_per_second/1000
        return ticks_per_milli*millis

    def __parse_lines_to_dict(self, lines):
        chart_dict = dict()
        current_heading = None
        heading_dict = None
        for line in lines:
            heading_m = re.match(HEADING_REGEX, line)
            if heading_m is not None:
                current_heading = heading_m.group(1)
                heading_dict = dict()
                continue

            open_group_m = re.match(OPEN_REGEX, line)
            if open_group_m is not None:
                continue

            close_group_m = re.match(CLOSE_REGEX, line)
            if close_group_m is not None:
                chart_dict[current_heading] = heading_dict
                continue

            heading_element_m = re.match(HEADING_ELEMENT_REGEX, line)
            if heading_element_m is not None:
                key, value = heading_element_m.group(1), heading_element_m.group(2)
                heading_dict[_sanitize_token(key)] = _sanitize_token(value)
                continue

            raise Exception(f"unhandled chart line: {line}")

        return chart_dict

    def __parse_sync_track(self, chart_dict):
        track_events = list(chart_dict["SyncTrack"].items())
        track_events.sort(key=operator.itemgetter(0))

        sync_track = []
        for tick, eventstring in track_events:
            time_signature_m = re.match(TIME_SIGNATURE_REGEX, eventstring)
            if time_signature_m is not None:
                # TODO: Don't ignore time signatures.
                continue

            bpm_m = re.match(BPM_REGEX, eventstring)
            if bpm_m is not None:
                bpm = int(bpm_m.group(1))
                sync_track.append(BPMEvent(tick, five_digit_bpm_to_real_bpm(bpm)))
                continue

            raise Exception(f"unhandled sync_track eventstring: {eventstring}")

        return sync_track

    def __parse_notes_from_chart_dict(self, chart_dict, difficulty_name):
        note_events = list(chart_dict[difficulty_name].items())

        notes = []
        for tick, eventstring in note_events:
            note_m = re.match(NOTE_REGEX, eventstring)
            if note_m is not None:
                notes.append(Note(tick, int(note_m.group(1))))
                continue

            raise Exception(f"unhandled note eventstring: {eventstring}")

        return notes

    def __ticks_since_start_at_millis(self, millis, tempo_history):
        # TODO: This can be refactored out along with the other block with this comment.
        current_event_index = None
        current_event_millis = None
        for i, (_, millis_since_start) in reversed(list(enumerate(tempo_history))):
            if millis >= millis_since_start:
                current_event_index = i
                current_event_millis = millis_since_start
                break

        millis_since_current_event = millis-current_event_millis
        current_bpm = self.sync_track[current_event_index].bpm
        ticks_since_current_event = self.millis_to_ticks(millis_since_current_event, current_bpm)
        ticks_before_current_event, _ = tempo_history[i]
        return ticks_since_current_event + ticks_before_current_event

    def __quantize_ticks(self, ticks, tempo_history):
        # TODO: This can be refactored out along with the other block with this comment.
        current_event_index = None
        millis_until_last_bpm_event = None
        ticks_until_last_bpm_event = None
        current_bpm = None
        for i, (ticks_since_start, millis_since_start) in reversed(list(enumerate(tempo_history))):
            if ticks >= ticks_since_start:
                current_event_index = i
                millis_until_last_bpm_event = millis_since_start
                ticks_until_last_bpm_event = ticks_since_start
                current_bpm = self.sync_track[current_event_index].bpm
                break

        notes_per_measure = 128
        while True:
            notes_per_beat = notes_per_measure//4
            notes_per_second = notes_per_beat * current_bpm / 60
            if notes_per_second < NOTES_PER_SECOND_CEILING:
                break
            notes_per_measure //= 2

        ticks_since_last_bpm_event = ticks-ticks_until_last_bpm_event
        ticks_per_note = self.resolution//notes_per_beat
        quantized_ticks_since_last_bpm_event = round_to_nearest_multiple(
            ticks_since_last_bpm_event, ticks_per_note)
        return round(quantized_ticks_since_last_bpm_event + ticks_until_last_bpm_event)

    def __str__(self):
        return f"""Chart:
  Offset: {self.offset}
  Resolution: {self.resolution}
  Player2: {self.player2}
  Difficulty: {self.difficulty}
  Preview Start: {self.preview_start}
  Preview End: {self.preview_end}
  Genre: {self.genre}
  Media Type: {self.media_type}
  Music Stream: {self.music_stream}
  Note count: {len(self.notes)}"""


def _sanitize_token(token):
    token = token.strip('"')
    token = _try_f(int, token)
    return token


def _try_f(f, x):
    try:
        if isinstance(x, list) or isinstance(x, tuple):
            return f(*x)
        else:
            return f(x)
    except:
        return x


def round_to_nearest_multiple(x, multiple):
    return multiple * round(x/multiple)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("need at least 2 args")
        sys.exit(1)
