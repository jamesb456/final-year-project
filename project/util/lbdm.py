import mido


def lbdm(track: mido.MidiTrack):
    for i in range(len(track)):
        print(track[i])


