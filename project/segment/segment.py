from typing import List, Optional, Tuple

from mido import MidiFile, MidiTrack, Message, MetaMessage

from project.segment.note import Note


class Segment:
    def __init__(self, file: MidiFile, melody_track_ind: int, notes: List[Note]):
        self.file = file  # source track
        self.notes = notes
        self.melody_track_ind = melody_track_ind

    @property
    def __melody_track(self) -> MidiTrack:
        return self.file.tracks[self.melody_track_ind]

    @property
    def start_time(self) -> Optional[int]:
        if len(self.notes) > 0:
            return self.notes[0].start_time
        else:
            return None

    @property
    def end_time(self) -> Optional[int]:
        if len(self.notes) > 0:
            return self.notes[-1].end_time
        else:
            return None

    def get_number_of_notes(self):
        return len(self.notes)

    def find_shortest_note_length(self) -> Optional[int]:
        return min([note.duration for note in self.notes], default=None)

    def get_notes_in_time_range(self, range_start: int, range_length: int) -> List[Note]:
        """
        Gets a list of notes who's onset times fall within the range [range_start,range_start + range_length)
        Args:
            range_start: The start of the range
            range_length: The end of the range

        Returns:
            A list of notes who's onset time's occur within the range [range_start,range_start + range_length)
        """
        return [note for note in self.notes if (range_start <= note.start_time < range_start + range_length)]

    def save_segment(self, filepath):
        # create new MidiFile with the same metadata
        new_file = MidiFile(type=self.file.type, ticks_per_beat=self.file.ticks_per_beat, charset=self.file.charset,
                            debug=self.file.debug, clip=self.file.clip)

        # add all the meta messages (e.g. time signature, instrument)
        new_track = new_file.add_track(self.__melody_track.name)
        self.copy_notes_to_track(new_track)
        new_file.save(filename=filepath)

    def copy_notes_to_track(self, track: MidiTrack):
        track.extend([message for message in self.__melody_track
                      if (message.is_meta and message.type != "end_of_track")
                      or message.type == "control_change" or message.type == "program_change"])
        # add the list of notes within the segment as Midi messages
        for (index, note) in enumerate(self.notes):
            # TODO: add velocity into note definition?
            track.append(Message(type="note_on", note=note.pitch, velocity=127, channel=note.channel,
                                 time=note.start_time - self.notes[index - 1].end_time if index != 0 else 0))
            track.append(Message(type="note_on", note=note.pitch, velocity=0, channel=note.channel,
                                 time=note.duration))  # running status note off

        # TODO: end of track at same offset as in the source track
        track.append(MetaMessage(type="end_of_track", time=0))
