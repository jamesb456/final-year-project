from typing import List


import numpy as np
from mido import MidiTrack, MidiFile

from project.segment import lbdm
from project.segment.segmenter import Segmenter
from project.segment.segment import Segment
from project.util.midtools import get_note_timeline


class LbdmSegmenter(Segmenter):

    def __init__(self, threshold: float = 0.5, pitch_weight: float = 0.25, ioi_weight: float = 0.5,
                 rest_weight: float = 0.25):

        super().__init__()
        self.threshold = threshold
        self.pitch_weight = pitch_weight
        self.ioi_weight = ioi_weight
        self.rest_weight = rest_weight

    def create_segments(self, mid: MidiFile) -> List[Segment]:

        # determine which track to use (temp this)
        track = mid.tracks[0]

        profile, indices, _ = lbdm.lbdm(track, pitch_weight=self.pitch_weight, ioi_weight=self.ioi_weight,
                                        rest_weight=self.rest_weight)
        # profile contains values [0,1], though not necessarily always going up to 1.
        # some determination of the correct threshold given the lbdm profile. for simplicity here
        # we use a fixed threshold

        segmentation_indices = []
        for profile_index, boundary_strength in np.ndenumerate(profile):
            if boundary_strength > self.threshold:
                segmentation_indices.append(indices[profile_index])

        start_index = -1
        tracks = []

        for seg_index in segmentation_indices:
            seg_track = MidiTrack()
            seg_track.extend(track[start_index+1:seg_index+1])
            start_index = seg_index

            tracks.append(seg_track)

        end_track = MidiTrack()
        end_track.extend(track[start_index + 1:])
        tracks.append(end_track)

        i = 0
        for tr in tracks:
            segment_mid = MidiFile(ticks_per_beat=mid.ticks_per_beat)
            segment_mid.tracks.append(tr)
            segment_mid.save(f"../../mid/generated/segment_{i}.mid")
            i += 1
