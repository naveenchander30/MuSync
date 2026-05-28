import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.auth.oauth_flows import OAuthFlows


class TestSpotifyLoginURL:
    """Test Spotify OAuth login URL generation"""

    def test_returns_url(self, app):
        with app.test_request_context():
            url = OAuthFlows.spotify_login_url()
            assert url.startswith('https://accounts.spotify.com/authorize?')
            assert 'client_id=' in url
            assert 'response_type=code' in url
            assert 'redirect_uri=' in url
            assert 'scope=' in url
            assert 'state=' in url

    def test_includes_client_id_param(self, app):
        with app.test_request_context():
            url = OAuthFlows.spotify_login_url()
            assert 'client_id=' in url

    def test_includes_redirect_uri(self, app):
        with app.test_request_context():
            url = OAuthFlows.spotify_login_url()
            assert 'redirect_uri=' in url
            assert 'auth%2Fspotify%2Fcallback' in url

    def test_sets_session_state(self, app):
        with app.test_request_context():
            from flask import session
            assert 'spotify_state' not in session
            OAuthFlows.spotify_login_url()
            assert 'spotify_state' in session
            assert len(session['spotify_state']) > 0


class TestYtMusicLoginURL:
    """Test YouTube Music OAuth login URL generation"""

    def test_returns_url(self, app):
        with app.test_request_context():
            url = OAuthFlows.ytmusic_login_url()
            assert url is not None
            assert url.startswith('https://accounts.google.com/o/oauth2/auth')

    def test_sets_session_state(self, app):
        with app.test_request_context():
            from flask import session
            assert 'ytmusic_state' not in session
            OAuthFlows.ytmusic_login_url()
            assert 'ytmusic_state' in session
            assert len(session['ytmusic_state']) > 0


class TestSpotifyCallback:
    """Test Spotify OAuth callback handling"""

    def test_invalid_state_raises_error(self, app):
        with app.test_request_context():
            with pytest.raises(ValueError, match="Invalid OAuth state"):
                OAuthFlows.handle_spotify_callback(
                    authorization_code='code123',
                    state='wrong_state',
                    user_id='test_user'
                )

    @patch('backend.auth.oauth_flows.requests.post')
    def test_successful_token_exchange(self, mock_post, app, default_user):
        with app.test_request_context():
            from flask import session
            OAuthFlows.spotify_login_url()
            state = session['spotify_state']

            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {
                'access_token': 'access123',
                'refresh_token': 'refresh123',
                'expires_in': 3600,
                'scope': 'playlist-read-private'
            }
            mock_post.return_value = mock_response

            result = OAuthFlows.handle_spotify_callback(
                authorization_code='code123',
                state=state,
                user_id='test_user'
            )
            assert result is True

    @patch('backend.auth.oauth_flows.requests.post')
    def test_failed_token_exchange_raises_error(self, mock_post, app, default_user):
        with app.test_request_context():
            from flask import session
            OAuthFlows.spotify_login_url()
            state = session['spotify_state']

            mock_response = MagicMock()
            mock_response.ok = False
            mock_response.text = 'error'
            mock_post.return_value = mock_response

            with pytest.raises(Exception, match="Spotify token exchange failed"):
                OAuthFlows.handle_spotify_callback(
                    authorization_code='bad_code',
                    state=state,
                    user_id='test_user'
                )
