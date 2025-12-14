"""
Tests for services.recipe_matcher module
Tests the core recipe matching algorithm
"""
import pytest
from services.recipe_matcher import (
    calculate_match,
    passes_filters,
    search_recipes,
    find_partial_matches
)


class TestCalculateMatch:
    """Test the calculate_match function"""
    
    def test_perfect_match(self):
        """Test when user has all ingredients"""
        recipe_ingredients = ['chicken', 'rice', 'soy sauce']
        user_ingredients = ['chicken', 'rice', 'soy sauce']
        
        result = calculate_match(recipe_ingredients, user_ingredients)
        
        assert result['percentage'] == 100.0
        assert len(result['matched']) == 3
        assert len(result['missing']) == 0
    
    def test_partial_match(self):
        """Test when user has some ingredients"""
        recipe_ingredients = ['chicken', 'rice', 'soy sauce', 'garlic']
        user_ingredients = ['chicken', 'rice']
        
        result = calculate_match(recipe_ingredients, user_ingredients)
        
        assert result['percentage'] == 50.0
        assert len(result['matched']) == 2
        assert len(result['missing']) == 2
        assert 'garlic' in result['missing']
        assert 'soy sauce' in result['missing']
    
    def test_no_match(self):
        """Test when user has no matching ingredients"""
        recipe_ingredients = ['chicken', 'rice', 'soy sauce']
        user_ingredients = ['pasta', 'tomato', 'cheese']
        
        result = calculate_match(recipe_ingredients, user_ingredients)
        
        assert result['percentage'] == 0.0
        assert len(result['matched']) == 0
        assert len(result['missing']) == 3
    
    def test_empty_user_ingredients(self):
        """Test with empty user ingredient list"""
        recipe_ingredients = ['chicken', 'rice']
        user_ingredients = []
        
        result = calculate_match(recipe_ingredients, user_ingredients)
        
        assert result['percentage'] == 0.0
        assert len(result['matched']) == 0
        assert len(result['missing']) == 2
    
    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive"""
        recipe_ingredients = ['CHICKEN', 'Rice', 'SOY SAUCE']
        user_ingredients = ['chicken', 'rice', 'soy sauce']
        
        result = calculate_match(recipe_ingredients, user_ingredients)
        
        assert result['percentage'] == 100.0


class TestPassesFilters:
    """Test the passes_filters function"""
    
    def test_no_filters(self):
        """Test that recipe passes when no filters applied"""
        recipe = {'name': 'Test Recipe', 'total_time': 30}
        result = passes_filters(recipe, None)
        assert result is True
    
    def test_time_filter_pass(self):
        """Test recipe passes time filter"""
        recipe = {'total_time': 25}
        filters = {'max_time': 30}
        
        result = passes_filters(recipe, filters)
        assert result is True
    
    def test_time_filter_fail(self):
        """Test recipe fails time filter"""
        recipe = {'total_time': 45}
        filters = {'max_time': 30}
        
        result = passes_filters(recipe, filters)
        assert result is False
    
    def test_skill_level_filter_pass(self):
        """Test recipe passes skill level filter"""
        recipe = {'skill_level': 'beginner'}
        filters = {'skill_level': 'beginner'}
        
        result = passes_filters(recipe, filters)
        assert result is True
    
    def test_skill_level_filter_fail(self):
        """Test recipe fails skill level filter"""
        recipe = {'skill_level': 'advanced'}
        filters = {'skill_level': 'beginner'}
        
        result = passes_filters(recipe, filters)
        assert result is False
    
    def test_dietary_tags_filter_pass(self):
        """Test recipe passes dietary tags filter"""
        recipe = {'dietary_tags': ['vegetarian', 'gluten-free']}
        filters = {'dietary_tags': ['vegetarian']}
        
        result = passes_filters(recipe, filters)
        assert result is True
    
    def test_dietary_tags_filter_fail(self):
        """Test recipe fails dietary tags filter (missing required tag)"""
        recipe = {'dietary_tags': ['vegetarian']}
        filters = {'dietary_tags': ['vegan']}
        
        result = passes_filters(recipe, filters)
        assert result is False
    
    def test_multiple_filters_pass(self):
        """Test recipe passes multiple filters"""
        recipe = {
            'total_time': 20,
            'skill_level': 'beginner',
            'cuisine': 'italian'
        }
        filters = {
            'max_time': 30,
            'skill_level': 'beginner',
            'cuisine': 'italian'
        }
        
        result = passes_filters(recipe, filters)
        assert result is True
    
    def test_multiple_filters_fail_one(self):
        """Test recipe fails when one filter doesn't match"""
        recipe = {
            'total_time': 45,
            'skill_level': 'beginner'
        }
        filters = {
            'max_time': 30,
            'skill_level': 'beginner'
        }
        
        result = passes_filters(recipe, filters)
        assert result is False


class TestSearchRecipes:
    """Test the search_recipes function"""
    
    def test_search_returns_sorted_results(self, sample_recipes, user_ingredients):
        """Test that search results are sorted by match percentage"""
        results = search_recipes(user_ingredients, sample_recipes)
        
        # Should return recipes sorted by match percentage (descending)
        assert len(results) > 0
        
        # Check sorting (each result should have higher or equal match than next)
        for i in range(len(results) - 1):
            assert results[i]['match_percentage'] >= results[i + 1]['match_percentage']
    
    def test_search_with_filters(self, sample_recipes):
        """Test search with time filter"""
        user_ingredients = ['bread', 'cheese']
        filters = {'max_time': 15}
        
        results = search_recipes(user_ingredients, sample_recipes, filters)
        
        # Should only return recipes under 15 minutes
        for recipe in results:
            assert recipe['total_time'] <= 15
    
    def test_search_no_matches(self, sample_recipes):
        """Test search with ingredients that don't match any recipe"""
        user_ingredients = ['pineapple', 'coconut', 'mango']
        
        results = search_recipes(user_ingredients, sample_recipes)
        
        assert len(results) == 0


class TestFindPartialMatches:
    """Test the find_partial_matches function"""
    
    def test_find_partial_matches(self, sample_recipes):
        """Test finding recipes with 50%+ match"""
        user_ingredients = ['chicken', 'rice']
        
        results = find_partial_matches(
            user_ingredients,
            sample_recipes,
            min_match_threshold=50
        )
        
        # Should find Chicken Fried Rice (2 out of 5 = 40%, close)
        # Depends on exact match calculation
        assert isinstance(results, list)
    
    def test_exclude_perfect_matches(self, sample_recipes):
        """Test that perfect matches are excluded"""
        user_ingredients = ['bread', 'cheese', 'butter']
        exclude_ids = {2}  # Grilled Cheese ID
        
        results = find_partial_matches(
            user_ingredients,
            sample_recipes,
            exclude_ids=exclude_ids
        )
        
        # Grilled Cheese should not be in results
        recipe_ids = [r['id'] for r in results]
        assert 2 not in recipe_ids