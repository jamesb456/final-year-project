import pathlib

import networkx

from typing import Optional
from mido import MidiFile


from project.algorithms.core.note_segment import NoteSegment


class MidiGraph:
    def __init__(self, mid_file: MidiFile, melody_track: int, chord_track: Optional[int] = None,
                 graph: Optional[networkx.Graph] = None):
        if graph is not None:
            self.__graph = graph
        else:
            self.__graph = networkx.Graph()
        self.mid_file = mid_file
        self.melody_track = melody_track
        self.chord_track = chord_track

    def add_node(self, filepath: str, segment: NoteSegment):
        self.__graph.add_node(pathlib.Path(filepath).stem, shape="box",
                              segment=segment)

    def add_identifying_node(self, filepath: str, segment: NoteSegment):
        self.__graph.add_node(pathlib.Path(filepath).stem, label="original_" + pathlib.Path(filepath).stem,
                              style="filled", fillcolor="gray", fontcolor="white", shape="box", segment=segment)

    def add_edge(self, f1: str, f2: str, weight: float = 1):
        self.__graph.add_edge(pathlib.Path(f1).stem, pathlib.Path(f2).stem, label=weight)

    def draw(self, path: str):
        agraph = networkx.drawing.nx_agraph.to_agraph(self.__graph)
        agraph.layout("dot")
        agraph.draw(path)

    def get_copy_of_graph(self) -> networkx.Graph:
        return self.__graph.copy()



