import pathlib
from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, Tuple, Optional

from mido import MidiFile, MidiTrack, Message

from project.algorithms.core.midtools import get_track_non_note_messages

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

    @property
    def filename(self) -> str:
        return str(pathlib.Path(self._file.filename).stem)

    def _get_melody_non_note_messages(self) -> Deque[Tuple[int, Message]]:
        return get_track_non_note_messages(self._melody_track)

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

    @abstractmethod
    def __len__(self):
        pass
