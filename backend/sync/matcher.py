from rapidfuzz import fuzz
import re


def normalize_text(text: str) -> str:
    """Normalize text for matching while preserving important info"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove common separators but keep words
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def calculate_artist_similarity(query_artists: list, candidate_artists: list) -> float:
    """Calculate artist similarity score (0.0 - 1.0)"""
    if not query_artists or not candidate_artists:
        return 0.0
    
    # Normalize artist names
    q_artists = [normalize_text(a) for a in query_artists]
    c_artists = [normalize_text(a) for a in candidate_artists]
    
    # Calculate best match for each query artist
    scores = []
    for qa in q_artists:
        best_match = 0
        for ca in c_artists:
            score = fuzz.partial_ratio(qa, ca) / 100.0
            best_match = max(best_match, score)
        scores.append(best_match)
    
    # Return average similarity
    return sum(scores) / len(scores)


def calculate_match_score(query_track, candidate_track, threshold: float = 0.90) -> float:
    """
    Calculate match score between two tracks using weighted scoring
    
    Args:
        query_track: Dict with 'name', 'artists', 'duration_ms'
        candidate_track: Dict with 'name', 'artists', 'duration_ms'
        threshold: Minimum score to consider a match (default 0.90 for conservative)
    
    Returns:
        float: Match score (0.0 - 1.0), or 0.0 if below threshold
    """
    # 1. Name matching (60% weight)
    query_name = normalize_text(query_track.get('name', ''))
    candidate_name = normalize_text(candidate_track.get('name', ''))
    
    # Use token_sort_ratio for better name matching
    name_score = fuzz.token_sort_ratio(query_name, candidate_name) / 100.0
    
    # 2. Artist matching (35% weight)
    query_artists = query_track.get('artists', [])
    candidate_artists = candidate_track.get('artists', [])
    
    artist_score = calculate_artist_similarity(query_artists, candidate_artists)
    
    # 3. Duration check (5% weight)
    query_duration = query_track.get('duration_ms', 0)
    candidate_duration = candidate_track.get('duration_ms', 0)
    
    if query_duration > 0 and candidate_duration > 0:
        duration_diff = abs(query_duration - candidate_duration)
        # Within 5 seconds = perfect match
        duration_score = 1.0 if duration_diff < 5000 else 0.5
    else:
        duration_score = 0.5  # Neutral if duration not available
    
    # Weighted combination
    total_score = (
        (name_score * 0.60) +
        (artist_score * 0.35) +
        (duration_score * 0.05)
    )
    
    # Return 0 if below threshold
    return total_score if total_score >= threshold else 0.0


def find_best_match(query_track, search_results, threshold: float = 0.90):
    """
    Find best matching track from search results
    
    Args:
        query_track: Dict with 'name', 'artists', 'duration_ms'
        search_results: List of candidate track dicts
        threshold: Minimum confidence threshold
    
    Returns:
        Best matching track dict or None if no confident match
    """
    best_match = None
    best_score = 0
    
    for candidate in search_results:
        score = calculate_match_score(query_track, candidate, threshold)
        
        if score > best_score:
            best_score = score
            best_match = candidate
    
    return best_match if best_score >= threshold else None
