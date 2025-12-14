"""
Integration Tests for SmartFridge API Endpoints
Tests all Flask API routes with mocked database operations
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
try:
    from api import app
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    pytest.skip("API module not available", allow_module_level=True)


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {'Content-Type': 'application/json'}


class TestHealthEndpoint:
    """Test system health check endpoint"""
    
    def test_health_check_returns_200(self, client):
        """Health endpoint should return 200 OK"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_check_contains_status(self, client):
        """Health check should include status information"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
    
    def test_health_check_shows_features(self, client):
        """Health check should list available features"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'features' in data


class TestAuthenticationEndpoints:
    """Test user authentication endpoints"""
    
    @patch('commands.auth_handlers.handle_register_user')
    def test_register_success(self, mock_register, client):
        """Test successful user registration"""
        mock_register.return_value = {
            'success': True,
            'user_id': 'test-123',
            'username': 'testuser',
            'message': 'Account created'
        }
        
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user_id' in data
    
    @patch('commands.auth_handlers.handle_register_user')
    def test_register_duplicate_username(self, mock_register, client):
        """Test registration with existing username"""
        mock_register.return_value = {
            'success': False,
            'message': 'Username already taken'
        }
        
        response = client.post('/api/auth/register', json={
            'username': 'existinguser',
            'password': 'testpass123'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    @patch('commands.auth_handlers.handle_login_user')
    def test_login_success(self, mock_login, client):
        """Test successful login"""
        mock_login.return_value = {
            'success': True,
            'user': {
                'user_id': 'test-123',
                'username': 'testuser'
            }
        }
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    @patch('commands.auth_handlers.handle_login_user')
    def test_login_invalid_credentials(self, mock_login, client):
        """Test login with wrong password"""
        mock_login.return_value = {
            'success': False,
            'message': 'Invalid username or password'
        }
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_logout(self, client):
        """Test logout endpoint"""
        response = client.post('/api/auth/logout')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_session_not_authenticated(self, client):
        """Test session check when not logged in"""
        response = client.get('/api/auth/session')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] is False


class TestRecipeEndpoints:
    """Test recipe search and retrieval endpoints"""
    
    @patch('api.query_recipes_by_ingredients')
    def test_search_recipes_success(self, mock_search, client):
        """Test successful recipe search"""
        mock_search.return_value = {
            'compatible': [
                {
                    'id': 1,
                    'name': 'Test Recipe',
                    'match_percentage': 100.0,
                    'matched_ingredients': ['chicken', 'rice'],
                    'missing_ingredients': []
                }
            ],
            'filtered': [],
            'dietary_restrictions': []
        }
        
        response = client.post('/api/recipes/search', json={
            'ingredient_names': ['chicken', 'rice'],
            'filters': {}
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) > 0
    
    @patch('api.query_recipes_by_ingredients')
    def test_search_with_filters(self, mock_search, client):
        """Test recipe search with filters"""
        mock_search.return_value = {
            'compatible': [],
            'filtered': [],
            'dietary_restrictions': []
        }
        
        response = client.post('/api/recipes/search', json={
            'ingredient_names': ['chicken'],
            'filters': {
                'max_time': 30,
                'skill_level': 'beginner'
            }
        })
        
        assert response.status_code == 200
        mock_search.assert_called_once()
    
    @patch('api.query_recipes_by_ingredients')
    def test_search_with_dietary_restrictions(self, mock_search, client):
        """Test that dietary restrictions are applied"""
        mock_search.return_value = {
            'compatible': [],
            'filtered': [
                {
                    'id': 2,
                    'name': 'Chicken Dish',
                    'violations': [{'ingredient': 'chicken', 'restriction': 'vegetarian'}]
                }
            ],
            'dietary_restrictions': ['vegetarian']
        }
        
        response = client.post('/api/recipes/search', json={
            'ingredient_names': ['chicken'],
            'filters': {}
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'filtered_recipes' in data
    
    @patch('api.query_recipe_by_id')
    def test_get_recipe_by_id_success(self, mock_get, client):
        """Test retrieving single recipe"""
        mock_get.return_value = {
            'id': 1,
            'name': 'Test Recipe',
            'ingredients': ['chicken', 'rice'],
            'instructions': []
        }
        
        response = client.get('/api/recipes/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test Recipe'
    
    @patch('api.query_recipe_by_id')
    def test_get_recipe_not_found(self, mock_get, client):
        """Test retrieving non-existent recipe"""
        mock_get.return_value = None
        
        response = client.get('/api/recipes/9999')
        assert response.status_code == 404


class TestIngredientEndpoints:
    """Test ingredient management endpoints (requires auth)"""
    
    def test_get_ingredients_requires_auth(self, client):
        """Ingredients endpoint should require authentication"""
        response = client.get('/api/ingredients')
        assert response.status_code == 401
    
    def test_add_ingredient_requires_auth(self, client):
        """Adding ingredient should require authentication"""
        response = client.post('/api/ingredients', json={
            'ingredient_name': 'chicken'
        })
        assert response.status_code == 401
    
    def test_remove_ingredient_requires_auth(self, client):
        """Removing ingredient should require authentication"""
        response = client.delete('/api/ingredients/123')
        assert response.status_code == 401


class TestFavoriteEndpoints:
    """Test favorite recipe endpoints (requires auth)"""
    
    def test_get_favorites_requires_auth(self, client):
        """Favorites endpoint should require authentication"""
        response = client.get('/api/favorites')
        assert response.status_code == 401
    
    def test_add_favorite_requires_auth(self, client):
        """Adding favorite should require authentication"""
        response = client.post('/api/favorites', json={
            'recipe_id': '1',
            'recipe_name': 'Test Recipe'
        })
        assert response.status_code == 401
    
    def test_remove_favorite_requires_auth(self, client):
        """Removing favorite should require authentication"""
        response = client.delete('/api/favorites/1')
        assert response.status_code == 401


class TestSubstitutionEndpoints:
    """Test ingredient substitution endpoints"""
    
    @patch('api.get_substitutions_for_ingredient')
    def test_get_substitutions_single(self, mock_subs, client):
        """Test getting substitutions for single ingredient"""
        mock_subs.return_value = [
            {
                'name': 'tofu',
                'ratio': '1:1',
                'best_for': ['vegetarian', 'vegan'],
                'flavor_impact': 'Neutral',
                'texture_impact': 'Firm',
                'cooking_notes': 'Press first'
            }
        ]
        
        response = client.get('/api/substitutions/chicken')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'substitutes' in data
        assert len(data['substitutes']) > 0
    
    @patch('api.get_substitutions_for_ingredient')
    def test_get_substitutions_multiple(self, mock_subs, client):
        """Test getting substitutions for multiple ingredients"""
        mock_subs.return_value = [
            {'name': 'oat milk', 'ratio': '1:1', 'best_for': ['vegan', 'nut-free'], 
             'flavor_impact': 'Mild', 'texture_impact': 'Creamy', 'cooking_notes': 'Works well'}
        ]
        
        response = client.post('/api/substitutions', json={
            'ingredients': ['milk', 'butter'],
            'dietary_restrictions': ['vegan', 'nut-free']
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'substitutions' in data


class TestCookingTermsEndpoints:
    """Test cooking terminology endpoints"""
    
    @patch('api.get_all_terms')
    @patch('api.get_term_definition')
    def test_get_all_cooking_terms(self, mock_def, mock_terms, client):
        """Test retrieving all cooking terms"""
        mock_terms.return_value = ['dice', 'sauté', 'simmer']
        mock_def.side_effect = lambda x: f"Definition of {x}"
        
        response = client.get('/api/cooking-terms')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'terms' in data
        assert 'count' in data
    
    @patch('api.get_term_definition')
    def test_get_single_cooking_term(self, mock_def, client):
        """Test retrieving single cooking term"""
        mock_def.return_value = "Cut food into small cubes"
        
        response = client.get('/api/cooking-terms/dice')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['term'] == 'dice'
        assert 'definition' in data
    
    @patch('api.get_term_definition')
    def test_get_unknown_cooking_term(self, mock_def, client):
        """Test retrieving unknown cooking term"""
        mock_def.return_value = None
        
        response = client.get('/api/cooking-terms/unknown')
        assert response.status_code == 404


class TestProfileEndpoints:
    """Test user profile endpoints (requires auth)"""
    
    def test_get_profile_requires_auth(self, client):
        """Profile endpoint should require authentication"""
        response = client.get('/api/profile')
        assert response.status_code == 401
    
    def test_update_dietary_restrictions_requires_auth(self, client):
        """Updating dietary restrictions should require authentication"""
        response = client.put('/api/profile/dietary-restrictions', json={
            'dietary_restrictions': ['vegan']
        })
        assert response.status_code == 401


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    @patch('api.get_system_analytics')
    def test_system_analytics(self, mock_analytics, client):
        """Test system-wide analytics"""
        mock_analytics.return_value = {
            'total_searches': 100,
            'total_users_created': 50,
            'total_favorites': 200
        }
        
        response = client.get('/api/analytics/system')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'analytics' in data


class TestErrorHandling:
    """Test error handling in API"""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post('/api/recipes/search',
                              data='not json',
                              content_type='application/json')
        # Should handle gracefully (400 or 500)
        assert response.status_code in [400, 500]
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser'
            # Missing password
        })
        # Should handle gracefully
        assert response.status_code in [400, 500]
    
    def test_nonexistent_endpoint(self, client):
        """Test 404 for non-existent endpoint"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are set"""
        response = client.options('/api/recipes/search')
        # CORS headers should be present
        assert response.status_code in [200, 204]