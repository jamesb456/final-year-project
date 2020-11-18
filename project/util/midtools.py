import math

import mido

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

def get_notes(track: mido.MidiTrack) -> List[Tuple[int,int]]:
    pass
