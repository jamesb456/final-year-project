import argparse
import pathlib

import networkx
from networkx.drawing.nx_agraph import write_dot

from project.segment.segment import Segment
from project.util.midtools import get_note_timeline

from mido import MidiFile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the similarity of a MIDI file "
                                                 "to MIDI files already segmented ")
    parser.add_argument("midi_path", type=str, help="Path to query MIDI file")

    args = parser.parse_args()
    # compute reduction of query midi file first
    query_file = MidiFile(args.midi_path)
    notes = get_note_timeline(query_file.tracks[0])
    query_segment = Segment(query_file, 0, notes)

    reduced_segments = []
    current_segment = query_segment
    while current_segment.get_number_of_notes() > 1:
        weight, reduced_segment = current_segment.reduce_segment()
        reduced_segments.append((weight, reduced_segment))
        current_segment = reduced_segment

    available_dots = pathlib.Path("mid/generated").glob("**/*.dot")
    for dot_file in available_dots:
        s = 0
        dot: networkx.Graph = networkx.drawing.nx_agraph.read_dot(dot_file)
        dot.add_node("query")
        edges_to_add = []
        nodes_to_add = set()
        for node, node_data in dot.nodes(data=True):
            print("Checking node " + node)
            if node == "query":
                pass
            elif "label" in node_data.keys() and ("original_segment" in node_data["label"] or node_data["label"] == "root"):
                pass
            else:
                segment_mid = MidiFile(str(dot_file.parents[0] / (node + ".mid")))
                melody_track = segment_mid.tracks[0]
                timeline = get_note_timeline(melody_track)
                for i in range(len(reduced_segments)):
                    weight, r_segment = reduced_segments[i]
                    j = 0
                    if r_segment.notes == timeline:
                        nodes_to_connect = ["query"]
                        node_weights = [weight]
                        if i > 0:
                            for j in range(0, i):
                                nodes_to_connect.append(f"query_reduction_{j+1}")
                                node_weights.append(reduced_segments[j][0])
                        for k in range(len(nodes_to_connect)-1, 0, -1):
                            nodes_to_add.add(nodes_to_connect[k])
                            if k == len(nodes_to_connect) - 1:
                                edges_to_add.append((nodes_to_connect[k], node, node_weights[k]))
                            else:
                                edges_to_add.append((nodes_to_connect[k-1], nodes_to_connect[k], node_weights[k]))

                        pass
            for node_name in nodes_to_add:
                dot.add_node(node_name)

            for node_u, node_v, weight in edges_to_add:
                dot.add_edge(node_u, node_v, label=f"{weight}")

        pos = networkx.nx_agraph.graphviz_layout(dot, prog="neato")
        networkx.draw(dot, pos=pos)
        write_dot(dot, f"output_{s}.dot")
        s += 1


