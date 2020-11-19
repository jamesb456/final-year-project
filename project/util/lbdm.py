import mido

from typing import List, Callable


def degree_of_change(x1: int, x2: int) -> float:
    if x1 == 0 and x2 == 0:
        return 0
    else:
        return abs(x1 - x2) / (x1 + x2)


def lbdm(track: mido.MidiTrack, pitch_weight: float = 0.25, ioi_weight: float = 0.5, rest_weight: float = 0.25 \
        ,change_func : Callable[[int,int],float] = degree_of_change) -> List[float]:
    """
    Creates a list of boundaries for the target MIDI track using the Local Boundary Detection Model.
    It looks at the intervals between notes in terms of pitch, inter-onsets (between the starts of notes pressing down)
    and rests (diff between offset to onset) to find the places where these differ significantly from the intervals
    before it. The boundaries are weighted : by default, the inter-onset intervals are weighted to be twice as important
    as the other intervals. These boundaries are normalised to between 0 and 1 inclusive.
    Args:
        track: The MIDI track to produce boundaries for
        pitch_weight: The relative importance of pitches in determining where boundaries are placed
        ioi_weight: The relative importance of inter-onset intervals in determining where boundaries are placed
        rest_weight: The relative importance of rests in determining where boundaries are placed
        change_func: A function to calculate the relative difference between two intervals
    Returns: A boundary strength profile describing the places in which the music changes

    """
    if len(track) < 2:
        return []
    # get only note_on / note_off events
    note_msgs = []
    pitches = []
    interonsets = []
    rests = []

    # notes: (note, start, end)

    for i in range(len(track)):
        if track[i].type == "note_on" and track[i].velocity != 0:  # ignore note off / running status note off messages
            note_msgs.append(track[i])

    for j in range(1, len(note_msgs)):
        pitches.append(abs(note_msgs[j].note - note_msgs[j - 1].note))
        interonsets.append(abs(note_msgs[j].time - note_msgs[j - 1].time))
        rests.append(0)  # temp

    print(pitches)
    print(interonsets)
    print(rests)

    pitch_sequences = []
    ioi_sequences = []
    rest_sequences = []





