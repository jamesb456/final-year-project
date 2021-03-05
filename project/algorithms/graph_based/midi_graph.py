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
        pass

    def add_node(self, filepath: str):
        self.__graph.add_node(pathlib.Path(filepath).stem,shape="box")

    def add_identifying_node(self, filepath: str):
        self.__graph.add_node(pathlib.Path(filepath).stem, label="original_" + pathlib.Path(filepath).stem,
                              style="filled",
                              fillcolor="gray",
                              fontcolor="white",
                              shape="box")

    def add_edge(self, f1: str, f2: str, weight: float = 1):
        self.__graph.add_edge(pathlib.Path(f1).stem, pathlib.Path(f2).stem, label=weight)

    def save_to_file(self, filepath: str):
        # add attributes to terminal nodes (that aren't the original nodes)
        for node in self.__graph.nodes:
            if "reduction" in node and len(self.__graph.edges([node])) == 1:
                self.__graph.nodes[node]["type"] = "terminal"

        pos = networkx.nx_agraph.graphviz_layout(self.__graph, prog="twopi")
        networkx.draw(self.__graph, pos=pos)
        write_dot(self.__graph, filepath)

