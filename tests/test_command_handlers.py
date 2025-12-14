"""
Unit Tests for Command Handlers
Tests write operations with mocked database
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from commands.command_handlers import (
        handle_add_ingredient,
        handle_remove_ingredient,
        handle_favorite_recipe,
        handle_unfavorite_recipe,
        handle_update_appliances
    )
    from commands.auth_handlers import (
        handle_register_user,
        handle_login_user,
        handle_update_user_password
    )
    COMMANDS_AVAILABLE = True
except ImportError:
    COMMANDS_AVAILABLE = False
    pytest.skip("Command handlers not available", allow_module_level=True)


class TestAddIngredient:
    """Test adding ingredients to user pantry"""
    
    @patch('commands.command_handlers.execute_update')
    @patch('commands.command_handlers.execute_query')
    def test_add_new_ingredient(self, mock_query, mock_update):
        """Test adding a new ingredient"""
        # Mock user exists
        mock_query.side_effect = [
            {'u_id': 'user-123'},  # user exists
            None,  # ingredient doesn't exist
            {'i_id': 1}  # new ingredient created
        ]
        mock_update.return_value = 1
        
        result = handle_add_ingredient('user-123', 'chicken', 2.0)
        
        assert result['success'] is True
        assert 'ingredient_id' in result
    
    @patch('commands.command_handlers.execute_query')
    def test_add_ingredient_user_not_found(self, mock_query):
        """Test adding ingredient when user doesn't exist"""
        mock_query.return_value = None
        
        result = handle_add_ingredient('nonexistent', 'chicken', 1.0)
        
        assert result['success'] is False
        assert 'not found' in result['message'].lower()
    
    @patch('commands.command_handlers.execute_update')
    @patch('commands.command_handlers.execute_query')
    def test_add_ingredient_with_expiration(self, mock_query, mock_update):
        """Test adding ingredient with expiration date"""
        mock_query.side_effect = [
            {'u_id': 'user-123'},
            {'i_id': 1}
        ]
        mock_update.return_value = 1
        
        result = handle_add_ingredient('user-123', 'milk', 1.0, exp_date='2024-12-31')
        
        assert result['success'] is True


class TestRemoveIngredient:
    """Test removing ingredients from pantry"""
    
    @patch('commands.command_handlers.execute_update')
    def test_remove_existing_ingredient(self, mock_update):
        """Test removing an existing ingredient"""
        mock_update.return_value = 1  # 1 row deleted
        
        result = handle_remove_ingredient('user-123', '1')
        
        assert result['success'] is True
    
    @patch('commands.command_handlers.execute_update')
    def test_remove_nonexistent_ingredient(self, mock_update):
        """Test removing ingredient that doesn't exist"""
        mock_update.return_value = 0  # 0 rows deleted
        
        result = handle_remove_ingredient('user-123', '999')
        
        assert result['success'] is False


class TestFavoriteRecipe:
    """Test favoriting recipes"""
    
    @patch('commands.command_handlers.execute_update')
    def test_favorite_new_recipe(self, mock_update):
        """Test favoriting a recipe for the first time"""
        mock_update.return_value = 1
        
        result = handle_favorite_recipe('user-123', '1', 'Test Recipe')
        
        assert result['success'] is True
    
    @patch('commands.command_handlers.execute_update')
    def test_favorite_already_favorited(self, mock_update):
        """Test favoriting an already favorited recipe"""
        mock_update.return_value = 0  # ON CONFLICT DO NOTHING
        
        result = handle_favorite_recipe('user-123', '1', 'Test Recipe')
        
        assert result['success'] is False


class TestUnfavoriteRecipe:
    """Test unfavoriting recipes"""
    
    @patch('commands.command_handlers.execute_update')
    def test_unfavorite_existing(self, mock_update):
        """Test unfavoriting a favorited recipe"""
        mock_update.return_value = 1
        
        result = handle_unfavorite_recipe('user-123', '1')
        
        assert result['success'] is True
    
    @patch('commands.command_handlers.execute_update')
    def test_unfavorite_not_favorited(self, mock_update):
        """Test unfavoriting a recipe that wasn't favorited"""
        mock_update.return_value = 0
        
        result = handle_unfavorite_recipe('user-123', '1')
        
        assert result['success'] is False


class TestUpdateAppliances:
    """Test updating user appliances"""
    
    @patch('commands.command_handlers.execute_update')
    def test_update_appliances_list(self, mock_update):
        """Test updating user's appliances"""
        mock_update.return_value = 1
        
        appliances = ['pan', 'oven', 'blender']
        result = handle_update_appliances('user-123', appliances)
        
        assert result['success'] is True
    
    @patch('commands.command_handlers.execute_update')
    def test_clear_all_appliances(self, mock_update):
        """Test clearing all appliances"""
        mock_update.return_value = 0
        
        result = handle_update_appliances('user-123', [])
        
        assert result['success'] is True


class TestUserRegistration:
    """Test user registration"""
    
    @patch('commands.auth_handlers.execute_update')
    @patch('commands.auth_handlers.execute_query')
    def test_register_new_user(self, mock_query, mock_update):
        """Test successful user registration"""
        mock_query.return_value = None  # username not taken
        mock_update.return_value = 1
        
        result = handle_register_user('newuser', 'password123')
        
        assert result['success'] is True
        assert 'user_id' in result
    
    @patch('commands.auth_handlers.execute_query')
    def test_register_duplicate_username(self, mock_query):
        """Test registration with existing username"""
        mock_query.return_value = {'u_id': 'existing'}
        
        result = handle_register_user('existinguser', 'password123')
        
        assert result['success'] is False
        assert 'already taken' in result['message'].lower()
    
    def test_register_invalid_username(self):
        """Test registration with invalid username"""
        result = handle_register_user('ab', 'password123')  # too short
        
        assert result['success'] is False
    
    def test_register_invalid_password(self):
        """Test registration with invalid password"""
        result = handle_register_user('validuser', '123')  # too short
        
        assert result['success'] is False


class TestUserLogin:
    """Test user login"""
    
    @patch('commands.auth_handlers.execute_query')
    @patch('commands.auth_handlers.verify_password')
    def test_login_success(self, mock_verify, mock_query):
        """Test successful login"""
        mock_query.return_value = {
            'u_id': 'user-123',
            'username': 'testuser',
            'password': 'hashed_password',
            'skill': 'beginner',
            'diet': None
        }
        mock_verify.return_value = True
        
        result = handle_login_user('testuser', 'correctpass')
        
        assert result['success'] is True
        assert 'user' in result
    
    @patch('commands.auth_handlers.execute_query')
    def test_login_user_not_found(self, mock_query):
        """Test login with non-existent user"""
        mock_query.return_value = None
        
        result = handle_login_user('nonexistent', 'password')
        
        assert result['success'] is False
    
    @patch('commands.auth_handlers.execute_query')
    @patch('commands.auth_handlers.verify_password')
    def test_login_wrong_password(self, mock_verify, mock_query):
        """Test login with wrong password"""
        mock_query.return_value = {
            'u_id': 'user-123',
            'username': 'testuser',
            'password': 'hashed_password',
            'skill': 'beginner',
            'diet': None
        }
        mock_verify.return_value = False
        
        result = handle_login_user('testuser', 'wrongpass')
        
        assert result['success'] is False


class TestPasswordUpdate:
    """Test password update"""
    
    @patch('commands.auth_handlers.execute_update')
    @patch('commands.auth_handlers.execute_query')
    @patch('commands.auth_handlers.verify_password')
    def test_update_password_success(self, mock_verify, mock_query, mock_update):
        """Test successful password update"""
        mock_query.return_value = {'password': 'old_hash'}
        mock_verify.return_value = True
        mock_update.return_value = 1
        
        result = handle_update_user_password('user-123', 'oldpass', 'newpass123')
        
        assert result['success'] is True
    
    @patch('commands.auth_handlers.execute_query')
    @patch('commands.auth_handlers.verify_password')
    def test_update_password_wrong_old(self, mock_verify, mock_query):
        """Test password update with wrong old password"""
        mock_query.return_value = {'password': 'old_hash'}
        mock_verify.return_value = False
        
        result = handle_update_user_password('user-123', 'wrongold', 'newpass123')
        
        assert result['success'] is False
    
    def test_update_password_too_short(self):
        """Test password update with invalid new password"""
        result = handle_update_user_password('user-123', 'oldpass', '123')
        
        assert result['success'] is False


class TestEventPublishing:
    """Test that commands publish events"""
    
    @patch('commands.command_handlers.get_event_bus')
    @patch('commands.command_handlers.execute_update')
    @patch('commands.command_handlers.execute_query')
    def test_add_ingredient_publishes_event(self, mock_query, mock_update, mock_bus):
        """Test that adding ingredient publishes event"""
        mock_query.side_effect = [
            {'u_id': 'user-123'},
            {'i_id': 1}
        ]
        mock_update.return_value = 1
        mock_event_bus = MagicMock()
        mock_bus.return_value = mock_event_bus
        
        handle_add_ingredient('user-123', 'chicken', 1.0)
        
        # Event should be published
        assert mock_event_bus.publish.called
    
    @patch('commands.auth_handlers.get_event_bus')
    @patch('commands.auth_handlers.execute_update')
    @patch('commands.auth_handlers.execute_query')
    def test_registration_publishes_event(self, mock_query, mock_update, mock_bus):
        """Test that registration publishes event"""
        mock_query.return_value = None
        mock_update.return_value = 1
        mock_event_bus = MagicMock()
        mock_bus.return_value = mock_event_bus
        
        handle_register_user('newuser', 'password123')
        
        assert mock_event_bus.publish.called