import glob
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mido
import numpy as np
import project.util.midtools as mi
from project.util.midtools import number_to_scientific_pitch



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


def pitch_time_curve(track: mido.MidiTrack):
    note_ons = []
    note_offs = []
    all_notes = []
    curr_time = 0
    for msg in track:
        if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            # note message type , message time, message note
            note_offs.append((curr_time + msg.time, msg.note))
            all_notes.append((curr_time + msg.time, msg.note))
        elif msg.type == "note_on":
            note_ons.append((curr_time + msg.time, msg.note))
            all_notes.append((curr_time + msg.time, msg.note))

        curr_time += msg.time

    plt.style.use("fivethirtyeight")
    on_arr = np.array(note_ons)
    off_arr = np.array(note_offs)
    all_arr = np.array(all_notes)

    print(on_arr[:, 0])
    print(off_arr[:, 0])

    plt.scatter(on_arr[:, 0], on_arr[:, 1], color="black", label="Note on events")
    plt.scatter(off_arr[:, 0], off_arr[:, 1], color="gray", label="Note off events")
    plt.plot(all_arr[:, 0], all_arr[:, 1], linewidth=1, color="black")
    plt.minorticks_on()

    maj_locator = ticker.MultipleLocator(1920)

    ax = plt.gca().xaxis
    ax.set_major_locator(maj_locator)

    plt.legend()
    plt.show()
