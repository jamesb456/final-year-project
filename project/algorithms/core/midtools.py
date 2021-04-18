"""
Common operation on MIDI files and objects
"""
import re

import mido

from typing import Dict, List, Tuple, Optional, Deque
from collections import OrderedDict, deque

from mido import MidiTrack, MidiFile, Message, bpm2tempo, tick2second, MetaMessage

from project.algorithms.core import constants
from project.algorithms.core.chord import Chord
from project.algorithms.core.note import Note
from project.algorithms.graph_based.signature import TimeSignature, KeySignature


def is_note_off(msg: Message) -> bool:
    return msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0)


def is_note_on(msg: Message) -> bool:
    return msg.type == "note_on" and msg.velocity > 0


def get_note_tally(mid: MidiFile) -> Dict[int, int]:
    """Returns a dictionary containing the occurrence of each note in the MIDI file.


    Args:
        mid (mido.MidiFile): The midi object to be analysed.

    Returns:
        Dict[int,int]: A dictionary with the keys being the MIDI note numbers (0 to 127), and the values being the
        number of occurences of the particular MIDI note.
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


def get_type_tally(mid: MidiFile) -> Dict[str, int]:
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


def get_start_offset(track: MidiTrack, ticks_per_beat: int) -> Tuple[float, int]:
    start_offset = 0
    tempo = bpm2tempo(120)
    first_note_on_ind = 0
    for i, message in enumerate(track):
        start_offset += tick2second(message.time, ticks_per_beat, tempo)
        if is_note_on(message):
            first_note_on_ind = i
            break
        elif message.type == "set_tempo":
            tempo = message.tempo

    return start_offset, first_note_on_ind


def get_end_offset(track: MidiTrack, ticks_per_beat: int) -> Tuple[float, int]:
    tempo = bpm2tempo(120)
    end_offset = 0
    last_note_off = 0
    last_note_off_ind = 0
    for i, message in enumerate(track):
        end_offset += tick2second(message.time, ticks_per_beat, tempo)
        if is_note_off(message):
            last_note_off = end_offset
            last_note_off_ind = i
        elif message.type == "set_tempo":
            tempo = message.tempo

    return last_note_off, last_note_off_ind


def get_chord_timeline(chord_track: MidiTrack) -> List[Tuple[Chord, int, int]]:
    chords = []
    on_dict = OrderedDict()
    # off_dict = defaultdict(list)
    curr_time = 0
    last_note_off_time = 0
    for i in range(len(chord_track)):
        curr_time += chord_track[i].time
        if is_note_on(chord_track[i]):
            if curr_time not in on_dict.keys():
                on_dict[curr_time] = []
            on_dict[curr_time].append(chord_track[i].note)
        elif is_note_off(chord_track[i]):
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
        chords.append((Chord(*note_list), time, end_times[i]))
        i += 1
    return chords


def get_note_timeline(track: MidiTrack, chord_track: Optional[mido.MidiTrack] = None) -> List[Note]:
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
    curr_ticks = 0
    for i in range(len(track)):
        if is_note_on(track[i]):
            # start of new note being played
            notes.append(Note(curr_ticks + track[i].time, -1, track[i].note, track[i].channel, None, i, None))
            last_note_dict[track[i].note] = len(notes) - 1
        elif is_note_off(track[i]):
            # note off (inc note on "running status")
            # naive: assume the previous note_on message was the one this note_off corresponds to
            # (not necessarily the case in polyphonic music)
            notes[last_note_dict[track[i].note]].end_time = curr_ticks + track[i].time  # set the last note's end time
            notes[last_note_dict[track[i].note]].end_message_index = i
        curr_ticks += track[i].time

    if chord_track is not None:
        chord_timeline = get_chord_timeline(chord_track)
        # naive (this is inefficient)
        for chord, chord_start, chord_end in chord_timeline:
            for note in notes:
                if note.start_time >= chord_start:
                    # test: and note.end_time <= chord_end
                    note.chord = Chord(*chord.to_midi_values())  # COPY

    return notes


def get_notes_in_time_range(track: MidiTrack, ticks_per_beat: int,
                            start: float = 0, end: float = float("inf"), allow_smaller: bool = True,
                            use_midi_times: bool = False) -> List[Note]:
    """
    Return all notes within the time (in seconds) range [start,end]

    Args:
        track: MidiTrack to get notes from
        ticks_per_beat: the number of Midi message "ticks" per quarter note
        start: The beginning of the time range (default: 0)
        end:  The end of the time range (default: inf (to the end of the track))
        allow_smaller: Whether to allow sets of notes that are smaller than the time range (for example, if the time range exceed the end of the song) (default: True). If False, returns the empty list [] if end goes over the end of the song
        use_midi_times: Whether to save notes with their MIDI tick values instead of the time in seconds (default: False)
    Returns:
        A list of notes in the time range [start,end]

    """
    if not allow_smaller:
        if end > get_end_offset(track, ticks_per_beat)[0]:
            return []

    notes = []
    last_note_dict = {}
    curr_time = 0
    curr_ticks = 0
    curr_tempo = bpm2tempo(120)

    for msg in track:
        curr_time += tick2second(msg.time, ticks_per_beat, curr_tempo)
        curr_ticks += msg.time
        if msg.type == "set_tempo":
            curr_tempo = msg.tempo

        if curr_time < start:
            continue
        elif curr_time > end:
            break
        elif is_note_on(msg):
            if use_midi_times:
                notes.append(Note(curr_ticks, -1, msg.note, msg.channel))
            else:
                notes.append(Note(curr_time, -1, msg.note, msg.channel))
            last_note_dict[msg.note] = len(notes) - 1
        elif is_note_off(msg):
            if msg.note in last_note_dict.keys():
                if use_midi_times:
                    notes[last_note_dict[msg.note]].end_time = curr_ticks
                else:
                    notes[last_note_dict[msg.note]].end_time = curr_time  # set the last note's end time
            else:
                if use_midi_times:
                    notes.append(Note(curr_ticks - msg.time, curr_ticks, msg.note, msg.channel))
                else:
                    notes.append(Note(float(start), curr_time, msg.note, msg.channel))

    if len(notes) > 0:  # limit note end to end of time period
        if notes[-1].end_time == -1:
            if use_midi_times:
                notes[-1].end_time = curr_ticks
            else:
                notes[-1].end_time = curr_time

    return notes


def get_track_signatures(track: MidiTrack) -> Tuple[List[Tuple[int, TimeSignature]], List[Tuple[int, KeySignature]]]:
    """
    Returns a list of key and time signatures in the MIDI track, and their positions within the track (in ticks)

    Args:
        track: The Midi track to check

    Returns:
        A Tuple of lists containing pairs of (time, signature) for both time and key signatures
    """
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


def get_track_tempo_changes(track: MidiTrack) -> List[Tuple[int, int]]:
    time = 0
    tempo_changes = []
    for message in track:
        time += message.time
        if message.type == "set_tempo":
            tempo_changes.append((time, message.tempo))

    return tempo_changes


def get_track_non_note_messages(track: MidiTrack) -> Deque[Tuple[int, Message]]:
    time = 0
    meta_messages = deque()
    for message in track:
        if message.is_meta or message.type == "control_change" or message.type == "program_change":
            meta_messages.append((time + message.time, message))
        time += message.time

    return meta_messages


def get_higher_pitch(pitch_class: str) -> str:
    if pitch_class == "G":
        return "A"
    else:
        return str(chr(ord(pitch_class) + 1))


def get_lower_pitch(pitch_class: str) -> str:
    if pitch_class == "A":
        return "G"
    else:
        return str(chr(ord(pitch_class) - 1))


def get_note_parts(note_str: str) -> Tuple[str, str, str]:
    key_regex = re.compile("([A-G])([#b])?(m)?")
    match = key_regex.match(note_str)
    pitch_class = match.group(1)
    tonality = match.group(2)
    minor_str = match.group(3) if match.group(3) == "m" else ""
    return pitch_class, tonality, minor_str


def get_correct_enharmonic(note_str: str) -> str:
    if note_str in constants.TWELVE_NOTE_SCALE_SHARP:
        return constants.TWELVE_NOTE_SCALE_ENHARMONIC[constants.TWELVE_NOTE_SCALE_SHARP.index(note_str)]
    else:
        return constants.TWELVE_NOTE_SCALE_ENHARMONIC[constants.TWELVE_NOTE_SCALE_FLAT.index(note_str)]


def transpose_keysig_up(msg) -> Optional[MetaMessage]:
    if msg.type == "key_signature":
        new_message = MetaMessage("key_signature")
        new_message.time = msg.time
        new_key = ""
        pitch_class, tonality, minor_str = get_note_parts(note_str=msg.key)
        if tonality == "b":
            new_key = pitch_class  # just need to add one semitone e.g Ab -> A
        elif tonality == "#":
            new_key = get_higher_pitch(pitch_class)
        else:
            if pitch_class == "E" or pitch_class == "B":
                new_key = get_higher_pitch(pitch_class)
            else:
                new_key = pitch_class + "#"

        new_message.key = get_correct_enharmonic(new_key) + minor_str
        return new_message
    else:
        return None


def transpose_keysig_down(msg) -> Optional[MetaMessage]:
    if msg.type == "key_signature":
        new_message = MetaMessage("key_signature")
        new_message.time = msg

        pitch_class, tonality, minor_str = get_note_parts(note_str=msg.key)
        if tonality == "#":
            new_message.key = msg.pitch_class  # just need to add one semitone e.g Ab -> A
        elif tonality == "b":
            new_message.key = get_lower_pitch(pitch_class)
        else:
            if pitch_class == "F" or pitch_class == "C":
                new_message.key = get_lower_pitch(pitch_class)
            else:
                new_message.key = get_correct_enharmonic(pitch_class + "b")

        msg.key += minor_str
        return new_message
    else:
        return None

