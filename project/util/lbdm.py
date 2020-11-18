import mido

from typing import List


def lbdm(track: mido.MidiTrack, pitch_weight: float = 0.25, ioi_weight: float = 0.5, rest_weight: float = 0.25) -> List[float]:
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
    Returns: A boundary strength profile describing the places in which the music changes

    """
    if len(track) < 2:
        return []
    # get only note_on / note_off events
    note_msgs = []
    pitches = []
    interonsets = []
    rests = []

    for i in range(len(track)):
        if track[i].type == "note_on":
            note_msgs.append(track[i])

    for j in range(1, len(note_msgs)):
        pitches.append(abs(track[j].note - track[j - 1].note))
        interonsets.append(abs(track[j].time - track[j - 1].time))



