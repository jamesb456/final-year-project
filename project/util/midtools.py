import math, mido
import numpy as np


from typing import Dict, List, Tuple


def get_note_tally(mid: mido.MidiFile) -> Dict[int, int]:
    """Returns a dictionary containing the occurrence of each note in the MIDI file.


    Args:
        mid (mido.MidiFile): The midi object to be analysed.

    Returns:
        Dict[int,int]: A dictionary with the keys being the MIDI note numbers (0 to 127), and the values being the number of occurences of
        the particular MIDI note.
    """



    note_dict = {}
    for i in range(128):
        note_dict[i] = 0

    for track in mid.tracks:
        for msg in track:
            # TODO: change to handle note_on/note_off pairs
            if msg.type == "note_on":
                note_dict[msg.note] += 1

    return note_dict


def get_type_tally(mid: mido.MidiFile) -> Dict[str, int]:
    """Returns a dictionary containing the occurrence of each message type in the MIDI file.


    Args:
        mid (mido.MidiFile): The midi object to be analysed.

    Returns:
        Dict[str,int]: A dictionary containing a tally of each MIDI message type (how often they appear)
    """
    type_dict = {}

    for track in mid.tracks:
        for msg in track:
            # TODO: change to handle note_on/note_off pairs
            if msg.type in type_dict:
                type_dict[msg.type] += 1
            else:
                type_dict[msg.type] = 1
    return type_dict


def number_to_scientific_pitch(num: int) -> str:
    """Converts a MIDI note number (in the range of 0 to 127) to a pitch in
    'scientific pitch notation'. This is comprised of the equivalent note from
    the 12-note scale (C, D# etc.) and the octave. Note 60 (C4) represents Middle C.

    If the number is outside of the range of MIDI note numbers (0 to 127), the number itself is
    returned (as a string)

    Args:
        num (int): The MIDI note number to be converted

    Returns:
        str: The note in scientific pitch notation if num is between 0 and 127 (inclusive both ends), or a
        string representation of num if not.
    """

    scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    if num < 0 or num > 127:
        return str(num)
    else:
        return scale[num % 12] + str(math.floor((num - 12) / 12.0))


def get_note_timeline(track: mido.MidiTrack) -> np.ndarray:
    """
    Returns a list of tuples, each of which represents a note in the source MIDI track. The tuples contain:

    1. The start time of the note (in ticks)
    2. The end time of the note (in ticks)
    3. The note value being played
    4. The index of the note off message within ``track``

    Args:
        track: A track from a MIDI file

    Returns:
        A list of tuples describing the notes in the MIDI track and when they are played.

    """
    notes = []
    note_offs = []
    curr_time = 0
    for i in range(len(track)):
        if track[i].type == "note_on" and track[i].velocity != 0:
            # start of new note being played
            notes.append(np.array((curr_time + track[i].time, -1, track[i].note, -1)))
            # notes.append((curr_time + track[i].time, track[i].note))
        elif track[i].type == "note_off" or (track[i].type == "note_on" and track[i].velocity == 0):
            # note off (inc note on "running status")
            # naive: assume the previous note_on message was the one this note_off corresponds to
            # (not necessarily the case in polyphonic music)
            notes[-1][1] = curr_time + track[i].time # set the last note's end time
            notes[-1][3] = i
        curr_time += track[i].time

    return np.array(notes)


