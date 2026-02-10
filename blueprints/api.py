from flask import Blueprint, jsonify, request
from flask_login import current_user
import json
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/check-username')
def check_username():
    """Check if a username is available"""
    from utils.security import check_username_availability
    from models import slugify_username
    
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    # Slugify the username
    username = slugify_username(username)
    
    # If user is logged in and checking their own username, it's always "available"
    if current_user.is_authenticated and username.lower() == current_user.username.lower():
        return jsonify({'available': True, 'message': 'This is your current username', 'is_current': True})
    
    # Check availability
    available, message = check_username_availability(username)
    return jsonify({'available': available, 'message': message, 'is_current': False})

@api_bp.route('/states')
def get_states():
    """Get list of states for a country"""
    country = 'india'  # Default to India for now
    
    try:
        # Load locations data
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'locations.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        states = list(locations.get(country, {}).get('states', {}).keys())
        return jsonify({'states': states})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/districts')
def get_districts():
    """Get list of districts for a state"""
    state = request.args.get('state', '')
    country = 'india'
    
    if not state:
        return jsonify({'error': 'State parameter required'}), 400
    
    try:
        # Load locations data
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'locations.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        districts = locations.get(country, {}).get('states', {}).get(state, [])
        return jsonify({'districts': districts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
