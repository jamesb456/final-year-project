import numpy as np

from typing import List

from mido import MidiFile, MidiTrack, bpm2tempo, tick2second
from project.algorithms.pitch_vector.pitch_vector_segment import PitchVectorSegment
from project.algorithms.core.segmenter import Segmenter
from project.algorithms.core.midtools import get_track_tempo_changes, is_note_on


class PitchVectorSegmenter(Segmenter):

    def __init__(self, window_size: float, observations: int):
        """
        A Segmenter which divides a MIDI file into several overlapping multidimensional vectors. Each vector is based
        on observations of the pitch within a ``window_size`` time window.

        Args:
            window_size: The size of the window, in seconds
            observations: The number of observations, or dimensions, in each vector.
        """
        self.window_size = window_size
        self.observations = observations
        super().__init__()

    @staticmethod
    def __normalize_pv(pv_arr: np.ndarray) -> float:
        """
        Normalize a pitch vector by taking away the mean of all components from every component.

        Args:
            pv_arr: The pitch vector to be normalized

        Returns:
            the mean pitch of the pitch vector
        """
        mean_pitch = np.mean(pv_arr)
        pv_arr -= mean_pitch
        return float(mean_pitch)

    @staticmethod
    def __get_observations(track: MidiTrack, start_index: int, num_obs: int, window_size: float,
                           tempo: int, ticks_per_beat: int) -> np.ndarray:
        """
        Returns a pitch vector with *observations* of the pitch throughout a time window starting at the note onset of
        the note at ``start_index``, and stopping after ``window_size`` seconds.

        Args:
            track: The MidiTrack to get the observations from.
            start_index: The start index of the note to begin the pitch vector from
            num_obs: The number of points to observe the pitch at.
            window_size: The size of the vector in terms of time in seconds
            tempo: The initial tempo of the song at the start of the vector
            ticks_per_beat: The ticks per beat of the MIDI file the track is taken from

        Returns:
            A numpy array which is a pitch vector
        """
        time_to_advance = window_size / (num_obs - 1)
        pv_arr = np.empty(num_obs, dtype=float)

        current_delta = track[start_index].time
        current_index = start_index
        current_tempo = tempo
        # derive current time from j? current_time = j * (window_size / (num_obs - 1))
        # current msg time = prev message times + tick2second(msg.time,ticks_per_beat,tempo)
        # if current msg time <= current time position is according to j
        #  check what the message is: if tempo, update the tempo
        #                             if note on, update the pitch
        # else do nothing
        # current msg time += this msg time
        for j in range(num_obs):
            note_observed = False
            max_time_delta = j * time_to_advance
            for message in track[current_index:]:
                msg_length = tick2second(message.time, ticks_per_beat, tempo)
                if current_delta + msg_length > max_time_delta:
                    break
                else:
                    current_delta += msg_length
                    current_index += 1
                    if message.type == "set_tempo":
                        current_tempo = message.tempo
                    elif is_note_on(message):
                        pv_arr[j:] = message.note  # default is that the last note playing for all notes after this
                        # is this note
                        # (i.e. if there's no note on since the last detected one thats what note is playing)
                        note_observed = True
                    elif message.type == "end_of_track":
                        if j == num_obs - 1 and current_delta == max_time_delta:
                            break  # end of track but not exceeding it (so if the vector goes right to the end
                            # that's fine, but any further is not

                        return np.empty(0)  # don't extract if pitch vector exceeds end of song

        return pv_arr

    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[PitchVectorSegment]:
        """
        Create segments based on an overlapping segmentation algorithm, extracting pitch vectors at each note onset.

        Args:
            mid: The file to segment
            track_index: The index of the track to create segments from
            **kwargs: Not used

        Returns:
            A list of segments of this MIDI file represented as vectors.
        """
        track: MidiTrack = mid.tracks[track_index]
        pitch_vector_segments = []
        delta_t = 0
        tempo = bpm2tempo(120)

        for i, msg in enumerate(track):
            delta_t += tick2second(msg.time, mid.ticks_per_beat, tempo)
            if is_note_on(msg):
                pv_arr = self.__get_observations(track, i, self.observations, self.window_size, tempo,
                                                 mid.ticks_per_beat)
                if len(pv_arr) == 0:
                    break
                pitch_modifier = self.__normalize_pv(pv_arr)  # normalize to have mean of 0
                start_offset = delta_t
                pitch_vector_segments.append(PitchVectorSegment(mid, track_index, pv_arr, pitch_modifier, start_offset))
            elif msg.type == "set_tempo":
                tempo = msg.tempo

        return pitch_vector_segments
