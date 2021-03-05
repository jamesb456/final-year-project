import argparse
import pathlib

import networkx
import pandas as pd
import matplotlib.pyplot as plt
from networkx.algorithms.shortest_paths.astar import astar_path, astar_path_length
from networkx.drawing.nx_agraph import write_dot

from project.segment.segment import Segment
from project.util.midtools import get_note_timeline

from mido import MidiFile

if __name__ == "__main__":
    non_connected_penalty = 15
    parser = argparse.ArgumentParser(description="Query the similarity of a MIDI file "
                                                 "to MIDI files already segmented ")
    parser.add_argument("midi_path", type=str, help="Path to query MIDI file")
    parser.add_argument("--write_graphs", action="store_true", help="If set to true, writes the graphs containing "
                                                                    "the query segment connected to the original, "
                                                                    "stored graphs.")

    args = parser.parse_args()
    # compute reduction of query midi file first
    query_file = MidiFile(args.midi_path)
    pathlib.Path(f"query_output/graphs/{pathlib.Path(args.midi_path).stem}").mkdir(exist_ok=True, parents=True)
    notes = get_note_timeline(query_file.tracks[0])
    query_segment = Segment(query_file, 0, notes)

    query_reduced_segments = []
    current_segment = query_segment

    print("Starting by computing reductions for query segment")
    while current_segment.get_number_of_notes() > 1:
        weight, reduced_segment = current_segment.reduce_segment()
        query_reduced_segments.append((weight, reduced_segment))
        current_segment = reduced_segment

    available_dots = pathlib.Path("mid/generated").glob("**/*.dot")

    # for each graph .dot we know about, check the similarity
    print("\nQuery reduction done, now checking each known graph file.")
    similarity_dict = {}
    for dot_filepath in available_dots:
        print("\n=====================\nOpening " + str(dot_filepath) + "\n\n")
        dot: networkx.Graph = networkx.drawing.nx_agraph.read_dot(dot_filepath)

        # due to issue in networkx have to reconvert to a float
        for u, v, edge in dot.edges(data=True):
            edge["label"] = float(edge["label"])
        dot.add_node("query")  # add query node to graph so we can compute the shortest path lengths
        last_node = "query"
        print("\n=Adding query segment reduction nodes to graph=\n")
        for i, (edge_weight, reduced_segment) in enumerate(query_reduced_segments):
            reduce_name = f"query_reduction_{i + 1}"
            dot.add_node(reduce_name)
            dot.add_edge(last_node, reduce_name, label=edge_weight, color="blue")
            last_node = reduce_name
        original_nodes = []
        # iterate through each node in the graph of the music piece, adding edges between those nodes and the reductions
        # we just computed for the query segment
        print("\nDone adding nodes. Now adding edges between query nodes and original nodes: ")
        for node, node_data in dot.nodes(data=True):
            if "query" in node:  # ignore any nodes from the query
                print("Ignoring node because it came from the query segment")
            else:
                if "label" in node_data.keys() and ("original_segment" in node_data["label"]):
                    original_nodes.append(node)

                # load the mid at this graph position
                segment_mid = MidiFile(str(dot_filepath.parents[0] / (node + ".mid")))
                segment_melody_track = segment_mid.tracks[0]
                segment_timeline = get_note_timeline(segment_melody_track)
                if query_segment.notes == segment_timeline:
                    dot.add_edge("query", node, label=0, color="blue")
                    continue
                else:
                    if len(segment_timeline) == 1:
                        if len(query_reduced_segments) > 0:
                            dot.add_edge(f"query_reduction_{len(query_reduced_segments)}", node,
                                         label=non_connected_penalty, color="red")
                        else:
                            dot.add_edge("query", node, label=non_connected_penalty, color="red")
                        continue

                    last_node = "query"
                    for i in range(len(query_reduced_segments)):
                        _, r_segment = query_reduced_segments[i]
                        j = 0
                        if r_segment.notes == segment_timeline:
                            dot.add_edge(f"query_reduction_{i + 1}", node, label=0, color="blue")
                            last_node = f"query_reduction_{i + 1}"
                            break
                        last_node = f"query_reduction_{i + 1}"

                    if "type" in node_data.keys() and node_data["type"] == "terminal":
                        # if there are no matching reductions
                        # add an edge of weight 1 between the last reduction and this node
                        # if it's the last reduced node
                        dot.add_edge(last_node, node, label=non_connected_penalty, color="red")

        print("\nRemoving root node")

        # we've added the query segment: now we can compute the distance of the shortest path
        print("\nQuery segment added to graph, now computing similarity:\n")
        total_path_length = 0
        for original_node in original_nodes:
            try:
                path_length = astar_path_length(dot, "query", original_node, weight="label")#
                total_path_length += path_length
            except networkx.NetworkXNoPath:
                # add a large penalty for a lack of connections
                total_path_length += 100
                print(f"No path between {original_node} and query")

        similarity_dict[str(dot_filepath.parents[0])] = total_path_length / len(original_nodes)  # avg distance between source segments and query segment

        if args.write_graphs:
            print("=Writing graph to file=")
            pos = networkx.nx_agraph.graphviz_layout(dot, prog="twopi", root="query")
            networkx.draw(dot, pos=pos)
            write_dot(dot, f"query_output/graphs/{pathlib.Path(args.midi_path).stem}"
                           f"/output_{dot_filepath.parts[len(dot_filepath.parts) - 2]}.dot")

    print("\nDone: Final similarity rankings: ")

    sorted_dict = {k: v for k, v in sorted(similarity_dict.items(), key=lambda item: item[1])}
    series = pd.Series(sorted_dict)

    for mid_name, similarity in sorted_dict.items():
        print(f"\t{mid_name}: {similarity}")
    series.plot(kind="bar")
    plt.show()
    series.to_csv(f"query_output/rankings/{pathlib.Path(args.midi_path).stem}.csv")



