"""
Unit Tests for Shopping Suggestion Engine
Tests the smart shopping suggestion algorithm
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.suggestion_engine import generate_shopping_suggestions, display_suggestions
    from services.recipe_matcher import calculate_match
    SUGGESTION_ENGINE_AVAILABLE = True
except ImportError:
    SUGGESTION_ENGINE_AVAILABLE = False
    pytest.skip("Suggestion engine not available", allow_module_level=True)


class TestGenerateShoppingSuggestions:
    """Test shopping suggestion generation"""
    
    def test_suggest_for_partial_matches(self):
        """Test suggestions when user has some ingredients"""
        user_ingredients = ['chicken', 'rice']
        recipes = [
            {
                'id': 1,
                'name': 'Chicken Stir Fry',
                'ingredients': ['chicken', 'rice', 'soy sauce', 'ginger'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'Asian'
            },
            {
                'id': 2,
                'name': 'Fried Rice',
                'ingredients': ['rice', 'soy sauce', 'eggs', 'vegetables'],
                'total_time': 20,
                'skill_level': 'beginner',
                'cuisine': 'Asian'
            }
        ]
        
        suggestions = generate_shopping_suggestions(user_ingredients, recipes, top_n=5)
        
        assert len(suggestions) > 0
        # soy sauce appears in both recipes, should be top suggestion
        soy_sauce_found = any(s['name'] == 'soy sauce' for s in suggestions)
        assert soy_sauce_found
        
        # Find soy sauce and check its count
        soy_sauce = next((s for s in suggestions if s['name'] == 'soy sauce'), None)
        if soy_sauce:
            assert soy_sauce['unlock_count'] >= 1  # At least 1 recipe
    
    def test_suggest_for_no_matches(self):
        """Test suggestions when user has zero matches"""
        user_ingredients = []
        recipes = [
            {
                'id': 1,
                'name': 'Simple Recipe',
                'ingredients': ['chicken', 'salt'],
                'total_time': 15,
                'skill_level': 'beginner',
                'cuisine': 'American'
            }
        ]
        
        suggestions = generate_shopping_suggestions(
            user_ingredients, 
            recipes, 
            top_n=5, 
            has_matches=False
        )
        
        assert len(suggestions) > 0
    
    def test_top_n_limit(self):
        """Test that suggestions are limited to top_n"""
        user_ingredients = ['chicken']
        recipes = [
            {
                'id': i,
                'name': f'Recipe {i}',
                'ingredients': ['chicken', f'ingredient_{i}'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'test'
            }
            for i in range(20)
        ]
        
        suggestions = generate_shopping_suggestions(user_ingredients, recipes, top_n=3)
        
        assert len(suggestions) <= 3
    
    def test_suggestions_with_filters(self):
        """Test suggestions respect recipe filters"""
        user_ingredients = ['chicken']
        recipes = [
            {
                'id': 1,
                'name': 'Quick Recipe',
                'ingredients': ['chicken', 'rice'],
                'total_time': 15,
                'skill_level': 'beginner',
                'cuisine': 'Asian',
                'dietary_tags': []
            },
            {
                'id': 2,
                'name': 'Slow Recipe',
                'ingredients': ['chicken', 'pasta'],
                'total_time': 60,
                'skill_level': 'advanced',
                'cuisine': 'Italian',
                'dietary_tags': []
            }
        ]
        
        filters = {'max_time': 30}
        suggestions = generate_shopping_suggestions(user_ingredients, recipes, filters=filters, top_n=5)
        
        # Should only suggest from recipes that pass filter
        # pasta should NOT appear (from 60-min recipe)
        suggestion_names = [s['name'] for s in suggestions]
        assert 'pasta' not in suggestion_names
    
    def test_exclude_already_shown_recipes(self):
        """Test that excluded recipe IDs are not considered"""
        user_ingredients = ['chicken']
        recipes = [
            {
                'id': 1,
                'name': 'Recipe 1',
                'ingredients': ['chicken', 'rice'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'Asian'
            },
            {
                'id': 2,
                'name': 'Recipe 2',
                'ingredients': ['chicken', 'pasta'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'Italian'
            }
        ]
        
        # Exclude recipe 1
        suggestions = generate_shopping_suggestions(
            user_ingredients, 
            recipes, 
            exclude_ids={1},
            top_n=5
        )
        
        # Should only suggest pasta (from recipe 2)
        assert len(suggestions) == 1
        assert suggestions[0]['name'] == 'pasta'
    
    def test_ranking_by_unlock_count(self):
        """Test that suggestions are ranked by how many recipes they unlock"""
        user_ingredients = ['chicken']
        recipes = [
            {
                'id': 1,
                'name': 'Recipe 1',
                'ingredients': ['chicken', 'rice', 'soy sauce'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'Asian'
            },
            {
                'id': 2,
                'name': 'Recipe 2',
                'ingredients': ['chicken', 'rice'],
                'total_time': 20,
                'skill_level': 'beginner',
                'cuisine': 'Asian'
            },
            {
                'id': 3,
                'name': 'Recipe 3',
                'ingredients': ['chicken', 'pasta'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'Italian'
            }
        ]
        
        suggestions = generate_shopping_suggestions(user_ingredients, recipes, top_n=5)
        
        # rice appears in 2 recipes, should be ranked higher than soy sauce (1) and pasta (1)
        assert suggestions[0]['name'] == 'rice'
        assert suggestions[0]['unlock_count'] == 2
    
    def test_suggestion_includes_recipe_names(self):
        """Test that suggestions include which recipes they unlock"""
        user_ingredients = ['chicken']
        recipes = [
            {
                'id': 1,
                'name': 'Chicken Rice',
                'ingredients': ['chicken', 'rice'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'Asian'
            }
        ]
        
        suggestions = generate_shopping_suggestions(user_ingredients, recipes, top_n=5)
        
        assert 'recipe_names' in suggestions[0]
        assert 'Chicken Rice' in suggestions[0]['recipe_names']


class TestDisplaySuggestions:
    """Test suggestion display formatting (output formatting test)"""
    
    def test_display_with_suggestions(self, capsys):
        """Test displaying suggestions to console"""
        suggestions = [
            {
                'name': 'soy sauce',
                'unlock_count': 2,
                'recipe_names': ['Fried Rice', 'Stir Fry']
            }
        ]
        
        display_suggestions(suggestions)
        
        captured = capsys.readouterr()
        assert 'soy sauce' in captured.out.lower()
        assert '2' in captured.out
    
    def test_display_no_suggestions(self, capsys):
        """Test displaying when no suggestions available"""
        suggestions = []
        
        display_suggestions(suggestions)
        
        captured = capsys.readouterr()
        assert 'no suggestions' in captured.out.lower()
    
    def test_display_with_partial_matches(self, capsys):
        """Test displaying partial matches"""
        suggestions = [{'name': 'rice', 'unlock_count': 1, 'recipe_names': ['Test']}]
        partial_matches = [
            {
                'name': 'Test Recipe',
                'match_percentage': 75.0,
                'matched_ingredients': ['chicken'],
                'missing_ingredients': ['rice']
            }
        ]
        
        display_suggestions(suggestions, partial_matches)
        
        captured = capsys.readouterr()
        assert 'recipes you\'re close to' in captured.out.lower()


class TestSuggestionEdgeCases:
    """Test edge cases in suggestion generation"""
    
    def test_empty_recipe_list(self):
        """Test with no recipes"""
        suggestions = generate_shopping_suggestions(['chicken'], [], top_n=5)
        assert len(suggestions) == 0
    
    def test_empty_user_ingredients(self):
        """Test with no user ingredients"""
        recipes = [
            {
                'id': 1,
                'name': 'Test',
                'ingredients': ['chicken'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'test'
            }
        ]
        suggestions = generate_shopping_suggestions([], recipes, top_n=5, has_matches=False)
        assert len(suggestions) > 0
    
    def test_all_recipes_100_percent_match(self):
        """Test when user has all ingredients for all recipes"""
        user_ingredients = ['chicken', 'rice', 'soy sauce']
        recipes = [
            {
                'id': 1,
                'name': 'Perfect Match',
                'ingredients': ['chicken', 'rice'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'test'
            }
        ]
        
        suggestions = generate_shopping_suggestions(user_ingredients, recipes, top_n=5)
        
        # Should return no suggestions (user can make everything)
        assert len(suggestions) == 0
    
    def test_recipes_with_overlapping_missing_ingredients(self):
        """Test when multiple recipes share missing ingredients"""
        user_ingredients = ['chicken']
        recipes = [
            {
                'id': 1,
                'name': 'Recipe 1',
                'ingredients': ['chicken', 'soy sauce', 'ginger'],
                'total_time': 30,
                'skill_level': 'beginner',
                'cuisine': 'Asian'
            },
            {
                'id': 2,
                'name': 'Recipe 2',
                'ingredients': ['chicken', 'soy sauce', 'garlic'],
                'total_time': 25,
                'skill_level': 'beginner',
                'cuisine': 'Asian'
            }
        ]
        
        suggestions = generate_shopping_suggestions(user_ingredients, recipes, top_n=5)
        
        # soy sauce appears in both, should be top suggestion
        assert suggestions[0]['name'] == 'soy sauce'
        assert suggestions[0]['unlock_count'] == 2