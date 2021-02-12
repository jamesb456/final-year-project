import operator
from typing import Tuple
from math import floor

from project.segment.note import Note
from project.segment.segment import Segment
from project.util.midtools import get_track_time_signatures

beat_strength_dict = {
    (4, 4): [0.5, 0.1, 0.3, 0.1],
    (3, 4): [0.66, 0.17, 0.17],
    (2, 4): [0.66, 0.33],
    (3, 8): [0.66, 0.17, 0.17],
    (6, 8): [0.3, 0.1, 0.1, 0.3, 0.1, 0.1]
}

def round_to_nearest_beat(ticks: int, ticks_per_beat: int) -> int:
    min_resolution = ticks_per_beat / 8  # 32nd note / demi-semiquaver
    return int(round(ticks / min_resolution) * min_resolution)


def get_note_metric_strength(note: Note, ticks_per_beat: int, time_signature: Tuple[int,int]) -> int:
    pass


def get_beat_strength(beat_index: int, time_signature: Tuple[int, int]):

    if time_signature in beat_strength_dict.keys():
        return beat_strength_dict[time_signature][beat_index]
    else:
        if beat_index == 1:
            return 0.4
        else:
            return 0.1


def reduce_segment(segment: Segment, window_size: int = -1) -> Segment:
    if segment.get_number_of_notes() < 2:
        return Segment(segment.file, segment.melody_track_ind, list(segment.notes))

    reduced_notes = []

    # work out the window size
    if window_size == -1:
        # find the shortest note
        # duration of note = end - start
        shortest_note_length = segment.find_shortest_note_length()

        window_size = shortest_note_length * 2

    # get the times of time signature events and what the signatures are
    time_signature_events = get_track_time_signatures(segment.file.tracks[segment.melody_track_ind])
    # ignore time signatures after this point
    time_signature_events = [(deltat, time_sig) for (deltat, time_sig) in time_signature_events if deltat <= segment.start_time]

    start_position = segment.start_time
    while start_position < segment.end_time:
        window_notes = segment.get_notes_in_time_range(start_position, window_size)

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

                ticks_since_time_signature = note.start_time - time_signature_deltat
                bar_length = (segment.file.ticks_per_beat * (time_signature[0] * (4 / time_signature[1])))
                # approx beat (zero index) is the time from last signature change to current note, modulo the length
                # of one full bar. This gives the number of ticks you are through the current bar/measure. Now scale
                # in terms of beat and restrain from 0 to 3
                # TODO: look at this
                beat_index = floor((ticks_since_time_signature % bar_length) / segment.file.ticks_per_beat)
                beat_strength = get_beat_strength(beat_index, time_signature)
                note_weights.append(beat_strength)

            # determine which note was more relevant
            index, weight = max(enumerate(note_weights), key=operator.itemgetter(1)) # get max note weight and index

            # use weight in graph later
            new_note = Note(start_position, window_notes[-1].end_time,
                            window_notes[index].pitch, window_notes[index].channel, window_notes[index].chord)
            # we don't care about start_message_index, end_message_index because it's no longer from a track
            reduced_notes.append(new_note)
            start_position += new_note.duration

    return Segment(segment.file, segment.melody_track_ind, reduced_notes)
