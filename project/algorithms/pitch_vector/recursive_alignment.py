from typing import List, Tuple

from project.algorithms.core.note import Note

import numpy as np


def __dist(p1: float, p2: float, floor: float = 10000000000) -> float:
    return min((p1 - p2) ** 2, floor)


def __linear_scaling(query: List[Note], candidate: List[Note]) -> float:
    j = 0
    dist = 0

    for c_note in candidate:
        t = j + c_note.duration
        if j + 1 < len(query) and t+1 < len(query):
            for k in range(int(j+1), int(t+1)):
                dist += __dist(query[k].pitch, c_note.pitch)
        else:
            break
        j = t + 1

    return -dist


def __dynamic_time_warping(query: List[Note], candidate: List[Note]) -> float:
    dtw = np.zeros((len(query), len(candidate)), dtype=float)
    dtw += np.inf
    dtw[0, 0] = 0
    for i in range(1, len(query)):
        for j in range(1, len(candidate)):
            cost = __dist(query[i].pitch, candidate[j].pitch)
            dtw[i, j] = cost + min(dtw[i-1, j],
                                   dtw[i, j-1],
                                   dtw[i-1, j-1])

    return dtw[len(query) - 1, len(candidate) - 1]


def recursive_alignment(query: List[Note], candidate: List[Note],
                        scale_pairs: List[Tuple[float,float]], rec_depth: int = 2) -> float:
    # temporary test: could use as comparison as well?
    return __dynamic_time_warping(query, candidate)
    # return __dynamic_time_warping(query, candidate)
