from rapidfuzz import fuzz
from rapidfuzz.utils import default_process

from pls.models import SearchQuery


def similarity(query: SearchQuery, title: str, artist: str) -> float:
    ptitle = default_process(title)
    partist = default_process(artist)
    pquery = (
        default_process(query)
        if isinstance(query, str)
        else (default_process(query[0]), default_process(query[1]))
    )

    split = title.split(" - ", 1)

    if len(split) == 2:
        pleft, pright = default_process(split[0]), default_process(split[1])

        return max(
            _similarity(pquery, pleft, pright),
            _similarity(pquery, pright, pleft),
            _similarity(pquery, ptitle, partist),
        )

    return _similarity(pquery, ptitle, partist)


def _similarity(query: SearchQuery, title: str, artist: str) -> float:
    if isinstance(query, str):
        return fuzz.token_ratio(query, f"{artist} {title}")

    artist_similarity = fuzz.ratio(query[0], artist)
    title_similarity = fuzz.ratio(query[1], title)

    return title_similarity * 0.5 + artist_similarity * 0.5
