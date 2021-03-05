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

    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[Segment]:

        # determine which track to segment
        track: MidiTrack = mid.tracks[track_index]
        chord_track = None

        if "chord_track" in kwargs.keys() and kwargs["chord_track"] is not None:
            print("--chord_track specified")
            chord_track = mid.tracks[kwargs["chord_track"]]

        # get list of notes within the track
        timeline = get_note_timeline(track, chord_track)
        # get the lbdm "sequence profile" describing where segmentation should take place
        profile, _ = lbdm.lbdm(timeline, pitch_weight=self.pitch_weight, ioi_weight=self.ioi_weight,
                               rest_weight=self.rest_weight, max_time_difference=mid.ticks_per_beat * 4)
        # profile contains values [0,1], though not necessarily always going up to 1.
        # some determination of the correct threshold given the lbdm profile. for simplicity here
        # we use a fixed threshold
        segments = []
        last_segmentation_index = -1
        for profile_index, boundary_strength in np.ndenumerate(profile):
            # ignore boundary if it's within the first few notes of a piece
            if timeline[profile_index[0]].end_time < mid.ticks_per_beat * 4:
                pass
            elif boundary_strength > self.threshold:
                segments.append(Segment(mid, track_index, timeline[last_segmentation_index+1:profile_index[0]+1]))
                last_segmentation_index = profile_index[0]

        # get last few notes
        segments.append(Segment(mid, track_index, timeline[last_segmentation_index+1:]))
        return segments
