from typing import List

from mido import MidiFile, MidiTrack, bpm2tempo, tick2second

from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.midtools import is_note_on, get_notes_in_time_range, get_note_timeline
from project.algorithms.core.note import Note
from project.algorithms.core.note_segment import NoteSegment
from project.algorithms.core.segmenter import Segmenter


class TimeSegmenter(Segmenter):
    def __init__(self, time: float):
        """
        A Segmenter which creates a ``NoteSegment`` for each `time` second segment of the MIDI file. A new segment is
        created at the start of each note onset if it would be long enough.

        Args:
            time: The length of the segment in seconds
        """
        self.time = time
        super().__init__()

    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[MidiSegment]:
        """
        Segment the given MidiFile, producing a ``TimeSegmenter.time`` second segment from each note onset. If the
        segment reaches the end of the track before ``TimeSegmenter.time`` seconds has been recorded, no segment is
        extracted

        Args:
            mid: The MidiFile to segment
            track_index:  track_index: The index of the track to segment with respect to
            **kwargs: Not used in this derived class

        Returns:
            A list of NoteSegments of fixed length
        """
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
