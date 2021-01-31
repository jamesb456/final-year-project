import mido
from typing import Callable, Tuple
import numpy as np


from project.util.midtools import get_note_timeline


def default_change(x1: int, x2: int) -> float:
    if x1 == 0 and x2 == 0:
        return 0
    else:
        return abs(x1 - x2) / (x1 + x2)


def normalize(arr: np.array) -> np.array:
    if len(arr) == 0:
        return arr
    else:
        return arr / np.max(arr)


def lbdm(track: mido.MidiTrack, pitch_weight: float = 0.25, ioi_weight: float = 0.5, rest_weight: float = 0.25
         , degree_of_change: Callable[[int, int], float] = default_change) \
        -> Tuple[np.ndarray, np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Creates a list of boundaries for the target MIDI track using the Local Boundary Detection Model.
    It looks at the intervals between notes in terms of pitch, inter-onsets (between the starts of notes pressing down)
    and rests (diff between offset to onset) to find the places where these differ significantly from the intervals
    before it. The boundaries are weighted : by default, the inter-onset intervals are weighted to be twice as important
    as the other intervals. These boundaries are normalised to between 0 and 1 inclusive.

    Notes:
        This method currently only takes into account note_on and note_off messages within the MidiTrack. Other messages
        that may have an effect on timing and pitch (e.g. sustain pedal, pitchwheel, tempo) are not currently taken into
        account.
    Args:
        track: The MIDI track to produce boundaries for
        pitch_weight: The relative importance of pitches in determining where boundaries are placed
        ioi_weight: The relative importance of inter-onset intervals in determining where boundaries are placed
        rest_weight: The relative importance of rests in determining where boundaries are placed
        degree_of_change: A function to calculate the relative difference between two intervals
    Returns:
        A boundary strength profile describing the places in which the music changes

    """

    # get only note_on / note_off events

    notes = get_note_timeline(track)

    pitches = []
    interonsets = []
    rests = []

    # create parametric profile
    for i in range(1, len(notes)):
        pitches.append(abs(notes[i][2] - notes[i - 1][2]))
        interonsets.append(notes[i][0] - notes[i - 1][0])
        rests.append(notes[i][0] - notes[i - 1][1])  # new onset - old offset
        # here we assume that when the note off event is sent, the note will immediately stop playing
        # what this actually sounds like (e.g. the note decreases in volume for a predetermined time)
        # is up to the configuration of the MIDI device playing the MIDI file

    sequence_pitches = []
    sequence_iois = []
    sequence_rests = []

    # determine the change between intervals
    for i in range(len(pitches)):
        prev_pitch = 0
        prev_ioi = 0
        prev_rest = 0

        next_pitch = 0
        next_ioi = 0
        next_rest = 0

        if i != 0:
            prev_pitch = pitches[i - 1]
            prev_ioi = interonsets[i - 1]
            prev_rest = rests[i - 1]
        if i < len(pitches) - 1:
            next_pitch = pitches[i + 1]
            next_ioi = interonsets[i + 1]
            next_rest = rests[i + 1]

        sequence_pitches.append((pitches[i] *
                                (degree_of_change(prev_pitch, pitches[i])
                                + (degree_of_change(pitches[i], next_pitch)))) + 1)

        sequence_iois.append((interonsets[i] *
                             (degree_of_change(prev_ioi, interonsets[i])
                             + (degree_of_change(interonsets[i], next_ioi)))) + 1)

        sequence_rests.append((rests[i] *
                              (degree_of_change(prev_rest, rests[i])
                              + (degree_of_change(rests[i], next_rest)))) + 1)

    # normalise to range [0,1]
    sequence_pitches = normalize(np.array(sequence_pitches))
    sequence_iois = normalize(np.array(sequence_iois))
    sequence_rests = normalize(np.array(sequence_rests))

    sequence_profile = (sequence_pitches * pitch_weight) + (sequence_iois * ioi_weight) + (sequence_rests * rest_weight)
    return sequence_profile, notes[:, 3], (sequence_pitches, sequence_iois, sequence_rests)


