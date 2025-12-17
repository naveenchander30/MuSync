from rapidfuzz.fuzz import token_sort_ratio, partial_ratio
from .normalize import normalize

def score(query_name, query_artists, candidate):
    qn = normalize(query_name)
    cn = normalize(candidate["name"])

    name_score = token_sort_ratio(qn, cn)

    qa = [normalize(a) for a in query_artists]
    ca = [normalize(a) for a in candidate["artists"]]

    artist_score = sum(
        partial_ratio(a, b) > 80
        for a in qa for b in ca
    ) * 15

    penalty = max(0, len(candidate["name"]) - len(query_name)) * 0.5
    return name_score + artist_score - penalty
