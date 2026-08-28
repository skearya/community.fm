from rapidfuzz import fuzz
from rapidfuzz.utils import default_process

from pls.models import SearchQuery

type Info = None | tuple[str, str]


def similarity(
    query: SearchQuery, artist: str, title: str, p=default_process
) -> tuple[float, Info]:
    pquery = p(query) if isinstance(query, str) else (p(query[0]), p(query[1]))
    partist = p(artist)
    ptitle = p(title)

    candidates: list[tuple[float, Info]] = [(score(pquery, partist, ptitle), None)]

    match title.split(" - ", 1):
        case [left, right]:
            pleft, pright = p(left), p(right)

            candidates.append((score(pquery, pleft, pright), (left, right)))
            candidates.append((score(pquery, pright, pleft), (right, left)))

    return max(candidates, key=lambda candidate: candidate[0])


def score(query: SearchQuery, artist: str, title: str) -> float:
    if isinstance(query, tuple):
        return title_artist_score(*query, artist, title)
    else:
        return query_score(query, f"{artist} {title}")


def query_score(q1: str, q2: str) -> float:
    return fuzz.WRatio(q1, q2)


def title_artist_score(a1: str, t1: str, a2: str, t2: str) -> float:
    title_similarity = fuzz.WRatio(t1, t2)
    artist_similarity = fuzz.WRatio(a1, a2)

    return title_similarity * 0.5 + artist_similarity * 0.5
