from project.util.constants import TWELVE_NOTE_SCALE


class TimeSignature:
    def __init__(self, numerator: int, denominator: int):
        self.numerator = numerator
        self.denominator = denominator


class KeySignature:
    def __init__(self, note: str, minor: bool):
        self.note = TWELVE_NOTE_SCALE.index(note)
        self.minor = minor
