import operator
from typing import List, Optional, Tuple

from mido import MidiFile, MidiTrack, Message, MetaMessage
from project.segment.note import Note


class Segment:
    def __init__(self, file: MidiFile, melody_track_ind: int, notes: List[Note]):
        self.__file = file  # source track
        self.notes = notes
        self.melody_track_ind = melody_track_ind

    @property
    def __melody_track(self) -> MidiTrack:
        return self.__file.tracks[self.melody_track_ind]

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

    @property
    def ticks_per_beat(self) -> int:
        return self.__file.ticks_per_beat

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
        new_file = MidiFile(type=self.__file.type, ticks_per_beat=self.__file.ticks_per_beat, charset=self.__file.charset,
                            debug=self.__file.debug, clip=self.__file.clip)

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

    def get_track_time_signatures(self) -> List[Tuple[int, Tuple[int, int]]]:
        time_signatures = []
        start_time = 0
        for message in self.__file.tracks[self.melody_track_ind]:
            if message.type == "time_signature":
                time_signatures.append((start_time + message.time, (message.numerator, message.denominator)))
            start_time += message.time

        return time_signatures

    def reduce_segment(self, window_size: int = -1) -> Tuple[int, 'Segment']:
        if self.get_number_of_notes() < 2:
            return 1, Segment(self.__file, self.melody_track_ind, self.notes)

        reduced_notes = []

        # work out the window size
        if window_size == -1:
            # find the shortest note
            # duration of note = end - start
            shortest_note_length = self.find_shortest_note_length()

            window_size = shortest_note_length * 2

        # get the times of time signature events and what the signatures are
        time_signature_events = self.get_track_time_signatures()
        # ignore time signatures after this point
        time_signature_events = [(deltat, time_sig) for (deltat, time_sig) in time_signature_events if
                                 deltat <= self.start_time]

        start_position = self.start_time
        while start_position < self.end_time:
            window_notes = self.get_notes_in_time_range(start_position, window_size)

            if len(window_notes) == 0:
                start_position += window_size
            elif len(window_notes) == 1:
                # need to cover note if there's 1 though so the whole window is occupied
                # if the note extends beyond the window, keep it at that length
                # else extend to the length of the window (either forward or backward)
                end_of_window = start_position + window_size
                end_position = 0
                if window_notes[0].end_time > end_of_window:
                    end_position = window_notes[0].end_time
                else:
                    end_position = end_of_window

                new_note = Note(start_position, end_position, window_notes[0].pitch,
                                window_notes[0].channel, window_notes[0].chord)

                reduced_notes.append(new_note)
                start_position += new_note.duration

            else:  # choose the most relevant note
                note_weights = []
                # work out the time signature (assume 4/4 that started at t=0 if not specified)
                time_sig_event = (0, (4, 4))
                if len(time_signature_events) > 1:
                    time_sig_event = time_signature_events[-1]  # choose the most recent time signature

                time_signature_deltat = time_sig_event[0]
                time_signature = time_sig_event[1]
                for note in window_notes:
                    # first look at metrical position
                    # work out which beat the note is on.
                    beat_strength = note.get_metric_strength(self.ticks_per_beat, time_signature, time_signature_deltat)

                    note_weights.append(beat_strength)

                # determine which note was more relevant (and find it's index)
                index, weight = max(enumerate(note_weights),
                                    key=operator.itemgetter(1))  # get max note weight and index

                # use weight in graph later
                new_note = Note(start_position, window_notes[-1].end_time,
                                window_notes[index].pitch, window_notes[index].channel, window_notes[index].chord)
                # we don't care about start_message_index, end_message_index because it's no longer from a track
                reduced_notes.append(new_note)
                start_position += new_note.duration

        return 1, Segment(self.__file, self.melody_track_ind, reduced_notes)

    def get_file_metadata(self):
        """

        Returns:

        """
        return {
            "type": self.__file.type,
            "ticks_per_beat": self.__file.ticks_per_beat,
            "charset": self.__file.charset,
            "debug": self.__file.debug,
            "clip": self.__file.clip
        }






