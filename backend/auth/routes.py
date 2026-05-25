from flask import Blueprint, request, jsonify, redirect, session, current_app
import secrets

from backend.auth.oauth_flows import OAuthFlows
from backend.auth.token_manager import TokenManager
from backend.database import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/spotify/login', methods=['GET'])
def spotify_login():
    """Initiate Spotify OAuth flow"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    # Get or create user
    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id, username=f"user_{user_id[:8]}")
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user_id
    
    login_url = OAuthFlows.spotify_login_url()
    return redirect(login_url)


@auth_bp.route('/spotify/callback', methods=['GET'])
def spotify_callback():
    """Handle Spotify OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    user_id = session.get('user_id')
    
    if not code or not state or not user_id:
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        OAuthFlows.handle_spotify_callback(code, state, user_id)
        return redirect(f"/dashboard?auth=spotify_success&user_id={user_id}")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500


@auth_bp.route('/ytmusic/login', methods=['GET'])
def ytmusic_login():
    """Initiate YouTube Music OAuth flow"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    # Get or create user
    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id, username=f"user_{user_id[:8]}")
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user_id
    
    login_url = OAuthFlows.ytmusic_login_url()
    return redirect(login_url)


@auth_bp.route('/ytmusic/callback', methods=['GET'])
def ytmusic_callback():
    """Handle YouTube Music OAuth callback"""
    authorization_response = request.url
    state = request.args.get('state')
    user_id = session.get('user_id')
    
    if not state or not user_id:
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        OAuthFlows.handle_ytmusic_callback(authorization_response, state, user_id)
        return redirect(f"/dashboard?auth=ytmusic_success&user_id={user_id}")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500


@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Get authentication status for a user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    spotify_valid = TokenManager.is_token_valid(user_id, 'spotify')
    ytmusic_valid = TokenManager.is_token_valid(user_id, 'ytmusic')
    
    return jsonify({
        "user_id": user_id,
        "spotify": spotify_valid,
        "ytmusic": ytmusic_valid
    })
