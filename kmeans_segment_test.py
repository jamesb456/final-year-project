from project.algorithms.graph_based.lbdm_clustering_segmenter import LbdmClusteringSegmenter
from mido import MidiFile
import pathlib

from project.algorithms.graph_based.lbdm_segmenter import LbdmSegmenter

if __name__ == "__main__":
    old_segmenter = LbdmSegmenter(threshold=0.5)
    segmenter = LbdmClusteringSegmenter()
    mid = MidiFile("mid/nottingham/jigs110.mid")
    old_segments = old_segmenter.create_segments(mid, 0)
    segments = segmenter.create_segments(mid, 0)

    for i, segment in enumerate(old_segments):
        segment.save_as_midi(f"mid/kmeans_test/old_{pathlib.Path(mid.filename).stem}_{i}.mid")

    for i, segment in enumerate(segments):
        segment.save_as_midi(f"mid/kmeans_test/kmeans_{pathlib.Path(mid.filename).stem}_{i}.mid")
