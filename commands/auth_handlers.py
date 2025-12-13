# Authentication Command Handlers for User Profile System
# Handles user registration, login, and profile management

import uuid
import hashlib
from typing import Dict, Any, Optional
from database.db_connection import execute_update, execute_query
from events.event_bus import get_event_bus
from events.domain_events import UserCreatedEvent, UserProfileUpdatedEvent

def hash_password(password: str) -> str:
    # hash password using SHA-256 (in production, use bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    # verify password against hash
    return hash_password(password) == hashed

def handle_register_user(username: str, password: str) -> Dict[str, Any]:
    """
    Register a new user account
    
    Args:
        username: Desired username
        password: Plain text password (will be hashed)
    
    Returns:
        Result dict with success status and user_id or error message
    """
    event_bus = get_event_bus()
    
    # validation
    if not username or len(username) < 3:
        return {'success': False, 'message': 'Username must be at least 3 characters'}
    
    if not password or len(password) < 6:
        return {'success': False, 'message': 'Password must be at least 6 characters'}
    
    # check if username already exists
    check_query = "SELECT u_id FROM \"user\" WHERE username = %s;"
    existing = execute_query(check_query, (username,), fetch_one=True)
    
    if existing:
        return {'success': False, 'message': 'Username already taken'}
    
    # create user
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    
    insert_query = """
        INSERT INTO "user" (u_id, username, password, skill, diet)
        VALUES (%s, %s, %s, %s, %s);
    """
    execute_update(insert_query, (user_id, username, password_hash, 'beginner', None))
    
    # publish event
    event = UserCreatedEvent(user_id, username, [])
    event_bus.publish(event)
    
    return {
        'success': True,
        'user_id': user_id,
        'username': username,
        'message': 'Account created successfully'
    }

def handle_login_user(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user login
    
    Args:
        username: Username
        password: Plain text password
    
    Returns:
        Result dict with success status and user data or error message
    """
    # get user from database
    query = """
        SELECT u_id, username, password, skill, diet
        FROM "user"
        WHERE username = %s;
    """
    user = execute_query(query, (username,), fetch_one=True)
    
    if not user:
        return {'success': False, 'message': 'Invalid username or password'}
    
    # verify password
    if not verify_password(password, user['password']):
        return {'success': False, 'message': 'Invalid username or password'}
    
    # get user's dietary restrictions
    diet_list = user['diet'].split(',') if user.get('diet') else []
    
    return {
        'success': True,
        'user': {
            'user_id': user['u_id'],
            'username': user['username'],
            'skill_level': user['skill'],
            'dietary_restrictions': diet_list
        },
        'message': 'Login successful'
    }

def handle_update_user_password(user_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
    """
    Update user password
    
    Args:
        user_id: User ID
        old_password: Current password for verification
        new_password: New password
    
    Returns:
        Result dict with success status
    """
    # validation
    if not new_password or len(new_password) < 6:
        return {'success': False, 'message': 'New password must be at least 6 characters'}
    
    # get current password hash
    query = "SELECT password FROM \"user\" WHERE u_id = %s;"
    user = execute_query(query, (user_id,), fetch_one=True)
    
    if not user:
        return {'success': False, 'message': 'User not found'}
    
    # verify old password
    if not verify_password(old_password, user['password']):
        return {'success': False, 'message': 'Current password is incorrect'}
    
    # update password
    new_hash = hash_password(new_password)
    update_query = "UPDATE \"user\" SET password = %s WHERE u_id = %s;"
    execute_update(update_query, (new_hash, user_id))
    
    return {
        'success': True,
        'message': 'Password updated successfully'
    }

def handle_delete_user_account(user_id: str, password: str) -> Dict[str, Any]:
    """
    Delete user account (with all associated data via CASCADE)
    
    Args:
        user_id: User ID
        password: Password for confirmation
    
    Returns:
        Result dict with success status
    """
    # verify password
    query = "SELECT password FROM \"user\" WHERE u_id = %s;"
    user = execute_query(query, (user_id,), fetch_one=True)
    
    if not user:
        return {'success': False, 'message': 'User not found'}
    
    if not verify_password(password, user['password']):
        return {'success': False, 'message': 'Password is incorrect'}
    
    # delete user (CASCADE will delete all associated data)
    delete_query = "DELETE FROM \"user\" WHERE u_id = %s;"
    execute_update(delete_query, (user_id,))
    
    return {
        'success': True,
        'message': 'Account deleted successfully'
    }

def handle_get_user_equipment(user_id: str) -> Dict[str, Any]:
    """Get user's equipment list"""
    query = """
        SELECT a.name
        FROM has_app ha
        JOIN appliance a ON ha.name = a.name
        WHERE ha.u_id = %s
        ORDER BY a.name;
    """
    equipment = execute_query(query, (user_id,), fetch_all=True)
    
    return {
        'success': True,
        'equipment': [e['name'] for e in (equipment or [])]
    }

def handle_update_user_dietary_restrictions(user_id: str, dietary_restrictions: list) -> Dict[str, Any]:
    # update user's dietary restrictions
    event_bus = get_event_bus()
    
    # update in database
    diet_str = ','.join(dietary_restrictions) if dietary_restrictions else None
    query = "UPDATE \"user\" SET diet = %s WHERE u_id = %s;"
    execute_update(query, (diet_str, user_id))
    
    # publish event
    event = UserProfileUpdatedEvent(user_id, {'dietary_restrictions': dietary_restrictions})
    event_bus.publish(event)
    
    return {
        'success': True,
        'message': 'Dietary restrictions updated'
    }

def handle_update_user_skill_level(user_id: str, skill_level: str) -> Dict[str, Any]:
    # update user's skill level
    event_bus = get_event_bus()
    
    # validation
    valid_levels = ['beginner', 'intermediate', 'advanced']
    if skill_level.lower() not in valid_levels:
        return {'success': False, 'message': f'Skill level must be one of: {", ".join(valid_levels)}'}
    
    # update in database
    query = "UPDATE \"user\" SET skill = %s WHERE u_id = %s;"
    execute_update(query, (skill_level.lower(), user_id))
    
    # publish event
    event = UserProfileUpdatedEvent(user_id, {'skill_level': skill_level})
    event_bus.publish(event)
    
    return {
        'success': True,
        'message': 'Skill level updated'
    }