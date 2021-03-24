from typing import Tuple


class VectorCandidate:
    def __init__(self, query_offset: float, window_modifier: float, candidate_offset: float,
                 song_ident: str):
        self.query_offset = query_offset
        self.window_modifier = window_modifier
        self.candidate_offset = candidate_offset
        self.song_ident = song_ident

    def get_candidate_segment_bounds(self, query_start: float, query_end: float) -> Tuple[float, float]:
        cand_start = self.candidate_offset - (self.query_offset - query_start) / self.window_modifier
        cand_end = self.candidate_offset + (query_end - self.query_offset) / self.window_modifier
        return cand_start, cand_end

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"song_ident {self.song_ident} query_offset {self.query_offset} " \
               f"window_mod {self.window_modifier} cand_offset {self.candidate_offset}"
