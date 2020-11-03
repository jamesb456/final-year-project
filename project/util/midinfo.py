import mido

from typing import Dict


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
