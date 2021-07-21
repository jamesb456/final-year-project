#  run everything: showing everything working
import contextlib
import pathlib
import shutil
import time

import tqdm
import os
import json

from project.algorithms.graph_based import segment_graph_based, query_graph_based, lbdm_segmenter
from project.algorithms.pitch_vector import segment_pitch_vector, query_pitch_vector, pitch_vector_segmenter
from project.algorithms.core import time_segmenter
from project.algorithms.create_datasets import create_dataset_pv, create_dataset_graph

from project.algorithms.query_creation import indexed_query_creator

if __name__ == '__main__':
    # segmentation
    print("Testing all components of the system together")
    print("Using a small version of the nottingham dataset (only the ashover songs)")
    print("Create/use a nottingham-mini dataset only containing these songs (@ mid/nottingham-mini )")

    ashover_files = list(pathlib.Path("mid/nottingham").glob("ashover*.mid"))  # files to copy
    nottingham_mini_path = pathlib.Path("mid/nottingham-mini")

    if not nottingham_mini_path.exists():
        print("No nottingham-mini directory: creating it and copying the ashover files to it.")
        nottingham_mini_path.mkdir(parents=True)
        for file in ashover_files:
            shutil.copy(file, nottingham_mini_path)
        print("Done copying")

    nottingham_mini_files = pathlib.Path("mid/nottingham-mini").glob("*.mid")

    print("First: indexing (using both the pitch vector and graph based methods)")
    for file in tqdm.tqdm(nottingham_mini_files, desc="Graph Algorithm indexing progress"):
        with open(os.devnull, 'w') as void:
            with contextlib.redirect_stderr(void):
                with contextlib.redirect_stdout(void):
                    segment_graph_based.segment_graph(file, 0, "nottingham-mini-chords", 1, False)

    for file in tqdm.tqdm(nottingham_mini_files, desc="Pitch Vector indexing progress"):
        with open(os.devnull, 'w') as void:
            with contextlib.redirect_stderr(void):
                with contextlib.redirect_stdout(void):
                    segment_pitch_vector.segment_pitch_vector(file, 0, "nottingham-mini-pv")

    print("Indexing done. To test the algorithms, first create 20 query midi files for each algorithm:")
    graph_segmenter = lbdm_segmenter.LbdmSegmenter()
    pv_segmenter = time_segmenter.TimeSegmenter(3)

    creator_graph = indexed_query_creator.IndexedQueryCreator(graph_segmenter, 1)
    creator_vector = indexed_query_creator.IndexedQueryCreator(pv_segmenter, 1)

    print("==The graph based queries:==")
    q1 = creator_graph.create_queries("mid/nottingham-mini", 20, 0, chord_track=1)

    print("\n==Done. The pitch vector queries:==")
    q2 = creator_vector.create_queries("mid/nottingham-mini", 20, 0)

    print("Queries created. Saving them to disk")

    query_location = pathlib.Path("mid/queries")
    (query_location / "mini_graph").mkdir(parents=True, exist_ok=True)
    (query_location / "mini_vector").mkdir(parents=True, exist_ok=True)

    for query_segment in q1:
        query_segment.save_as_midi(query_location / "mini_graph" /
                                   f"{query_segment.filename}_{query_segment.start_time}.mid")

    for query_segment in q2:
        query_segment.save_as_midi(query_location / "mini_vector" /
                                   f"{query_segment.filename}_{query_segment.start_time}.mid")

    print("Queries saved. Now test them in query by example")
    print("First load the datasets")

    dataset_graph = create_dataset_graph("nottingham-mini-chords")
    dataset_pv = create_dataset_pv("nottingham-mini-pv", 8)

    print("=Datasets loaded=")

    graph_queries = list(pathlib.Path(query_location / "mini_graph").glob("*.mid"))
    pitch_vector_queries = list(pathlib.Path(query_location / "mini_vector").glob("*.mid"))
    graph_results = []
    pitch_results = []
    for mid in tqdm.tqdm(graph_queries, desc="Graph querying progress"):
        with open(os.devnull, 'w') as void:
            with contextlib.redirect_stderr(void):
                with contextlib.redirect_stdout(void):
                    results = query_graph_based.query_graph(str(mid), 0, True, False, dataset_graph, chord_track=1)
                    graph_results.append(results)

    for mid in tqdm.tqdm(pitch_vector_queries, desc="Pitch vector querying progress"):
        with open(os.devnull, 'w') as void:
            with contextlib.redirect_stderr(void):
                with contextlib.redirect_stdout(void):
                    results, _ = query_pitch_vector.query_pitch_vector(str(mid), dataset_pv, 0)
                    pitch_results.append(results)

    print("Done: to give an idea of what the results look like from least to most similar:")

    print("==Graph results:==")
    print(json.dumps(graph_results[0], indent=4))

    print("\n\n==Pitch Vector results:==")
    print(json.dumps(pitch_results[0], indent=4))
