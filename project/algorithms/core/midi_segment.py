from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, Tuple

from mido import MidiFile, MidiTrack, Message


class MidiSegment(ABC):
    def __init__(self, file: MidiFile, melody_track_ind: int):
        self._file = file  # source track
        self.melody_track_ind = melody_track_ind

    @property
    def _melody_track(self) -> MidiTrack:
        return self._file.tracks[self.melody_track_ind]

    @property
    def ticks_per_beat(self) -> int:
        return self._file.ticks_per_beat

    def _get_melody_instructional_messages(self) -> Deque[Tuple[int, Message]]:
        time = 0
        meta_messages = deque()
        for message in self._melody_track:
            if message.is_meta or message.type == "control_change" or message.type == "program_change":
                meta_messages.append((time + message.time, message))
            time += message.time

        return meta_messages

    def get_file_metadata(self):
        """

        Returns:

        """
        return {
            "type": self._file.type,
            "ticks_per_beat": self._file.ticks_per_beat,
            "charset": self._file.charset,
            "debug": self._file.debug,
            "clip": self._file.clip
        }

    @abstractmethod
    def copy_notes_to_track(self, track: MidiTrack):
        pass

    @abstractmethod
    def save_segment(self, filepath):
        pass

    @abstractmethod
    def save_as_midi(self, filepath):
        pass
