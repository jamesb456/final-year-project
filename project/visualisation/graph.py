import glob
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mido
import numpy as np

from project.algorithms.core.midtools import  get_type_tally, get_note_tally, get_note_timeline
from project.algorithms.graph_based.lbdm import lbdm


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

        type_dict = get_type_tally(mid)
        note_dict = get_note_tally(mid)
        print(f"\tType dictionary: {type_dict}")

        axes[i].set_title(f"Note distribution ({mid.filename})")

        axes[i].bar(note_dict.keys(), note_dict.values())
        axes[i].set_xlim(0, 127)
        axes[i].set_xticks(range(0, 128))

        axes[i].xaxis.set_major_locator(ticker.MultipleLocator(12.0))

    plt.show()


def pitch_time_graph(track: mido.MidiTrack, ticks_per_beat: int):

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

    plt.scatter(on_arr[:, 0] / ticks_per_beat, on_arr[:, 1], color="black", label="Note on events")
    plt.scatter(off_arr[:, 0] / ticks_per_beat, off_arr[:, 1], color="gray", label="Note off events")
    plt.plot(all_arr[:, 0] / ticks_per_beat, all_arr[:, 1], linewidth=1, color="black")
    plt.minorticks_on()

    plt.xlabel("Time elapsed (beats)")
    plt.ylabel("Note")
    plt.legend()
    plt.show()


def lbdm_graph(track: mido.MidiTrack, ticks_per_beat: int = 1024):
    # temp, ignore rests for the moment
    notes = get_note_timeline(track)
    (profile, (pitch, ioi, rest)) = lbdm(notes, max_time_difference=ticks_per_beat * 4)

    plt.style.use("fivethirtyeight")
    plt.xlabel("Note interval index")
    plt.ylabel("Boundary strength")
    plt.title("LBDM test")
    barwidth = 0.3
    plt.plot(np.array(range(len(profile))), profile, label="LBDM overall boundary strength", linewidth=2, color="purple")
    plt.bar(np.array(range(len(profile))) - barwidth, pitch, label="Pitch boundary strength", width=barwidth)
    plt.bar(np.array(range(len(profile))), ioi, label="Inter onset boundary strength", width=barwidth)
    plt.bar(np.array(range(len(profile))) + barwidth, rest, label="Rest boundary strength", width=barwidth)
    plt.tight_layout()
    plt.legend()

    plt.show()


