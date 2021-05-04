import pickle
from collections import deque
from typing import List, Optional, Tuple, Deque

from mido import MidiFile, MidiTrack, Message

from project.algorithms.core import constants
from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.note import Note
from project.algorithms.graph_based.signature import TimeSignature, KeySignature
from project.algorithms.core.midtools import get_track_signatures, get_track_non_note_messages, transpose_keysig_down, \
    transpose_keysig_up


class NoteSegment(MidiSegment):

    def __init__(self, file: MidiFile, melody_track_ind: int, notes: List[Note], chord_track_ind: Optional[int] = None):
        """
        A NoteSegment is a derived class of MidiSegment. It represents part of a MIDI file as a list of musical notes.

        Args:
            file: the MIDI file this segment is taken from
            melody_track_ind: the index of track the melody of the MIDI are contained in
            notes: A list of notes derived from the MIDI file in some way (not necessarily straight from the file, could be a reduction)
            chord_track_ind: the index of the track the chords of the MIDI file are contained in, if it exists
        """
        super().__init__(file, melody_track_ind)
        self.notes = notes
        self.chord_track_ind = chord_track_ind
        # precompute time and key signatures
        self.time_signature_events, self.key_signature_events = get_track_signatures(file.tracks[melody_track_ind])
        self.duration_transform = 1
        self.transpose_amount = 0

    @property
    def start_time(self) -> Optional[float]:
        """
        Return the start time of the segment, defined as the onset of the first note

        Returns:
            None if this segment contains no notes, otherwise the onset of the first note is returned
        """
        if len(self.notes) > 0:
            return self.notes[0].start_time
        else:
            return None

    @property
    def end_time(self) -> Optional[float]:
        """
        Return the end time of the segment, defined as the offset of the last note

        Returns:
            None if this segment contains no notes, otherwise the offset of the last note is returned
        """
        if len(self.notes) > 0:
            return self.notes[-1].end_time
        else:
            return None

    @property
    def _chord_track(self) -> Optional[MidiTrack]:
        """
        Return a MidiTrack which contains the chords of this NoteSegment. Returns None if no chords exist.

        Returns:
            None if this segment has no chords associated with it, otherwise the MidiTrack from which the chords were derived is returned.
        """
        if self.chord_track_ind is None:
            return None
        else:
            return self._file.tracks[self.chord_track_ind]

    def _get_chord_non_note_messages(self) -> Deque[Tuple[int, Message]]:
        """
        Gets the non-note messages from the chord track. This is the same as _get_melody_non_note_messages, except
        for the chord track (if it exists)

        Returns:
           A Deque containing messages relevant for saving this segment (with chords) as a MIDI file.
        """
        if self._chord_track is None:
            return deque()
        else:
            return get_track_non_note_messages(self._chord_track)

    def copy_notes_to_track(self, track: MidiTrack):
        """
        Add all the notes in this NoteSegment to a new MidiTrack `track`.

        Args:
            track: The track to add the notes (in message form) to.
        """
        non_note_message_queue = self._get_melody_non_note_messages()
        temp_queue = deque()
        for time, msg in non_note_message_queue:
            if msg.type == "key_signature":
                transposed_msg = msg
                for i in range(abs(self.transpose_amount)):
                    if self.transpose_amount < 0:
                        transposed_msg = transpose_keysig_down(transposed_msg)
                    else:
                        transposed_msg = transpose_keysig_up(transposed_msg)

                temp_queue.append((int(time * self.duration_transform), transposed_msg))
            else:
                temp_queue.append((int(time * self.duration_transform), msg))

        non_note_message_queue = temp_queue

        # add the list of notes within the core as Midi messages
        current_meta_index = 0
        current_time = self.start_time
        for (index, note) in enumerate(self.notes):
            note.start_time = int(note.start_time * self.duration_transform)
            note.end_time = int(note.end_time * self.duration_transform)
            # add meta messages at the appropriate time
            if len(non_note_message_queue) > 0 and non_note_message_queue[0][0] <= current_time:
                while len(non_note_message_queue) > 0 and non_note_message_queue[0][0] <= current_time:
                    track.append(non_note_message_queue.popleft()[1])

            time_since_last_note = note.start_time - self.notes[index - 1].end_time if index != 0 else 0
            track.append(Message(type="note_on", note=note.pitch, velocity=127, channel=note.channel,
                                 time=time_since_last_note))
            current_time += time_since_last_note

            if len(non_note_message_queue) > 0 and non_note_message_queue[0][0] <= current_time:
                while len(non_note_message_queue) > 0 and non_note_message_queue[0][0] <= current_time:
                    track.append(non_note_message_queue.popleft()[1])

            track.append(Message(type="note_on", note=note.pitch, velocity=0, channel=note.channel,
                                 time=note.duration))  # running status note off
            current_time += note.duration
        # add remaining meta messages
        while len(non_note_message_queue) > 0:
            track.append(non_note_message_queue.popleft()[1])

    def copy_chords_to_track(self, track: MidiTrack):
        """
        Copy the list of chords in this NoteSegment to the MidiTrack track. If there are no chords, the track is
        not modified.

        Args:
            track: the track to add the chords to.

        """
        if self._chord_track is None:
            return
        else:
            non_note_message_queue = self._get_chord_non_note_messages()

            temp_queue = deque()
            for time, msg in non_note_message_queue:
                if msg.type != "key_signature":
                    temp_queue.append((int(time * self.duration_transform), msg))
                else:
                    new_msg = msg
                    for i in range(abs(self.transpose_amount)):
                        if self.transpose_amount < 0:
                            new_msg = transpose_keysig_down(msg)
                        else:
                            new_msg = transpose_keysig_up(msg)

            non_note_message_queue = temp_queue

            current_meta_index = 0
            current_time = self.start_time
            for (index, note) in enumerate(self.notes):
                # add meta messages at the appropriate time
                if len(non_note_message_queue) > 0 and non_note_message_queue[0][0] <= current_time:
                    while len(non_note_message_queue) > 0 and non_note_message_queue[0][0] <= current_time:
                        track.append(non_note_message_queue.popleft()[1])

                time_since_last_note = note.start_time - self.notes[index - 1].end_time if index != 0 else 0

                midi_values = note.chord.to_midi_values() if note.chord is not None else []
                if len(midi_values) > 0:
                    track.append(Message(type="note_on", note=midi_values[0], velocity=127, channel=note.channel,
                                         time=time_since_last_note))
                    for chord_pitch in midi_values[1:]:
                        track.append(Message(type="note_on", note=chord_pitch, velocity=127, channel=note.channel,
                                             time=0))

                current_time += time_since_last_note

                if len(non_note_message_queue) > 0 and non_note_message_queue[0][0] <= current_time:
                    while len(non_note_message_queue) > 0 and non_note_message_queue[0][0] <= current_time:
                        track.append(non_note_message_queue.popleft()[1])

                if len(midi_values) > 0:
                    track.append(Message(type="note_on", note=midi_values[0], velocity=0, channel=note.channel,
                                         time=note.duration))  # running status note off
                    for chord_pitch in midi_values[1:]:
                        track.append(Message(type="note_on", note=chord_pitch, velocity=0, channel=note.channel,
                                             time=0))

                current_time += note.duration
            # add remaining meta messages
            while len(non_note_message_queue) > 0:
                track.append(non_note_message_queue.popleft()[1])

    def __get_time_signature_at(self, tick_time: int) -> Tuple[int, TimeSignature]:
        """
        Returns what the time signature is at the given time in ticks

        Args:
            tick_time: The time in ticks at which to query the time signature

        Returns:
            A (time, time_sig) pair consisting of the last time signature, and the time this time signature was changed.
        """
        last_time_sig_event = 0, TimeSignature.default()
        for time_sig_time, time_sig_value in self.time_signature_events:
            if time_sig_time <= tick_time:
                last_time_sig_event = time_sig_time, time_sig_value
            else:
                break
        return last_time_sig_event

    def __get_key_signature_at(self, tick_time: int) -> KeySignature:
        """
        Returns what the key signature is at the given time in ticks

        Args:
            tick_time: The time in ticks at which to query the key signature

        Returns:
            A (time, key_sig) pair consisting of the last key signature, and the time this key signature was changed.
        """
        last_key_sig = KeySignature.default()
        for key_sig_time, key_sig_value in self.key_signature_events:
            if key_sig_time <= tick_time:
                last_key_sig = key_sig_value
            else:
                break
        return last_key_sig

    def get_number_of_notes(self):
        """
        Get the number of notes within this NoteSegment. This gives the exact same value as len(NoteSegment)

        Returns:
            The amount of notes within this NoteSegment
        """
        return len(self.notes)

    def get_mean_pitch(self) -> float:
        """
        Returns the mean pitch value of this segment as a floating point value

        Returns:
            the mean pitch value of this segment
        """
        if len(self.notes) == 0:
            return 0
        else:
            return sum([note.pitch for note in self.notes]) / len(self.notes)

    def find_shortest_note_length(self) -> Optional[int]:
        """
        Returns the shortest length note in this NoteSegment, or None if there are no notes.

        Returns:
            None if there are no notes present, else the note with the shortest length/duration
        """
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
        """
        Save the notes in this segment as a complete MIDI file. The metadata of this new MIDI file is exactly the same
        as the file this segment originally came from

        Args:
            filepath: The filepath to save the new MidiFile to.
        """
        # create new MidiFile with the same metadata
        new_file = MidiFile(**self.get_file_metadata())

        # add all the meta messages (e.g. time signature, instrument)
        new_track = new_file.add_track(self._melody_track.name)
        self.copy_notes_to_track(new_track)
        if self._chord_track is not None:
            new_chord_track = new_file.add_track(self._chord_track.name)
            self.copy_chords_to_track(new_chord_track)
        new_file.save(filename=filepath)

    def save_segment(self, filepath):
        """
        Save this segment as a python ``pickle`` to the given filepath

        Args:
            filepath: the filepath to save the segment to
        """
        with open(filepath, "wb") as fh:
            pickle.dump(self, fh, pickle.HIGHEST_PROTOCOL)

    def reduce_segment(self, window_size: int = -1) -> Tuple[int, 'NoteSegment']:
        """
        Reduce this segment to a simpler version by looking at up to 2 notes within a sliding time window, deleting
        the least relevant one, and then assigning its duration to the more relevant one. The relevance of notes is
        decided by three scores:\n
        * Metrical: position of each note within their musical bars.
        * Consonance (requires chords): interval between the note and it's underlying chord
        * Functional (requires chords): interval between a note's underlying chord and the key signature

        Args:
            window_size: The size of the note window in ticks. If left to the default, the window size is 2x the shortest note length.

        Returns:
            A new reduced segment based on the above rules. If there are only 0 or 1 notes in this note segment, returns a new, identical segment.
        """
        if self.get_number_of_notes() < 2:
            return 1, NoteSegment(self._file, self.melody_track_ind, self.notes)

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
            window_notes = self.get_notes_in_time_range(int(start_position), window_size)

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
                    time_sig_time, time_sig_value = self.__get_time_signature_at(int(note.start_time))
                    key_sig_value = self.__get_key_signature_at(int(note.start_time))

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

        return weight, NoteSegment(self._file, self.melody_track_ind, reduced_notes)

    def transpose(self, transpose_pitch: int):
        """
        Move all notes ( and chords if they exist) in this segment up or down by ``transpose_pitch``

        Args:
            transpose_pitch: The amount to move each note up or down pitchwise
        """
        self.transpose_amount += transpose_pitch
        for note in self.notes:
            note.pitch += transpose_pitch
            if note.chord is not None:
                note.chord.transpose(transpose_pitch)

    def change_duration_transform(self, factor: float = 1):
        """
        Scale each note by a constant factor. Note: only works with factors > 1.

        Args:
            factor: The amount to change the duration of each note by

        """
        self.duration_transform = factor

    def add_note(self, pitch: int, tick_length: int, index: int):
        """
        Add a note at the specified index, with pitch ``pitch`` and length ``tick_length``

        Args:
            pitch: The pitch of the note to add
            tick_length: the length (in ticks) of the note to add
            index: the index at which to place this new note

        """
        # change note start & end times after this new note to take it into account
        if index < len(self.notes):
            for note in self.notes[index:]:
                note.start_time += tick_length
                note.end_time += tick_length
            self.notes.insert(index, Note(int(self.notes[index].start_time - tick_length),
                                          int(self.notes[index].end_time - tick_length),
                                          pitch, self.notes[index].channel, self.notes[index].chord))

    def remove_note(self, index: int):
        """
        Remove the note from the specified index. If this index isn't valid the method does nothing.

        Args:
            index: The index of the note to remove
        """
        if index in range(len(self.notes)):
            del self.notes[index]

    def __str__(self):
        return str(self.__dict__)

    def __len__(self):
        """
        Return the number of notes in this NoteSegment

        Returns:
            The number of notes within this NoteSegment
        """
        return self.get_number_of_notes()
