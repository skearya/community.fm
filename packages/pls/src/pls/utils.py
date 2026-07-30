from rapidfuzz import fuzz
from rapidfuzz.utils import default_process

from pls.models import SearchQuery


def similarity(query: SearchQuery, artist: str, title: str, p=default_process) -> float:
    pquery = p(query) if isinstance(query, str) else (p(query[0]), p(query[1]))
    partist = p(artist)
    ptitle = p(title)

    return similarity_processed(pquery, partist, ptitle)


def similarity_processed(
    query: SearchQuery, artist: str, title: str, split=True
) -> float:
    candidates: list[float] = []

    if isinstance(query, str):
        candidates.append(query_similarity(query, f"{artist} {title}"))
    else:
        candidates.append(title_artist_similarity(*query, artist, title))
        candidates.append(query_similarity(" ".join(query), f"{artist} {title}"))

    if split:
        items = title.split(" - ", 1)

        if len(items) == 2:
            candidates.append(similarity_processed(query, *items, split=False))
            candidates.append(similarity_processed(query, *items[::-1], split=False))

    return max(candidates)


def query_similarity(q1: str, q2: str) -> float:
    return fuzz.WRatio(q1, q2)


def title_artist_similarity(a1: str, t1: str, a2: str, t2: str) -> float:
    title_similarity = fuzz.WRatio(t1, t2)
    artist_similarity = fuzz.WRatio(a1, a2)

    return title_similarity * 0.5 + artist_similarity * 0.5
