import argparse
import pathlib

import networkx

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
        dot : networkx.Graph = networkx.drawing.nx_agraph.read_dot(dot_file)

