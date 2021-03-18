import pathlib

import networkx
import pandas as pd
from mido import MidiFile
from networkx import read_gpickle, astar_path_length, write_gpickle

from project.core.segment.graph_segment import GraphSegment
from project.util.midtools import get_note_timeline


def query_graph(midi_path, use_minimum, write_graphs):
    query_file = MidiFile(midi_path)
    metric = "Minimum" if use_minimum else "Average"
    non_connected_penalty = 100
    pathlib.Path(f"query_output/graphs/{pathlib.Path(midi_path).stem}").mkdir(exist_ok=True, parents=True)
    notes = get_note_timeline(query_file.tracks[0])  # TODO: change to use arbitrary track index
    query_segment = GraphSegment(query_file, 0, notes)

    query_reduced_segments = []
    current_segment = query_segment

    print("Starting by computing reductions for query core")
    while current_segment.get_number_of_notes() > 1:
        weight, reduced_segment = current_segment.reduce_segment()
        query_reduced_segments.append((weight, reduced_segment))
        current_segment = reduced_segment

    available_graphs = pathlib.Path("mid/generated/graph").glob("**/*.gpickle")

    # for each graph .dot we know about, check the similarity
    print("\nQuery reduction done, now checking each known graph file.")
    similarity_dict = {}
    for graph_filepath in available_graphs:
        print("\n=====================\nOpening " + str(graph_filepath) + " for querying \n")
        dot: networkx.Graph = read_gpickle(graph_filepath)

        # due to issue in networkx have to reconvert to a float
        for u, v, edge in dot.edges(data=True):
            edge["label"] = float(edge["label"])
        dot.add_node("query")  # add query node to graph so we can compute the shortest path lengths
        last_node = "query"
        for i, (edge_weight, reduced_segment) in enumerate(query_reduced_segments):
            reduce_name = f"query_reduction_{i + 1}"
            dot.add_node(reduce_name)
            dot.add_edge(last_node, reduce_name, label=edge_weight, color="blue")
            last_node = reduce_name
        original_nodes = []
        # iterate through each node in the graph of the music piece, adding edges between those nodes and the reductions
        # we just computed for the query core
        for node, node_data in dot.nodes(data=True):
            if "query" in node:  # ignore any nodes from the query
                pass
            else:
                if "label" in node_data.keys() and ("original_segment" in node_data["label"]):
                    original_nodes.append(node)

                # load the mid at this graph position
                segment_mid = MidiFile(str(graph_filepath.parents[0] / (node + ".mid")))
                segment_melody_track = segment_mid.tracks[0]
                segment_timeline = get_note_timeline(segment_melody_track)
                if query_segment.notes == segment_timeline:
                    # dot.add_edge("query", node, label=0, color="blue")
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

        # we've added the query core: now we can compute the distance of the shortest path
        total_path_length = 0
        min_path_length = float('inf')
        for original_node in original_nodes:
            try:
                path_length = astar_path_length(dot, "query", original_node, weight="label")  #
                total_path_length += path_length
                min_path_length = min(min_path_length, path_length)
            except networkx.NetworkXNoPath:
                # add a large penalty for a lack of connections
                total_path_length += non_connected_penalty
                print(f"No path between {original_node} and query")

        if use_minimum:
            # avg distance between source segments and query core
            similarity_dict[str(graph_filepath.parts[len(graph_filepath.parts) - 2])] = min_path_length
        else:
            # min distance between source segments and query core
            similarity_dict[str(graph_filepath.parts[len(graph_filepath.parts) - 2])] = total_path_length / len(
                original_nodes)
        print(f"Done: {metric} distance was {similarity_dict[str(graph_filepath.parts[len(graph_filepath.parts) - 2])]}")
        if write_graphs:
            print("= --write_graphs: Writing graph to file=")
            write_gpickle(dot, f"query_output/graphs/{pathlib.Path(midi_path).stem}"
                               f"/output_{graph_filepath.parts[len(graph_filepath.parts) - 2]}.gpickle")

    print("\nDone: Final similarity rankings (least to most similar): ")

    sorted_dict = {k: v for k, v in sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True)}
    series = pd.Series(sorted_dict)

    for index, (mid_name, similarity) in enumerate(sorted_dict.items()):
        print(f"\t[{len(sorted_dict.items()) - index}] {mid_name}: {similarity}")

    # plt.clf()
    # series.plot(kind="barh")
    # plt.ylabel("MIDI file")

    # plt.xlabel(f"{metric} distance to query core")
    # plt.title(f"{metric} distance between the query core {pathlib.Path(args.midi_path)} and known MIDI graphs "
    #           f"(Lower is better)")
    # plt.show(block=False)
    series.rename_axis(f"{metric} core distance from query core")
    series.to_csv(f"query_output/rankings/{pathlib.Path(midi_path).stem}.csv")