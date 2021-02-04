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

    def create_segments(self, mid: MidiFile, track_index: int) -> List[Segment]:

        # determine which track to use (temp this)
        track: MidiTrack = mid.tracks[track_index]

        # timeline is a numpy array with 4 columns representing the notes in the MIDI file as follows:
        # [0] the start time in ticks of the note (the time of the "note on" event)
        # [1] the end time in ticks of the note (the time of the "note off" event)
        # [2] the pitch of the note (as a MIDI note number)
        # [3] the index in the track of the note off event of the note
        # (i.e. track[timeline[i][3]] is the corresponding  note off event)
        timeline = get_note_timeline(track)

        # get the lbdm "sequence profile" describing where segmentation should take place
        profile, _ = lbdm.lbdm(timeline, pitch_weight=self.pitch_weight, ioi_weight=self.ioi_weight,
                               rest_weight=self.rest_weight)
        # profile contains values [0,1], though not necessarily always going up to 1.
        # some determination of the correct threshold given the lbdm profile. for simplicity here
        # we use a fixed threshold
        segments = []
        last_segmentation_index = 0
        for profile_index, boundary_strength in np.ndenumerate(profile):
            if boundary_strength > self.threshold:
                segments.append(Segment(mid, timeline[last_segmentation_index:profile_index[0]+1]))
                last_segmentation_index = profile_index[0]

        # get last few notes
        segments.append(Segment(mid, timeline[last_segmentation_index:]))
        # code for saving segments to file
        # put the end of the track into the last segment
        # tracks = []
        #    for seg_index in segmentation_indices:
        #             seg_track = MidiTrack()
        #             seg_track.extend(track[start_index+1:seg_index+1])
        #             start_index = seg_index
        #
        #             tracks.append(seg_track)
        # end_track = MidiTrack()
        # end_track.extend(track[start_index + 1:])
        # tracks.append(end_track)
        #
        # i = 0
        # # create midi files out of segments. Note these segments may not represent
        # # true segments of the track as listened as important messages such as
        # # instrument, volume and tempo messages may only be at the start of the MIDI track
        # for tr in tracks:
        #     segment_mid = MidiFile(ticks_per_beat=mid.ticks_per_beat)
        #     segment_mid.tracks.append(tr)
        #     segment_mid.save(f"../../mid/generated/segment_{i}.mid")
        #     i += 1
        return segments
