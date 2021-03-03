import argparse
import pathlib

import networkx
from networkx.algorithms.shortest_paths.astar import astar_path
from networkx.drawing.nx_agraph import write_dot

from project.segment.segment import Segment
from project.util.midtools import get_note_timeline

from mido import MidiFile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the similarity of a MIDI file "
                                                 "to MIDI files already segmented ")
    parser.add_argument("midi_path", type=str, help="Path to query MIDI file")
    parser.add_argument("--write_graphs", action="store_true", help="If set to true, writes the graphs containing "
                                                                    "the query segment connected to the original, "
                                                                    "stored graphs.")
    args = parser.parse_args()
    # compute reduction of query midi file first
    query_file = MidiFile(args.midi_path)
    notes = get_note_timeline(query_file.tracks[0])
    query_segment = Segment(query_file, 0, notes)

    reduced_segments = []
    current_segment = query_segment

    print("Starting by computing reductions for query segment")
    while current_segment.get_number_of_notes() > 1:
        weight, reduced_segment = current_segment.reduce_segment()
        reduced_segments.append((weight, reduced_segment))
        current_segment = reduced_segment

    available_dots = pathlib.Path("mid/generated").glob("**/*.dot")

    # for each graph .dot we know about, check the similarity
    print("\nQuery reduction done, now checking each known graph file.")
    for dot_file in available_dots:
        print("\n=====================\nOpening " + str(dot_file) + "\n\n")
        dot: networkx.Graph = networkx.drawing.nx_agraph.read_dot(dot_file)
        dot.add_node("query")  # add query node to graph so we can compute the shortest path lengths
        last_node = "query"
        print("\n=Adding query segment reduction nodes to graph=\n")
        for i, (edge_weight, reduced_segment) in enumerate(reduced_segments):
            reduce_name = f"query_reduction_{i + 1}"
            dot.add_node(reduce_name)
            dot.add_edge(last_node, reduce_name, label=edge_weight, color="blue")
            last_node = reduce_name

        original_nodes = []
        # iterate through each node in the graph of the music piece, adding edges between those nodes and the reductions
        # we just computed for the query segment
        print("\nDone adding nodes. Now adding edges between query nodes and original nodes: ")
        root_name = ""
        for node, node_data in dot.nodes(data=True):
            print("Checking node " + node)
            if "query" in node:  # ignore any nodes from the query
                print("Ignoring node because it came from the query segment")
            elif "label" in node_data.keys() and ("original_segment" in node_data["label"]):
                # ignore root or segments from the original song
                # (but add to a list to query the shortest path for later)
                original_nodes.append(node)
            elif "type" in node_data.keys() and node_data["type"] == "root":
                print("Ignoring the original song's root node")
                root_name = node
            else:
                # load the mid at this graph position
                segment_mid = MidiFile(str(dot_file.parents[0] / (node + ".mid")))
                melody_track = segment_mid.tracks[0]
                timeline = get_note_timeline(melody_track)
                for i in range(len(reduced_segments)):
                    weight, r_segment = reduced_segments[i]
                    j = 0
                    if r_segment.notes == timeline:
                        dot.add_edge(f"query_reduction_{i + 1}", node, label="0", color="blue")
                        pass

        print("\nRemoving root node")
        dot.remove_node(root_name)

        # we've added the query segment: now we can compute the distance of the shortest path
        print("\nQuery segment added to graph, now computing similarity:\n")
        for original_node in original_nodes:
            try:
                path = astar_path(dot, "query", original_node)
                print(f"Shortest path between query and {original_node} is {path}")
            except networkx.NetworkXNoPath:
                print(f"No path between {original_node} and query")

        if args.write_graphs:
            print("Writing graph to file")
            pos = networkx.nx_agraph.graphviz_layout(dot, prog="twopi")
            networkx.draw(dot, pos=pos)
            write_dot(dot, f"output_{dot_file.parts[len(dot_file.parts) - 2]}.dot")
