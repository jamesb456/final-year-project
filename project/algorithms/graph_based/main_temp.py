# test for structure:

# general procedure

# 1.) segment each voice / track
# 2.) reduce each segment
# 3.) make links between segments
# 4.) repeat steps 2-3 until each segment contains one note

import numpy as np
import matplotlib.pyplot as plt
from mido import MidiTrack, MidiFile
from project.segment import lbdm


def example(track: MidiTrack, ticks_per_beat: int):
    profile, _ = lbdm.lbdm(track)
    # profile contains values [0,1], though not necessarily always going up to 1.

    # some determination of the correct threshold given the lbdm profile. for simplicity here
    # we use a fixed threshold
    threshold = 0.5

    segmentation_indices = []
    for tuple_ind, boundary_strength in np.ndenumerate(profile):
        if boundary_strength > threshold:
            segmentation_indices.append(tuple_ind[0])

    # form segments: create separate tracks for each of them??
    # or use separate class ?
    print(segmentation_indices)
    print(profile)
    plt.style.use("fivethirtyeight")
    plt.plot(profile)
    plt.show()

    segment_tracks = []
    start_index = 0
    for i, seg_index in enumerate(segmentation_indices):

        seg_track = MidiTrack()
        # create a separate track for this segment
        seg_track.extend(track[start_index:segmentation_indices[i]+1])
        segment_tracks.append(seg_track)
        start_index = segmentation_indices[i] + 1

    for i, track in enumerate(segment_tracks):
        track_file = MidiFile(ticks_per_beat=ticks_per_beat)
        track_file.tracks.append(track)
        track_file.save(filename=f"../../../mid/generated/segment_{i}.mid")


if __name__ == '__main__':
    mid = MidiFile("../../../mid/ashover13.mid")

    example(mid.tracks[0], mid.ticks_per_beat)
