import operator

from collections import deque, namedtuple
from typing import List, Optional, Tuple, Deque

from mido import MidiFile, MidiTrack, Message, MetaMessage
from project.segment.note import Note
from project.segment.signature import TimeSignature, KeySignature

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

    def __get_melody_instructional_messages(self) -> Deque[Tuple[int, Message]]:
        time = 0
        meta_messages = deque()
        for message in self.__melody_track:
            if message.is_meta or message.type == "control_change" or message.type == "program_change":
                meta_messages.append((time + message.time, message))
            time += message.time

        return meta_messages

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
        new_file = MidiFile(type=self.__file.type, ticks_per_beat=self.__file.ticks_per_beat,
                            charset=self.__file.charset,
                            debug=self.__file.debug, clip=self.__file.clip)

        # add all the meta messages (e.g. time signature, instrument)
        new_track = new_file.add_track(self.__melody_track.name)
        self.copy_notes_to_track(new_track)
        new_file.save(filename=filepath)

    def copy_notes_to_track(self, track: MidiTrack):

        message_queue = self.__get_melody_instructional_messages()

        # add the list of notes within the segment as Midi messages
        current_meta_index = 0
        current_time = self.start_time
        for (index, note) in enumerate(self.notes):
            # add meta messages at the appropriate time
            if message_queue[0][0] <= current_time:
                while len(message_queue) > 0 and message_queue[0][0] <= current_time:
                    track.append(message_queue.popleft()[1])

            time_since_last_note = note.start_time - self.notes[index - 1].end_time if index != 0 else 0
            track.append(Message(type="note_on", note=note.pitch, velocity=127, channel=note.channel,
                                 time=time_since_last_note))
            current_time += time_since_last_note

            if message_queue[0][0] <= current_time:
                while len(message_queue) > 0 and message_queue[0][0] <= current_time:
                    track.append(message_queue.popleft()[1])

            track.append(Message(type="note_on", note=note.pitch, velocity=0, channel=note.channel,
                                 time=note.duration))  # running status note off
            current_time += note.duration
        # add remaining meta messages
        while len(message_queue) > 0:
            track.append(message_queue.popleft()[1])

    def get_track_signatures(self) -> Tuple[List[Tuple[int, TimeSignature]], List[Tuple[int, KeySignature]]]:
        time_signatures = []
        key_signatures = []
        start_time = 0
        for message in self.__file.tracks[self.melody_track_ind]:
            if message.type == "time_signature":
                time_signatures.append((start_time + message.time, TimeSignature(message.numerator, message.denominator)))
            elif message.type == "key_signature":
                if message.key.endswith("m"):  # is minor key
                    key_signatures.append((start_time + message.time, KeySignature(message.key[:-1], True)))
                else:
                    key_signatures.append((start_time + message.time, KeySignature(message.key, False)))
            start_time += message.time

        return time_signatures, key_signatures

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
        time_signature_events, key_signature_events = self.get_track_signatures()
        # ignore time signatures after this point
        time_signature_events = [(deltat, time_sig) for (deltat, time_sig) in time_signature_events if
                                 deltat <= self.start_time]

        weight = 0

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
                time_sig_event = (0, TimeSignature(4, 4))
                if len(time_signature_events) > 0:
                    time_sig_event = time_signature_events[-1]  # choose the most recent time signature
                key_sig_event = (0, KeySignature("C",False))
                if len(key_signature_events) > 0:
                    key_sig_event = key_signature_events[-1]

                time_signature_deltat = time_sig_event[0]
                time_signature = time_sig_event[1]

                key_signature = key_sig_event[1]

                for note in window_notes:
                    # first look at metrical position
                    # work out which beat the note is on.
                    beat_strength = note.get_metric_strength(self.ticks_per_beat, time_signature, time_signature_deltat)
                    consonance_score = note.get_consonance_score()
                    functional_score = note.get_functional_score(key_signature)
                    note_weights.append((beat_strength, consonance_score, functional_score))

                # determine which note was more relevant (and find it's index)
                strongest_index = 0
                strongest_total = 0
                strongest_beat = 0
                strongest_consonance = 0
                strongest_functional = 0

                # determine the index of the note with the strongest weight
                # in case of a tie, first consider the one on the stronger beat,
                # then the one with the stronger note consonance.
                # If they are still tied, just keep the earlier note
                for index, (beat, consonance, functional) in enumerate(note_weights):
                    if beat + consonance + functional > strongest_total:
                        strongest_total = beat + consonance
                        strongest_index = index
                        strongest_beat = beat
                        strongest_consonance = consonance
                        strongest_functional = functional
                    elif beat + consonance == strongest_total:
                        if functional > strongest_functional:
                            strongest_index = index
                            strongest_beat = beat
                            strongest_consonance = consonance
                            strongest_functional = functional
                        elif consonance > strongest_consonance:
                            strongest_index = index
                            strongest_beat = beat
                            strongest_consonance = consonance
                            strongest_functional = functional
                        elif beat > strongest_beat:
                            strongest_index = index
                            strongest_beat = beat
                            strongest_consonance = consonance
                            strongest_functional = functional

                # use weight in graph later
                new_note = Note(start_position, window_notes[-1].end_time,
                                window_notes[strongest_index].pitch, window_notes[strongest_index].channel,
                                window_notes[strongest_index].chord)
                # we don't care about start_message_index, end_message_index because it's no longer from a track
                reduced_notes.append(new_note)
                start_position += new_note.duration

                # weight graph based on the mean of the consonace/functional/metric score totoal
                # in the paper this is called the *semantic* distance measure
                weight += (strongest_total / 3)

        return weight, Segment(self.__file, self.melody_track_ind, reduced_notes)

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
