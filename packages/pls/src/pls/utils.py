from rapidfuzz import fuzz
from rapidfuzz.utils import default_process


def similarity(
    one: str, two: str, three: str | None = None, four: str | None = None
) -> float:
    if three and four:
        title, title2, artist, artist2 = one, two, three, four

        title_similarity = fuzz.token_set_ratio(
            default_process(title), default_process(title2)
        )

        artist_similarity = fuzz.token_set_ratio(
            default_process(artist), default_process(artist2)
        )

        return title_similarity * 0.4 + artist_similarity * 0.6

    return fuzz.token_set_ratio(default_process(one), default_process(two))
