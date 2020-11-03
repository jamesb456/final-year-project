import glob
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mido

import project.util.midinfo as mi

scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def number_to_scientific_pitch(num: int) -> str:
    """Converts a MIDI note number (in the range of 0 to 127) to a pitch in
    'scientific pitch notation'. This is comprised of the equivalent note from
    the 12-note scale (C, D# etc.) and the octave. Note 60 (C4) represents Middle C.

    If the number is outside of the range of MIDI note numbers (0 to 127), the number itself is
    returned (as a string)

    Args:
        num (int): The MIDI note number to be converted

    Returns:
        str: The note in scientific pitch notation if num is between 0 and 127 (inclusive both ends), or a
        string representation of num if not.
    """
    if num < 0 or num > 127:
        return str(num)
    else:
        return scale[num % 12] + str(math.floor((num - 12) / 12.0))


def view_midi_information():
    # get all MIDI files in directory
    midi_files = glob.glob("mid/*.mid")
    print(f"Input MIDI files: {midi_files}")

    plt.style.use("fivethirtyeight")
    fig, axes = plt.subplots(len(midi_files), 1)

    for (i, midi_file) in enumerate(midi_files):
        mid = mido.MidiFile(midi_file)
        print(f"MIDI file information for {mid.filename}")
        print(f"\tTicks per beat: {mid.ticks_per_beat}")
        print(f"""\tMIDI Type: {mid.type}
        (0 = single track
        1 = multi track
        2 = asynchronous)""")

        type_dict = mi.get_type_tally(mid)
        note_dict = mi.get_note_tally(mid)
        print(f"\tType dictionary: {type_dict}")

        axes[i].set_title(f"Note distribution ({mid.filename})")

        axes[i].bar(note_dict.keys(), note_dict.values())
        axes[i].set_xlim(0, 127)
        axes[i].set_xticks(range(0, 128))
        axes[i].set_xticklabels(map(number_to_scientific_pitch, range(0, 128)))

        axes[i].xaxis.set_major_locator(ticker.MultipleLocator(12.0))

    plt.show()
