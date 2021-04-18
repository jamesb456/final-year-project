from typing import List, Optional

from mido import MidiFile, MidiTrack, bpm2tempo, tick2second

import numpy as np

from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.midtools import is_note_on, get_notes_in_time_range, get_note_timeline
from project.algorithms.core.note import Note
from project.algorithms.core.note_segment import NoteSegment
from project.algorithms.core.segmenter import Segmenter


class RandomSegmenter(Segmenter):
    def __init__(self, seed: Optional[int], min_length: float = 1, max_length: float = 2):
        self.min_length = min_length
        self.max_length = max_length
        self.seed = seed
        super().__init__()

    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[MidiSegment]:
        track: MidiTrack = mid.tracks[track_index]
        chord_track_ind = kwargs["chord_track"]
        if chord_track_ind is not None:
            chord_track = mid.tracks[chord_track_ind]
        else:
            chord_track = None
        time_segments = []
        delta_t = 0
        tempo = bpm2tempo(120)
        if self.seed is not None:
            rand: np.random.Generator = np.random.default_rng(int(self.seed))
        else:
            rand: np.random.Generator = np.random.default_rng()

        lengths: np.ndarray = (rand.random(len(track)) * (self.max_length - self.min_length)) + self.min_length
        for i, msg in enumerate(track):
            delta_t += tick2second(msg.time, mid.ticks_per_beat, tempo)
            if is_note_on(msg):
                notes = get_notes_in_time_range(track, mid.ticks_per_beat, delta_t, delta_t + lengths[i],
                                                allow_smaller=False, use_midi_times=True, chord_track=chord_track)
                if len(notes) > 0:
                    time_segments.append(NoteSegment(mid, track_index, notes, chord_track_ind=chord_track_ind))
            elif msg.type == "set_tempo":
                tempo = msg.tempo

        return time_segments
