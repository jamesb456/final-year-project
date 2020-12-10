import mido

from typing import Tuple


def reduce(segment: mido.MidiTrack, time_signature: Tuple[int,int], key_signature: int, ppqn: int) -> mido.MidiTrack:
    new_segment = mido.MidiTrack()

    # work out the window size
    # base case: this is the 2x shortest note in the piece
    # where this doesn't make sense (e.g. if in 3/4 a quarter note is the shortest note, window size should equal
    # 3 quarter notes (as 2 would chop notes in half))

    # find shortest note

    return new_segment

