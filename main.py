"""
Temp file, delete later
"""

import mido

import project.visualisation.graph as gr
import project.util.midtools as mdt

from typing import List


md = mido.MidiFile("mid/test_midi_3.mid")
print(f"For midi {md.filename}: Ticks per beat: {md.ticks_per_beat}")
tracks: List[mido.MidiTrack] = md.tracks



# for msg in tracks[0]:
#     if msg.type == "note_on":
#         print(f"""Note:{mdt.number_to_scientific_pitch(msg.note)}
# Time until msg played (beat): {msg.time / md.ticks_per_beat} Velocity {msg.velocity}""")
print(tracks[0].name)
gr.pitch_time_graph(tracks[0], md.ticks_per_beat)
gr.lbdm_graph(tracks[0])
