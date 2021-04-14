from enum import IntEnum

TWELVE_NOTE_SCALE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
TWELVE_NOTE_SCALE_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
BEAT_STRENGTH_DICT = {
    (4, 4): [0.5, 0.1, 0.3, 0.1],
    (3, 4): [0.66, 0.17, 0.17],
    (2, 4): [0.66, 0.34],
    (6, 4): [0.25, 0.125, 0.125, 0.25, 0.125, 0.125],
    (3, 8): [0.66, 0.17, 0.17],
    (6, 8): [0.3, 0.1, 0.1, 0.3, 0.1, 0.1],
    (9, 8): [0.17, 0.09, 0.09, 0.17, 0.09, 0.09, 0.17, 0.09, 0.09],
    (12, 8): [0.1, 0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.05],
    (2, 2): [0.66, 0.34],
    (3, 2): [0.6, 0.2, 0.2],


}


class Interval(IntEnum):
    ROOT = 0
    MIN_SECOND = 1
    MAJ_SECOND = 2
    MIN_THIRD = 3
    MAJ_THIRD = 4
    FOURTH = 5
    DIM_FIFTH = 6
    FIFTH = 7
    MIN_SIXTH = 8
    MAJ_SIXTH = 9
    SEVENTH = 10
    MAJ_SEVENTH = 11
    OCTAVE = 12
    FLAT_NINTH = 13
    NINTH = 14


CONSONANCE_SCORE_DICT = {
    Interval.ROOT: 1.0,
    Interval.MIN_SECOND: 0.2,
    Interval.MAJ_SECOND: 0.2,
    Interval.MIN_THIRD: 0.75,
    Interval.MAJ_THIRD: 0.75,
    Interval.FOURTH: 0.3,
    Interval.DIM_FIFTH: 0.5,
    Interval.FIFTH: 0.75,
    Interval.MIN_SIXTH: 0.4,
    Interval.MAJ_SIXTH: 0.4,
    Interval.SEVENTH: 0.5,
    Interval.MAJ_SEVENTH: 0.2,
}

FUNCTIONAL_SCORE_DICT = {
    Interval.ROOT: 1.0,
    Interval.MIN_SECOND: 0.2,
    Interval.MAJ_SECOND: 0.5,
    Interval.MIN_THIRD: 0.4,
    Interval.MAJ_THIRD: 0.4,
    Interval.FOURTH: 0.8,
    Interval.DIM_FIFTH: 0.3,
    Interval.FIFTH: 0.9,
    Interval.MIN_SIXTH: 0.1,
    Interval.MAJ_SIXTH: 0.6,
    Interval.SEVENTH: 0.7,
    Interval.MAJ_SEVENTH: 0.7,
}


OCTAVE_SEMITONE_COUNT = 12

TIME_FORMAT = "%Y%m%d_%I%M%S"
