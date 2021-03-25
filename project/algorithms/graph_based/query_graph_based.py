import pathlib
from typing import List, Dict

import networkx
import pandas as pd
from mido import MidiFile
from networkx import astar_path_length, write_gpickle
from tqdm import tqdm

from project.algorithms.graph_based.midi_graph import MidiGraph
from project.algorithms.graph_based.graph_segment import GraphSegment
from project.algorithms.core.midtools import get_note_timeline


def query_graph(midi_path: str, melody_track: int, use_minimum: bool,
                write_graphs: bool, graphs: List[MidiGraph]) -> Dict[str, float]:
    query_file = MidiFile(midi_path)
    metric = "Minimum" if use_minimum else "Average"
    non_connected_penalty = 100
    pathlib.Path(f"query_output/graphs/{pathlib.Path(midi_path).stem}").mkdir(exist_ok=True, parents=True)
    notes = get_note_timeline(query_file.tracks[melody_track])
    query_segment = GraphSegment(query_file, 0, notes)

    query_reduced_segments = []
    current_segment = query_segment

    # print("Starting by computing reductions for query segment")
    while current_segment.get_number_of_notes() > 1:
        weight, reduced_segment = current_segment.reduce_segment()
        query_reduced_segments.append((weight, reduced_segment))
        current_segment = reduced_segment

    # for each graph file we know about, check the similarity
    # print("\nQuery reduction done, now checking each known graph file.")
    similarity_dict = {}
    prog_bar = tqdm(graphs, desc=f"Graph Algorithm: {pathlib.Path(midi_path).stem} Progress")
    for midi_graph in prog_bar:
        # get a copy of the graph
        graph = midi_graph.get_copy_of_graph()
        source_mid_path = str(pathlib.Path(graph.nodes["root"]["source"]).stem)
        prog_bar.set_postfix({"current_graph": source_mid_path})
        # print("\n=====================\nOpening graph for " + source_mid_path + " for querying \n")

        # due to issue in networkx have to reconvert to a float
        for u, v, edge in graph.edges(data=True):
            edge["label"] = float(edge["label"])
        graph.add_node("query")  # add query node to graph so we can compute the shortest path lengths
        last_node = "query"
        for i, (edge_weight, reduced_segment) in enumerate(query_reduced_segments):
            reduce_name = f"query_reduction_{i + 1}"
            graph.add_node(reduce_name)
            graph.add_edge(last_node, reduce_name, label=edge_weight, color="blue")
            last_node = reduce_name
        original_nodes = []
        # iterate through each node in the graph of the music piece, adding edges between those nodes and the reductions
        # we just computed for the query core
        for node, node_data in graph.nodes(data=True):
            if "query" in node or node == "root":  # ignore any nodes from the query or the root node
                pass
            else:
                if "label" in node_data.keys() and ("original_segment" in node_data["label"]):
                    original_nodes.append(node)

                # load the mid at this graph position
                segment_timeline = node_data["notes"]
                if query_segment.notes == segment_timeline:
                    # dot.add_edge("query", node, label=0, color="blue")
                    continue
                else:
                    if len(segment_timeline) == 1:
                        if len(query_reduced_segments) > 0:
                            graph.add_edge(f"query_reduction_{len(query_reduced_segments)}", node,
                                           label=non_connected_penalty, color="red")
                        else:
                            graph.add_edge("query", node, label=non_connected_penalty, color="red")
                        continue

                    last_node = "query"
                    for i in range(len(query_reduced_segments)):
                        _, r_segment = query_reduced_segments[i]
                        j = 0
                        if r_segment.notes == segment_timeline:
                            graph.add_edge(f"query_reduction_{i + 1}", node, label=0, color="blue")
                            last_node = f"query_reduction_{i + 1}"
                            break
                        last_node = f"query_reduction_{i + 1}"

                    if "type" in node_data.keys() and node_data["type"] == "terminal":
                        # if there are no matching reductions
                        # add an edge of weight 1 between the last reduction and this node
                        # if it's the last reduced node
                        graph.add_edge(last_node, node, label=non_connected_penalty, color="red")

        # we've added the query core: now we can compute the distance of the shortest path
        total_path_length = 0
        min_path_length = float('inf')
        for original_node in original_nodes:
            try:
                path_length = astar_path_length(graph, "query", original_node, weight="label")  #
                total_path_length += path_length
                min_path_length = min(min_path_length, path_length)
            except networkx.NetworkXNoPath:
                # add a large penalty for a lack of connections
                total_path_length += non_connected_penalty
                print(f"No path between {original_node} and query")

        if use_minimum:
            # avg distance between source segments and query core
            similarity_dict[source_mid_path] = min_path_length
        else:
            # min distance between source segments and query core
            similarity_dict[source_mid_path] = total_path_length / len(
                original_nodes)
        #  print(f"Done: {metric} distance was {similarity_dict[source_mid_path]}")
        if write_graphs:
            #  print("= --write_graphs: Writing graph to file=")
            write_gpickle(graph, f"query_output/graphs/{pathlib.Path(midi_path).stem}"
                                 f"/output_{source_mid_path}.gpickle")

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
    return sorted_dict
