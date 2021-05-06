import pathlib

import networkx

from typing import Optional
from mido import MidiFile


from project.algorithms.core.note_segment import NoteSegment


class MidiGraph:
    def __init__(self, mid_file: MidiFile, melody_track: int, chord_track: Optional[int] = None,
                 graph: Optional[networkx.Graph] = None):
        """
        A graph of MIDI segments. Each node is primarily represented via a string, with the segments
        themselves being added as extra data. Internally, this class uses a NetworkX graph.

        Args:
            mid_file: The MIDI file this graph represents
            melody_track: The MIDI track index used to create the segments in the graph
            chord_track: The MIDI track index containing the chords of the MIDI, if it exists
            graph: If not None, use an existing NetworkX graph as the internal graph
        """
        if graph is not None:
            self.__graph = graph
        else:
            self.__graph = networkx.Graph()
        self.mid_file = mid_file
        self.melody_track = melody_track
        self.chord_track = chord_track

    def add_node(self, node_name: str, segment: NoteSegment):
        """
        Add a node to the graph. A node consists of a string (essentially a key) and the corresponding segment.
        
        Args:
            node_name: A string which will become the node name
            segment: The segment associated with node_name

        """
        self.__graph.add_node(pathlib.Path(node_name).stem, shape="box",
                              segment=segment)

    def add_identifying_node(self, node_name: str, segment: NoteSegment):
        """
        Add an *identifying* node to the graph: this means an original segment that wasn't reduced.

        Args:
            node_name: The name of the identifying node
            segment: The segment associated with node_name
        """
        self.__graph.add_node(pathlib.Path(node_name).stem, label="original_" + pathlib.Path(node_name).stem,
                              style="filled", fillcolor="gray", fontcolor="white", shape="box", segment=segment)

    def add_edge(self, n1: str, n2: str, weight: float = 1):
        """
        Add an edge between 2 nodes in the graph, with an optional weight. These edges are NOT directed.

        Args:
            n1: The string key of one of the nodes to connect up
            n2: The string key of one the other node to connect up
            weight: The weight of the edge between n1 and n2. The default weight is 1.

        """
        self.__graph.add_edge(pathlib.Path(n1).stem, pathlib.Path(n2).stem, label=weight)

    def draw(self, path: str):
        """
        Draw the internal graph to the path ``path``

        Args:
            path: The path to save the drawing of the graph
        """
        agraph = networkx.drawing.nx_agraph.to_agraph(self.__graph)
        agraph.layout("dot")
        agraph.draw(path)

    def get_copy_of_graph(self) -> networkx.Graph:
        """
        Return a copy of the internal graph

        Returns:
            A copy of the internal graph

        """
        return self.__graph.copy()



