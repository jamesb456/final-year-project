import project.algorithms.core.constants as constants


class TimeSignature:

    def __init__(self, numerator: int, denominator: int):
        """
        A class representing a TimeSignature in a simple way

        Args:
            numerator: The top number of a time signature
            denominator: The bottom of a time signature
        """
        self.numerator = numerator
        self.denominator = denominator

    @staticmethod
    def default():
        """
        Returns the default time signature for MIDI files (4/4)

        Returns:
             the default time signature for MIDI files (4/4)
        """
        return TimeSignature(4, 4)

    def __repr__(self):
        return f"({self.numerator} {self.denominator})"


class KeySignature:
    def __init__(self, note: str, minor: bool):
        """
        A class representing a KeySignature in a simple way. Based on a textual representation

        Args:
            note: The pitch class of the note e.g. 0 -> C 5 -> F
            minor: Whether the key signature is minor or not.
        """
        if note in constants.TWELVE_NOTE_SCALE_SHARP:
            self.note = constants.TWELVE_NOTE_SCALE_SHARP.index(note)
        elif note in constants.TWELVE_NOTE_SCALE_FLAT:
            self.note = constants.TWELVE_NOTE_SCALE_FLAT.index(note)
        else:
            raise ValueError(f"Error: note ''{note}'' could not be parsed into a pitch number"
                             f"when trying to create a valid key signature ")

        self.minor = minor

    @staticmethod
    def default():
        """
        Returns the default key signature for MIDI files (C Major)

        Returns:
             the default key signature for MIDI files (C Major)
        """
        return KeySignature("C", False)

    def __repr__(self):
        return "{} {}".format(constants.TWELVE_NOTE_SCALE_SHARP[self.note], "minor" if self.minor else "major")
