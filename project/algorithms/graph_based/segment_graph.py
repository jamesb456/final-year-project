import networkx

from typing import Optional
from mido import MidiFile, MidiTrack
from project.segment.segment import Segment


class SegmentGraph:
    def __init__(self, mid_file: MidiFile, melody_track: int, chord_track: Optional[int] = None):
        self.__graph = networkx.Graph()
        self.mid_file = mid_file
        self.melody_track = melody_track
        self.chord_track = chord_track

    def add_node(self, filepath: str):
        self.__graph.add_node(filepath)

    def add_edge(self, f1: str, f2: str, weight: int = 1):
        self.__graph.add_edge(f1, f2, weight=weight)
