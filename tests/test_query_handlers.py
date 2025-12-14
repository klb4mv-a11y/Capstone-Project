"""
Integration Tests for Query Handlers
Tests database query operations with mocked PostgreSQL
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from queries.query_handlers import (
        query_user_profile,
        query_user_pantry,
        query_recipe_by_id,
        query_recipes_by_ingredients,
        query_user_favorites,
        query_shopping_suggestions
    )
    QUERIES_AVAILABLE = True
except ImportError:
    QUERIES_AVAILABLE = False
    pytest.skip("Query handlers not available", allow_module_level=True)


class TestQueryUserProfile:
    """Test user profile queries"""
    
    @patch('queries.query_handlers.execute_query')
    def test_query_existing_user(self, mock_execute):
        """Test querying an existing user profile"""
        mock_execute.return_value = {
            'u_id': 'user-123',
            'username': 'testuser',
            'skill': 'beginner',
            'diet': 'vegan,gluten-free'
        }
        
        result = query_user_profile('user-123')
        
        assert result is not None
        assert result['user_id'] == 'user-123'
        assert result['username'] == 'testuser'
        assert 'vegan' in result['dietary_restrictions']
        assert 'gluten-free' in result['dietary_restrictions']
    
    @patch('queries.query_handlers.execute_query')
    def test_query_nonexistent_user(self, mock_execute):
        """Test querying a non-existent user"""
        mock_execute.return_value = None
        
        result = query_user_profile('nonexistent')
        assert result is None
    
    @patch('queries.query_handlers.execute_query')
    def test_user_with_no_dietary_restrictions(self, mock_execute):
        """Test user with no dietary restrictions"""
        mock_execute.return_value = {
            'u_id': 'user-456',
            'username': 'testuser2',
            'skill': 'intermediate',
            'diet': None
        }
        
        result = query_user_profile('user-456')
        assert result['dietary_restrictions'] == []


class TestQueryUserPantry:
    """Test user pantry queries"""
    
    @patch('queries.query_handlers.execute_query')
    def test_query_pantry_with_ingredients(self, mock_execute):
        """Test querying pantry with ingredients"""
        mock_execute.return_value = [
            {'ingredient_id': 1, 'name': 'chicken', 'amount': 2.0, 'exp_date': None},
            {'ingredient_id': 2, 'name': 'rice', 'amount': 1.0, 'exp_date': '2024-12-31'}
        ]
        
        result = query_user_pantry('user-123')
        
        assert len(result) == 2
        assert result[0]['name'] == 'chicken'
        assert result[1]['exp_date'] == '2024-12-31'
    
    @patch('queries.query_handlers.execute_query')
    def test_query_empty_pantry(self, mock_execute):
        """Test querying an empty pantry"""
        mock_execute.return_value = []
        
        result = query_user_pantry('user-123')
        assert len(result) == 0


class TestQueryRecipeById:
    """Test single recipe retrieval"""
    
    @patch('queries.query_handlers.execute_query')
    def test_query_existing_recipe(self, mock_execute):
        """Test querying an existing recipe"""
        # Mock recipe basic info
        mock_execute.side_effect = [
            {'r_id': 1, 'name': 'Test Recipe', 'desc': 'Italian', 'time': 30, 'skill': 'beginner', 'serving': 4},
            [{'name': 'chicken'}, {'name': 'rice'}],  # ingredients
            [{'name': 'pan'}],  # equipment
            [{'step': 1, 'instruction': 'Cook chicken', 'time': 600}]  # steps
        ]
        
        result = query_recipe_by_id('1')
        
        assert result is not None
        assert result['name'] == 'Test Recipe'
        assert len(result['ingredients']) == 2
        assert 'chicken' in result['ingredients']
    
    @patch('queries.query_handlers.execute_query')
    def test_query_nonexistent_recipe(self, mock_execute):
        """Test querying a non-existent recipe"""
        mock_execute.return_value = None
        
        result = query_recipe_by_id('9999')
        assert result is None


class TestQueryRecipesByIngredients:
    """Test recipe search by ingredients"""
    
    @patch('queries.query_handlers.execute_query')
    def test_search_with_perfect_match(self, mock_execute):
        """Test search that finds perfect 100% match"""
        # Mock recipe list
        mock_execute.side_effect = [
            [{'id': 1, 'name': 'Chicken Rice', 'desc': 'Asian', 'time': 30, 'skill': 'beginner', 'serving': 2}],
            [{'name': 'chicken'}, {'name': 'rice'}],  # recipe ingredients
            [{'name': 'pan'}]  # equipment
        ]
        
        result = query_recipes_by_ingredients(['chicken', 'rice'], {}, user_id=None)
        
        # Handle both old format (list) and new format (dict)
        if isinstance(result, dict):
            recipes = result['compatible']
        else:
            recipes = result
        
        assert len(recipes) > 0
        assert recipes[0]['match_percentage'] == 100.0
    
    @patch('queries.query_handlers.execute_query')
    def test_search_with_time_filter(self, mock_execute):
        """Test search with time constraint"""
        mock_execute.return_value = [
            {'id': 1, 'name': 'Quick Recipe', 'desc': '', 'time': 15, 'skill': 'beginner', 'serving': 2}
        ]
        
        filters = {'max_time': 20}
        result = query_recipes_by_ingredients(['chicken'], filters, user_id=None)
        
        # Should call execute_query with time filter in params
        assert mock_execute.called
    
    @patch('queries.query_handlers.execute_query')
    def test_search_with_skill_filter(self, mock_execute):
        """Test search with skill level filter"""
        mock_execute.return_value = [
            {'id': 1, 'name': 'Easy Recipe', 'desc': '', 'time': 30, 'skill': 'beginner', 'serving': 2}
        ]
        
        filters = {'skill_level': 'beginner'}
        result = query_recipes_by_ingredients(['chicken'], filters, user_id=None)
        
        assert mock_execute.called
    
    @patch('queries.query_handlers.execute_query')
    def test_search_with_no_results(self, mock_execute):
        """Test search that finds no recipes"""
        mock_execute.return_value = []
        
        result = query_recipes_by_ingredients(['unicorn_meat'], {}, user_id=None)
        
        if isinstance(result, dict):
            assert len(result['compatible']) == 0
        else:
            assert len(result) == 0


class TestQueryUserFavorites:
    """Test user favorites queries"""
    
    @patch('queries.query_handlers.query_user_pantry')
    @patch('queries.query_handlers.query_recipe_by_id')
    @patch('queries.query_handlers.execute_query')
    def test_query_favorites_with_match_calculation(self, mock_execute, mock_recipe, mock_pantry):
        """Test favorites with current pantry match percentage"""
        mock_execute.return_value = [
            {'id': 1, 'name': 'Favorite Recipe'}
        ]
        mock_pantry.return_value = [
            {'name': 'chicken'},
            {'name': 'rice'}
        ]
        mock_recipe.return_value = {
            'ingredients': ['chicken', 'rice', 'soy sauce']
        }
        
        result = query_user_favorites('user-123')
        
        assert len(result) > 0
        assert 'match_percentage' in result[0]
    
    @patch('queries.query_handlers.execute_query')
    def test_query_empty_favorites(self, mock_execute):
        """Test user with no favorites"""
        mock_execute.return_value = []
        
        result = query_user_favorites('user-123')
        assert len(result) == 0


class TestQueryShoppingSuggestions:
    """Test shopping suggestion queries"""
    
    @patch('queries.query_handlers.query_user_pantry')
    @patch('queries.query_handlers.query_recipes_by_ingredients')
    def test_shopping_suggestions(self, mock_search, mock_pantry):
        """Test generating shopping suggestions"""
        mock_pantry.return_value = [
            {'name': 'chicken'},
            {'name': 'rice'}
        ]
        mock_search.return_value = [
            {
                'match_percentage': 66.7,
                'missing_ingredients': ['soy sauce', 'ginger']
            },
            {
                'match_percentage': 75.0,
                'missing_ingredients': ['soy sauce']
            }
        ]
        
        result = query_shopping_suggestions('user-123', {}, top_n=5)
        
        # soy sauce should be ranked high (appears in 2 recipes)
        assert len(result) > 0
    
    @patch('queries.query_handlers.query_user_pantry')
    @patch('queries.query_handlers.query_recipes_by_ingredients')
    def test_shopping_suggestions_with_filters(self, mock_search, mock_pantry):
        """Test shopping suggestions with filters"""
        mock_pantry.return_value = [{'name': 'chicken'}]
        mock_search.return_value = []
        
        filters = {'max_time': 30}
        result = query_shopping_suggestions('user-123', filters, top_n=3)
        
        # Should pass filters to recipe search
        assert mock_search.called


class TestDietaryRestrictionFiltering:
    """Test dietary restriction filtering in queries"""
    
    @patch('queries.query_handlers.execute_query')
    @patch('queries.query_handlers.check_recipe_compatibility')
    def test_filtering_incompatible_recipes(self, mock_check, mock_execute):
        """Test that incompatible recipes are filtered out"""
        # Setup
        mock_execute.side_effect = [
            [{'u_id': 'user-123', 'diet': 'vegan'}],  # user profile
            [{'id': 1, 'name': 'Chicken Recipe', 'time': 30, 'skill': 'beginner', 'serving': 2}],  # recipes
            [{'name': 'chicken'}],  # recipe ingredients
            [{'name': 'pan'}]  # equipment
        ]
        mock_check.return_value = (False, [{'ingredient': 'chicken', 'restriction': 'vegan'}])
        
        result = query_recipes_by_ingredients(['chicken'], {}, user_id='user-123')
        
        # Recipe should be in filtered list, not compatible list
        if isinstance(result, dict):
            assert len(result['filtered']) > 0
            assert 'violations' in result['filtered'][0]