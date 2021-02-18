import project.util.constants as constants


class Chord:
    def __init__(self, root_tone: int, inversion: int = 0):
        self.root_tone = root_tone
        self.inversion = inversion

    @staticmethod
    def from_midi_values(*midi_notes: int) -> 'Chord':
        # super simple atm, just take the root note as the chord
        # normalized_chord = sorted([note - min(midi_notes) for note in midi_notes])
        return Chord(midi_notes[0] % constants.OCTAVE_SEMITONE_COUNT, 0)

    def __str__(self):
        return constants.TWELVE_NOTE_SCALE[self.root_tone]

    def __repr__(self):
        return self.__str__()
