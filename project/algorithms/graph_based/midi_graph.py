import pathlib

import networkx

from typing import Optional, List
from mido import MidiFile, MidiTrack

from project.util.midtools import get_note_timeline

from networkx.readwrite.gpickle import write_gpickle, read_gpickle
from tqdm import tqdm


class MidiGraph:
    def __init__(self, mid_file: MidiFile, melody_track: int, chord_track: Optional[int] = None, graph: Optional[networkx.Graph] = None):
        if graph is not None:
            self.__graph = graph
        else:
            self.__graph = networkx.Graph()
            self.__graph.add_node("root", source=mid_file.filename, melody_track=melody_track, chord_track=chord_track)

        self.mid_file = mid_file
        self.melody_track = melody_track
        self.chord_track = chord_track

    def add_node(self, filepath: str):
        self.__graph.add_node(pathlib.Path(filepath).stem, shape="box")

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

        write_gpickle(self.__graph, filepath)
        # positions = networkx.nx_agraph.graphviz_layout(self.__graph, prog="twopi") # node positions
        # networkx.draw(self.__graph, pos=positions)
        # write_dot(self.__graph, filepath)

    def load_notes_for_segments(self, mid_locations: str):
        for node in self.__graph.nodes:
            if node != "root":
                segment_mid = MidiFile(f"{mid_locations}/{node}.mid")
                self.__graph.nodes[node]["notes"] = get_note_timeline(segment_mid.tracks[self.melody_track])

    def get_copy_of_graph(self) -> networkx.Graph:
        return self.__graph.copy()

    @staticmethod
    def from_gpickle(pickle_path: str) -> "MidiGraph":
        graph: networkx.Graph = read_gpickle(pickle_path)
        root = graph.nodes["root"]
        mid_graph = MidiGraph(root["source"], root["melody_track"], root["chord_track"], graph=graph)
        return mid_graph


def create_dataset_graph() -> List[MidiGraph]:
    available_graphs = list(pathlib.Path("mid/generated/graph").glob("**/*.gpickle"))
    graphs = []
    for gpickle in tqdm(available_graphs):
        graph = MidiGraph.from_gpickle(str(gpickle))
        graph.load_notes_for_segments(str(pathlib.Path(gpickle).parents[0]))
        graphs.append(graph)

    return graphs
