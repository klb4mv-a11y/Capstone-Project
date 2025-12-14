"""
Pytest configuration and shared fixtures for SmartFridge tests
"""
import pytest
import sys
import os

# Add project root to Python path so tests can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_recipe():
    """Sample recipe for testing"""
    return {
        'id': 1,
        'name': 'Test Recipe',
        'ingredients': ['chicken', 'rice', 'soy sauce', 'garlic'],
        'prep_time': 10,
        'cook_time': 20,
        'total_time': 30,
        'servings': 4,
        'skill_level': 'beginner',
        'cuisine': 'Asian'
    }


@pytest.fixture
def sample_recipes():
    """Multiple sample recipes for testing"""
    return [
        {
            'id': 1,
            'name': 'Chicken Fried Rice',
            'ingredients': ['chicken', 'rice', 'eggs', 'soy sauce', 'oil'],
            'total_time': 25,
            'skill_level': 'beginner',
            'cuisine': 'Asian',
            'dietary_tags': []
        },
        {
            'id': 2,
            'name': 'Grilled Cheese',
            'ingredients': ['bread', 'cheese', 'butter'],
            'total_time': 10,
            'skill_level': 'beginner',
            'cuisine': 'American',
            'dietary_tags': ['vegetarian']
        },
        {
            'id': 3,
            'name': 'Veggie Stir-Fry',
            'ingredients': ['broccoli', 'carrots', 'soy sauce', 'garlic', 'oil'],
            'total_time': 20,
            'skill_level': 'beginner',
            'cuisine': 'Asian',
            'dietary_tags': ['vegetarian', 'vegan']
        }
    ]


@pytest.fixture
def user_ingredients():
    """Sample user ingredients"""
    return ['chicken', 'rice', 'soy sauce']


@pytest.fixture
def master_ingredient_list():
    """Master ingredient list for fuzzy matching tests"""
    return [
        'chicken', 'rice', 'soy sauce', 'garlic', 'eggs',
        'bread', 'cheese', 'butter', 'broccoli', 'carrots',
        'oil', 'onion', 'tomato', 'lettuce', 'pasta'
    ]