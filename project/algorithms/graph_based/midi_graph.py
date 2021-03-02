import pathlib

import networkx

from typing import Optional
from mido import MidiFile, MidiTrack

from networkx.drawing.nx_pydot import write_dot


class MidiGraph:
    def __init__(self, mid_file: MidiFile, melody_track: int, chord_track: Optional[int] = None):
        self.__graph = networkx.Graph()
        self.mid_file = mid_file
        self.melody_track = melody_track
        self.chord_track = chord_track
        self.__graph.add_node(pathlib.Path(mid_file.filename).stem, label="root", melody_track=melody_track,
                              chord_track=chord_track, directory=pathlib.Path(mid_file.filename).parents[0])
        pass

    def add_node(self, filepath: str):
        self.__graph.add_node(pathlib.Path(filepath).stem)

    def add_identifying_node(self, filepath: str):
        self.__graph.add_node(pathlib.Path(filepath).stem, label="original_" + pathlib.Path(filepath).stem )

    def add_edge(self, f1: str, f2: str, weight: int = 1):
        self.__graph.add_edge(pathlib.Path(f1).stem, pathlib.Path(f2).stem, label=weight)

    def save_to_file(self, filepath: str):
        pos = networkx.nx_agraph.graphviz_layout(self.__graph, prog="dot")
        networkx.draw(self.__graph, pos=pos)
        write_dot(self.__graph, filepath)

    @staticmethod
    def from_file(graph_path: str):
        pass
