import project.util.constants as constants

class TimeSignature:
    def __init__(self, numerator: int, denominator: int):
        self.numerator = numerator
        self.denominator = denominator

    @staticmethod
    def default():
        return TimeSignature(4, 4)

    def __repr__(self):
        return f"({self.numerator} {self.denominator})"


class KeySignature:
    def __init__(self, note: str, minor: bool):
        self.note = constants.TWELVE_NOTE_SCALE.index(note)
        self.minor = minor

    @staticmethod
    def default():
        return KeySignature("C", False)

    def __repr__(self):
        return "{} {}".format(constants.TWELVE_NOTE_SCALE[self.note], "minor" if self.minor else "major")
