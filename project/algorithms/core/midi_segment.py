import pathlib
from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, Tuple, Optional

from mido import MidiFile, MidiTrack, Message

from project.algorithms.core.midtools import get_track_non_note_messages


class MidiSegment(ABC):

    def __init__(self, file: MidiFile, melody_track_ind: int):
        """
        Represents a subsection of a MIDI file. This is an *abstract* class and must be inherited to be useful.

        Args:
            file: The MIDI file the segment comes from
            melody_track_ind: The index of the track containing the *melody* line of the MIDI file.
        """
        self._file = file  # source track
        self.melody_track_ind = melody_track_ind

    @property
    def _melody_track(self) -> MidiTrack:
        """
        Returns the MIDI track containing the melody of the MIDI file

        Returns:
            the MIDI track containing the melody of the MIDI file
        """
        return self._file.tracks[self.melody_track_ind]

    @property
    def ticks_per_beat(self) -> int:
        """
        Returns the *ticks_per_beat* of the MIDI file this segment is taken from.
        This quantity tells you how many MIDI time units, called ticks,
        make up one musical beat. The speed of each beat is given by messages in each MIDI track.

        Returns:
            The ticks_per_beat of the MIDI file

        """
        return self._file.ticks_per_beat

    @property
    def filename(self) -> str:
        """
        Return the filename of the MIDI file this segment is from, without the directory or file extension.

        Returns:
                The filename of the MIDI file this segment is from
        """
        return str(pathlib.Path(self._file.filename).stem)

    def _get_melody_non_note_messages(self) -> Deque[Tuple[int, Message]]:
        """
        Returns a double ended queue containing the messages relevant for saving MIDI files  (other than the
        actual notes). This means any `MetaMessage`, as well as `control_change` and `program_change` messages. These
        messages correspond to things like instrument choice, key signature, tempo etc.
        Returns:
            A Deque containing messages relevant for saving this segment as a MIDI file.
        """
        return get_track_non_note_messages(self._melody_track)

    def get_file_metadata(self):
        """
            Returns a dictionary containing the MIDI file's metadata. This method exists to make it easy to create
            a new MIDI file with the same MIDI data e.g. m = MidiFile(**midi_segment.get_file_metadata())

        Returns:
            a dictionary containing the MIDI file's metadata
        """
        return {
            "type": self._file.type,
            "ticks_per_beat": self._file.ticks_per_beat,
            "charset": self._file.charset,
            "debug": self._file.debug,
            "clip": self._file.clip
        }

    def save_as_midi(self, filepath):
        """
        Save this segment as a MIDI file. This method is optional to implement.
        Args:
            filepath: The path to save the MIDI file at.
        """
        pass

    def copy_notes_to_track(self, track: MidiTrack):
        """
        Add the notes represented by this MIDI segment to a MidiTrack. This method is optional to implement

        Args:
            track: the track to copy the notes to.
        """
        pass

    @abstractmethod
    def save_segment(self, filepath):
        """
        Serialize this segment to disk at the desired filepath

        Args:
            filepath: Where to serialize the segment to

        """
        pass

    @abstractmethod
    def __len__(self):
        """
        Returns the number of `elements` within this MIDI segment.

        Returns:
            the number of `elements` (whatever that means for the concrete implementation) for this segment
        """
        pass
