from typing import List

import numpy as np
from mido import MidiTrack, MidiFile

from project.algorithms.graph_based import lbdm
from project.algorithms.core.segmenter import Segmenter
from project.algorithms.core.note_segment import NoteSegment
from project.algorithms.core.midtools import get_note_timeline


class LbdmSegmenter(Segmenter):

    def __init__(self, threshold: float = 0.5, pitch_weight: float = 0.25, ioi_weight: float = 0.5,
                 rest_weight: float = 0.25):
        """
        A Segmenter which creates segments of music based on the LBDM algorithm (Cambouropoulos, 2001). See lbdm.py
        for how the segmentation works. In short the output of the LBDM algorithm is a boundary profile. This Segmenter
        splits the input MIDI file at places where the boundary value is > ``threshold``. LbdmClusteringSegmenter is
        similar but uses k-means clustering to determine the threshold

        Args:
            threshold: If the value of the generated boundary profile value is above this value, the MIDI is split at this boundary
            pitch_weight: The relative weight of the changes in pitch
            ioi_weight: The relative weight of the changes in onset
            rest_weight: The relative wieght of the changes in rest (offset->onset)
        """
        super().__init__()
        self.threshold = threshold
        self.pitch_weight = pitch_weight
        self.ioi_weight = ioi_weight
        self.rest_weight = rest_weight

    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[NoteSegment]:
        """
        Create Segments using the LBDM algorithm.
        Args:
            mid: The MIDI file to segment
            track_index: the track to segment with respect to

        Keyword Args:
            chord_track: a track of the MIDI file only containing chords, if such a track exists

        Returns:
            A list of NoteSegments, the size and position of which being determined by the LBDM algorithm
        """
        # determine which track to segment
        track: MidiTrack = mid.tracks[track_index]
        chord_track_ind = None
        chord_track = None
        if "chord_track" in kwargs.keys() and kwargs["chord_track"] is not None:
            chord_track_ind = kwargs["chord_track"]
            chord_track = mid.tracks[chord_track_ind]

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
                segments.append(NoteSegment(mid, track_index, timeline[last_segmentation_index + 1:profile_index[0] + 1]
                                            , chord_track_ind=chord_track_ind))
                last_segmentation_index = profile_index[0]

        # get last few notes
        segments.append(NoteSegment(mid, track_index, timeline[last_segmentation_index + 1:],
                                    chord_track_ind=chord_track_ind))
        return segments
