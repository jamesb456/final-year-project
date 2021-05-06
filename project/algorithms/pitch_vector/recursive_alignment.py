from math import floor
from typing import List, Tuple, Optional

from project.algorithms.core.note import Note

import numpy as np


def __dist(p1: Note, p2: Note, max_value: float = 10000) -> float:
    """
    The distance measure used to evaluate the "distance" between two notes.

    Args:
        p1: The first note.
        p2: The second note.
        max_value: The upper limit for what the distance can be at maximum.

    Returns:
        The "distance" between two notes
    """
    return min(((p1.pitch - p2.pitch) ** 2) + ((p1.start_time - p2.start_time) ** 2), max_value)


def __linear_scaling(query: List[Note], candidate: List[Note]) -> float:
    """
    A method for aligning two sequence of notes which only uses their relative positions. This didn't work
    so wasn't used in the final implementation.
    """
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
    """
    A dynamic programming algorithm for calculating the distance between a query and candidate list of notes. DTW
    tries to find the best alignment between the two sets of notes.

    Args:
        query: The series of notes from the query
        candidate: The series of notes from the candidate

    Returns:
        The distance between the query and candidate after DTW aligned the notes as best it could.
    """
    if len(query) == 0 or len(candidate) == 0:
        return 0
    dtw = np.zeros((len(query), len(candidate)), dtype=float)
    dtw += np.inf
    dtw[0, 0] = 0
    for i in range(1, len(query)):
        for j in range(1, len(candidate)):
            cost = __dist(query[i], candidate[j])
            dtw[i, j] = cost + min(dtw[i - 1, j],
                                   dtw[i, j - 1],
                                   dtw[i - 1, j - 1])

    return dtw[len(query) - 1, len(candidate) - 1]


def recursive_alignment(query: List[Note], candidate: List[Note],
                        scale_pairs: List[Tuple[float, float]], rec_depth: int = 1) -> float:
    """
    Return the distance between two sets of notes using recursive alignment.

    Args:
        query: The series of notes from the query
        candidate: The series of notes from the candidate
        scale_pairs: Points to split the query at
        rec_depth: The maximum depth of recursion allowed

    Returns:
        The distance between the query and candidate after recursive alignment aligned the notes as best it could.
    """
    i = 0
    j = floor(len(candidate) / 2)
    min_score: Optional[float] = None
    n1 = candidate[0:j]
    n2 = candidate[j:]
    for (sx, sy) in scale_pairs:
        k = floor(sx * len(query))
        q1 = query[0:k]
        q2 = query[k:]
        score = __dynamic_time_warping(q1, n1) + __dynamic_time_warping(q2, n2)
        if min_score is None or score < min_score:
            min_score = score
            i = k
    if rec_depth == 0:
        return min_score
    else:
        q1 = query[0:i]
        q2 = query[i:]
        return recursive_alignment(q1, n1, scale_pairs, rec_depth - 1) \
            + recursive_alignment(q2, n2, scale_pairs, rec_depth - 1)
