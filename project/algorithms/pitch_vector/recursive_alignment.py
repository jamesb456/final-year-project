from math import floor
from typing import List, Tuple, Optional

from project.algorithms.core.note import Note

import numpy as np


def __dist(p1: float, p2: float, floor: float = 10000000000) -> float:
    return min((p1 - p2) ** 2, floor)


def __linear_scaling(query: List[Note], candidate: List[Note]) -> float:
    j = 0
    dist = 0
    scale = len(query)  # duration of candidate is always 1 (as it has been normalized)
    print(f"scale is {scale}")
    for i in range(len(candidate)):
        t = j + (scale * candidate[i].duration)
        # for k in range(int(j), int(t)):
        #     dist += __dist(query[k].pitch, candidate[i].pitch)
        print(f"\t t is {t}")
        j = t
    return -dist


def __dynamic_time_warping(query: List[Note], candidate: List[Note]) -> float:
    dtw = np.zeros((len(query), len(candidate)), dtype=float)
    dtw += np.inf
    dtw[0, 0] = 0
    for i in range(1, len(query)):
        for j in range(1, len(candidate)):
            cost = __dist(query[i].pitch, candidate[j].pitch)
            dtw[i, j] = cost + min(dtw[i - 1, j],
                                   dtw[i, j - 1],
                                   dtw[i - 1, j - 1])

    return dtw[len(query) - 1, len(candidate) - 1]


def recursive_alignment(query: List[Note], candidate: List[Note],
                        scale_pairs: List[Tuple[float, float]], rec_depth: int = 1) -> float:
    # i = 0
    # j = floor(len(candidate) / 2)
    # max_score: Optional[float] = None
    # n1 = candidate[0:j]
    # n2 = candidate[j:]
    # print(f"query is {query}")
    # print(f"candidate is {candidate}")
    # for (sx, sy) in scale_pairs:
    #     print(f"sx is {sx}")
    #     k = floor(sx * len(query))
    #     print(f"\tk is {k}")
    #     q1 = query[0:k]
    #     q2 = query[k:]
    #     score = __dynamic_time_warping(q1, n1) + __dynamic_time_warping(q2, n2)
    #     if max_score is None or score > max_score:
    #         max_score = score
    #         i = k
    # if rec_depth == 0:
    #     return max_score
    # else:
    #     q1 = query[0:i]
    #     q2 = query[i:]
    #     return recursive_alignment(q1, n1, scale_pairs, rec_depth - 1) \
    #            + recursive_alignment(q2, n2, scale_pairs, rec_depth - 1)
    return __dynamic_time_warping(query, candidate)
