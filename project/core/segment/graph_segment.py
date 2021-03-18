from typing import List, Optional, Tuple

from mido import MidiFile, MidiTrack, Message

from project.core.segment.midi_segment import MidiSegment
from project.core.note import Note
from project.core.signature import TimeSignature, KeySignature
from project.util.midtools import get_track_signatures


class GraphSegment(MidiSegment):

    def __init__(self, file: MidiFile, melody_track_ind: int, notes: List[Note]):
        super().__init__(file, melody_track_ind)
        self.notes = notes
        # precompute time and key signatures
        self.time_signature_events, self.key_signature_events = get_track_signatures(file.tracks[melody_track_ind])

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

    def copy_notes_to_track(self, track: MidiTrack):

        message_queue = self._get_melody_instructional_messages()

        # add the list of notes within the core as Midi messages
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

    def __get_time_signature_at(self, time: int) -> Tuple[int, TimeSignature]:
        last_time_sig_event = 0, TimeSignature.default()
        for time_sig_time, time_sig_value in self.time_signature_events:
            if time_sig_time <= time:
                last_time_sig_event = time_sig_time, time_sig_value
            else:
                break
        return last_time_sig_event

    def __get_key_signature_at(self, time: int) -> KeySignature:
        last_key_sig = KeySignature.default()
        for key_sig_time, key_sig_value in self.key_signature_events:
            if key_sig_time <= time:
                last_key_sig = key_sig_value
            else:
                break
        return last_key_sig

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

    def save_as_midi(self, filepath):
        # create new MidiFile with the same metadata
        new_file = MidiFile(**self.get_file_metadata())

        # add all the meta messages (e.g. time signature, instrument)
        new_track = new_file.add_track(self._melody_track.name)
        self.copy_notes_to_track(new_track)
        new_file.save(filename=filepath)

    def save_segment(self, filepath):
        pass

    def reduce_segment(self, window_size: int = -1) -> Tuple[int, 'GraphSegment']:
        if self.get_number_of_notes() < 2:
            return 1, GraphSegment(self._file, self.melody_track_ind, self.notes)

        reduced_notes = []

        # work out the window size
        if window_size == -1:
            # find the shortest note
            # duration of note = end - start
            shortest_note_length = self.find_shortest_note_length()

            window_size = shortest_note_length * 2

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

                for note in window_notes:
                    time_sig_time, time_sig_value = self.__get_time_signature_at(note.start_time)
                    key_sig_value = self.__get_key_signature_at(note.start_time)

                    beat_strength = note.get_metric_strength(self.ticks_per_beat, time_sig_value, time_sig_time)
                    consonance_score = note.get_consonance_score()
                    functional_score = note.get_functional_score(key_sig_value)
                    note_weights.append((beat_strength, consonance_score, functional_score))

                # determine which note was more relevant (and find it's index)
                strongest_index = 0
                strongest_total = 0
                strongest_beat = 0
                strongest_consonance = 0
                strongest_functional = 0
                prev_strongest_total = 0

                # determine the index of the note with the strongest weight
                # in case of a tie, first consider the one on the stronger beat,
                # then the one with the stronger note consonance.
                # If they are still tied, just keep the earlier note
                for index, (beat, consonance, functional) in enumerate(note_weights):
                    if beat + consonance + functional > strongest_total:
                        prev_strongest_total = strongest_total
                        strongest_total = beat + consonance + functional
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

                # weight graph based on the mean of the consonance/functional/metric score total
                # in the paper this is called the *semantic* distance measure
                weight += ((strongest_total - prev_strongest_total) / 3)

        return weight, GraphSegment(self._file, self.melody_track_ind, reduced_notes)


