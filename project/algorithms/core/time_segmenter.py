from typing import List

from mido import MidiFile, MidiTrack, bpm2tempo, tick2second

from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.midtools import is_note_on, get_notes_in_time_range, get_note_timeline
from project.algorithms.core.note import Note
from project.algorithms.core.note_segment import NoteSegment
from project.algorithms.core.segmenter import Segmenter


class TimeSegmenter(Segmenter):
    def __init__(self, time: float):
        self.time = time
        super().__init__()

    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[MidiSegment]:
        track: MidiTrack = mid.tracks[track_index]
        time_segments = []
        delta_t = 0
        tempo = bpm2tempo(120)

        for i, msg in enumerate(track):
            delta_t += tick2second(msg.time, mid.ticks_per_beat, tempo)
            if is_note_on(msg):
                notes = get_notes_in_time_range(track, mid.ticks_per_beat, delta_t, delta_t + self.time,
                                                allow_smaller=False, use_midi_times=True)
                if len(notes) > 0:
                    time_segments.append(NoteSegment(mid, track_index, notes))
            elif msg.type == "set_tempo":
                tempo = msg.tempo

        return time_segments
