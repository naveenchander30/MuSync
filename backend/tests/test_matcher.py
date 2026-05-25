import pytest
from backend.sync.matcher import (
    normalize_text,
    calculate_artist_similarity,
    calculate_match_score,
    find_best_match
)


class TestNormalizeText:
    """Test text normalization"""
    
    def test_lowercase_conversion(self):
        assert normalize_text("HELLO") == "hello"
    
    def test_remove_special_chars(self):
        assert normalize_text("hello-world") == "hello world"
    
    def test_remove_punctuation(self):
        assert normalize_text("song!@#") == "song"
    
    def test_strip_whitespace(self):
        assert normalize_text("  hello  ") == "hello"
    
    def test_empty_string(self):
        assert normalize_text("") == ""
    
    def test_none_returns_empty(self):
        assert normalize_text(None) == ""


class TestArtistSimilarity:
    """Test artist similarity calculation"""
    def test_exact_match(self):
        artists_a = ["Taylor Swift"]
        artists_b = ["Taylor Swift"]
        score = calculate_artist_similarity(artists_a, artists_b)
        assert score == 1.0
    
    def test_partial_match(self):
        artists_a = ["Taylor Swift"]
        artists_b = ["T. Swift"]
        score = calculate_artist_similarity(artists_a, artists_b)
        assert 0.0 < score <= 1.0
    
    def test_no_match(self):
        artists_a = ["Taylor Swift"]
        artists_b = ["Ed Sheeran"]
        score = calculate_artist_similarity(artists_a, artists_b)
        assert score < 0.5
    
    def test_empty_artists(self):
        score = calculate_artist_similarity([], ["Artist"])
        assert score == 0.0
    
    def test_multiple_artists(self):
        artists_a = ["Artist1", "Artist2"]
        artists_b = ["Artist1", "Artist2"]
        score = calculate_artist_similarity(artists_a, artists_b)
        assert score == 1.0


class TestMatchScore:
    """Test match score calculation"""
    
    def test_exact_match_scores_high(self):
        query = {
            'name': 'Shape of You',
            'artists': ['Ed Sheeran'],
            'duration_ms': 233000
        }
        candidate = {
            'name': 'Shape of You',
            'artists': ['Ed Sheeran'],
            'duration_ms': 233000
        }
        score = calculate_match_score(query, candidate, threshold=0.90)
        assert score >= 0.90
    
    def test_similar_names_with_different_artists(self):
        query = {
            'name': 'Shape of You',
            'artists': ['Ed Sheeran'],
            'duration_ms': 233000
        }
        candidate = {
            'name': 'Shape of You',
            'artists': ['Different Artist'],
            'duration_ms': 233000
        }
        score = calculate_match_score(query, candidate, threshold=0.90)
        assert score < 0.90
    
    def test_below_threshold_returns_zero(self):
        query = {
            'name': 'Song A',
            'artists': ['Artist A'],
            'duration_ms': 200000
        }
        candidate = {
            'name': 'Song B',
            'artists': ['Artist B'],
            'duration_ms': 200000
        }
        score = calculate_match_score(query, candidate, threshold=0.90)
        assert score == 0.0
    
    def test_duration_tolerance(self):
        query = {
            'name': 'Test Song',
            'artists': ['Test Artist'],
            'duration_ms': 200000
        }
        candidate = {
            'name': 'Test Song',
            'artists': ['Test Artist'],
            'duration_ms': 204000  # 4 seconds difference
        }
        score = calculate_match_score(query, candidate, threshold=0.90)
        assert score >= 0.90


class TestFindBestMatch:
    """Test best match finding"""
    
    def test_finds_best_match(self):
        query = {
            'name': 'Bohemian Rhapsody',
            'artists': ['Queen'],
            'duration_ms': 354000
        }
        candidates = [
            {
                'name': 'Bohemian Rhapsody',
                'artists': ['Queen'],
                'duration_ms': 354000,
                'videoId': 'fJ9rUzIMcZQ'
            },
            {
                'name': 'Some Other Song',
                'artists': ['Other Artist'],
                'duration_ms': 200000,
                'videoId': 'other123'
            }
        ]
        best = find_best_match(query, candidates, threshold=0.90)
        assert best is not None
        assert best['videoId'] == 'fJ9rUzIMcZQ'
    
    def test_no_match_returns_none(self):
        query = {
            'name': 'Unknown Song',
            'artists': ['Unknown Artist'],
            'duration_ms': 200000
        }
        candidates = [
            {
                'name': 'Different Song',
                'artists': ['Different Artist'],
                'duration_ms': 200000,
                'videoId': 'diff123'
            }
        ]
        best = find_best_match(query, candidates, threshold=0.90)
        assert best is None
    
    def test_returns_highest_scoring(self):
        query = {
            'name': 'Test',
            'artists': ['Artist'],
            'duration_ms': 200000
        }
        candidates = [
            {
                'name': 'Test',
                'artists': ['Artist'],
                'duration_ms': 200000,
                'videoId': 'good'
            },
            {
                'name': 'Test Cover',
                'artists': ['Artist Cover'],
                'duration_ms': 200000,
                'videoId': 'ok'
            }
        ]
        best = find_best_match(query, candidates, threshold=0.90)
        assert best is not None
        assert best['videoId'] == 'good'
