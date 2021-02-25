import math
import sys

import mido
import numpy as np


from typing import Dict, List, Tuple, Optional
from collections import OrderedDict


from project.segment.chord import Chord
from project.segment.note import Note
from project.segment.signature import TimeSignature, KeySignature


def get_note_tally(mid: mido.MidiFile) -> Dict[int, int]:
    """Returns a dictionary containing the occurrence of each note in the MIDI file.


    Args:
        mid (mido.MidiFile): The midi object to be analysed.

    Returns:
        Dict[int,int]: A dictionary with the keys being the MIDI note numbers (0 to 127), and the values being the number of occurences of
        the particular MIDI note.
    """

    note_dict = {}
    for i in range(128):
        note_dict[i] = 0

    for track in mid.tracks:
        for msg in track:
            # TODO: change to handle note_on/note_off pairs
            if msg.type == "note_on":
                note_dict[msg.note] += 1

    return note_dict


def get_type_tally(mid: mido.MidiFile) -> Dict[str, int]:
    """Returns a dictionary containing the occurrence of each message type in the MIDI file.


    Args:
        mid (mido.MidiFile): The midi object to be analysed.

    Returns:
        Dict[str,int]: A dictionary containing a tally of each MIDI message type (how often they appear)
    """
    type_dict = {}

    for track in mid.tracks:
        for msg in track:
            # TODO: change to handle note_on/note_off pairs
            if msg.type in type_dict:
                type_dict[msg.type] += 1
            else:
                type_dict[msg.type] = 1
    return type_dict


def get_chord_timeline(chord_track: mido.MidiTrack) -> List[Tuple[Chord, int, int]]:
    chords = []
    on_dict = OrderedDict()
    # off_dict = defaultdict(list)
    curr_time = 0
    last_note_off_time = 0
    for i in range(len(chord_track)):
        curr_time += chord_track[i].time
        if chord_track[i].type == "note_on" and chord_track[i].velocity != 0:
            if curr_time not in on_dict.keys():
                on_dict[curr_time] = []
            on_dict[curr_time].append(chord_track[i].note)
        elif chord_track[i].type == "note_off" or (chord_track[i].type == "note_on" and chord_track[i].velocity == 0):
            last_note_off_time = curr_time
            # off_dict[curr_time].append(chord_track[i].note)

    if len(on_dict) == 0:
        return []

    # get the end times of each chord
    end_times = list(on_dict.keys())[1:]
    end_times.append(last_note_off_time)
    # assume that a chord only stops playing when the next one starts (this is sufficient for the nottingham dataset)
    # TODO: change to also take into account that chords have an explicit time that they stop playing
    i = 0
    for (time, note_list) in on_dict.items():
        chords.append((Chord.from_midi_values(*note_list), time, end_times[i]))
        i += 1
    return chords


def get_note_timeline(track: mido.MidiTrack, chord_track: Optional[mido.MidiTrack] = None) -> List[Note]:
    """
    Returns a list of notes derived from the messages within the MIDI track. The data stored within each note is
    1. The start time of the note (in ticks)
    2. The end time of the note (in ticks)
    3. The note value being played
    4. The output channel of the note. This is important so the instrument that is played is preserved
    5. If chord_track is specified, the chord that was playing at the same time as the note

    Args:
        track: A track from a MIDI file
        chord_track: A track containing what chords were played in the midi file.

    Returns:
        A list of notes derived from the messages in the MIDI track .

    """
    notes = []
    last_note_dict = {}
    curr_time = 0
    for i in range(len(track)):            
        if track[i].type == "note_on" and track[i].velocity != 0:
            # start of new note being played
            notes.append(Note(curr_time + track[i].time, -1, track[i].note, track[i].channel, None, i, None))
            last_note_dict[track[i].note] = len(notes) - 1
        elif track[i].type == "note_off" or (track[i].type == "note_on" and track[i].velocity == 0):
            # note off (inc note on "running status")
            # naive: assume the previous note_on message was the one this note_off corresponds to
            # (not necessarily the case in polyphonic music)
            notes[last_note_dict[track[i].note]].end_time = curr_time + track[i].time  # set the last note's end time
            notes[last_note_dict[track[i].note]].end_message_index = i
        curr_time += track[i].time

    if chord_track is not None:
        chord_timeline = get_chord_timeline(chord_track)
        # naive (this is inefficient)
        for chord, chord_start, chord_end in chord_timeline:
            for note in notes:
                if note.start_time >= chord_start and note.end_time <= chord_end:
                    note.chord = chord

    return notes


def get_track_signatures(track: mido.MidiTrack) -> Tuple[List[Tuple[int, TimeSignature]], List[Tuple[int, KeySignature]]]:
    time_signatures = []
    key_signatures = []
    start_time = 0
    for message in track:
        if message.type == "time_signature":
            time_signatures.append(
                (start_time + message.time, TimeSignature(message.numerator, message.denominator)))
        elif message.type == "key_signature":
            if message.key.endswith("m"):  # is minor key
                key_signatures.append((start_time + message.time, KeySignature(message.key[:-1], True)))
            else:
                key_signatures.append((start_time + message.time, KeySignature(message.key, False)))
        start_time += message.time

    return time_signatures, key_signatures