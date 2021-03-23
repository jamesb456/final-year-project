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
        if note in constants.TWELVE_NOTE_SCALE:
            self.note = constants.TWELVE_NOTE_SCALE.index(note)
        elif note in constants.TWELVE_NOTE_SCALE_FLAT:
            self.note = constants.TWELVE_NOTE_SCALE_FLAT.index(note)
        else:
            raise ValueError(f"Error: note ''{note}'' could not be parsed into a pitch number"
                             f"when trying to create a valid key signature ")

        self.minor = minor

    @staticmethod
    def default():
        return KeySignature("C", False)

    def __repr__(self):
        return "{} {}".format(constants.TWELVE_NOTE_SCALE[self.note], "minor" if self.minor else "major")
