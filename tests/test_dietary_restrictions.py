"""
Tests for queries.dietary_restrictions module
Tests recipe filtering based on dietary restrictions
"""
import pytest
from queries.dietary_restrictions import (
    check_recipe_compatibility,
    get_restriction_info,
    get_all_restrictions,
    DIETARY_RESTRICTIONS
)


class TestCheckRecipeCompatibility:
    """Test recipe compatibility checking"""
    
    def test_vegetarian_blocks_meat(self):
        """Test that vegetarian filter blocks meat"""
        recipe_ingredients = ['chicken', 'rice', 'soy sauce']
        restrictions = ['vegetarian']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is False
        assert len(violations) > 0
        assert any(v['ingredient'] == 'chicken' for v in violations)
    
    def test_vegan_blocks_dairy_and_eggs(self):
        """Test that vegan filter blocks dairy and eggs"""
        recipe_ingredients = ['pasta', 'cheese', 'eggs', 'butter']
        restrictions = ['vegan']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is False
        # Should catch cheese, eggs, AND butter
        assert len(violations) >= 3
    
    def test_gluten_free_blocks_wheat(self):
        """Test that gluten-free filter blocks wheat products"""
        recipe_ingredients = ['chicken', 'pasta', 'tomato']
        restrictions = ['gluten-free']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is False
        assert any(v['ingredient'] == 'pasta' for v in violations)
    
    def test_dairy_free_blocks_milk_products(self):
        """Test that dairy-free filter blocks all dairy"""
        recipe_ingredients = ['oats', 'milk', 'banana']
        restrictions = ['dairy-free']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is False
        assert any(v['ingredient'] == 'milk' for v in violations)
    
    def test_nut_free_blocks_nuts(self):
        """Test that nut-free filter blocks nuts"""
        recipe_ingredients = ['oats', 'peanut butter', 'banana']
        restrictions = ['nut-free']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is False
        assert any('peanut' in v['ingredient'] for v in violations)
    
    def test_multiple_restrictions(self):
        """Test checking multiple restrictions at once"""
        recipe_ingredients = ['chicken', 'bread', 'cheese']
        restrictions = ['vegetarian', 'gluten-free']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is False
        # Should violate both vegetarian (chicken) and gluten-free (bread)
        assert len(violations) >= 2
    
    def test_compatible_recipe_vegetarian(self):
        """Test that vegetarian-friendly recipe passes"""
        recipe_ingredients = ['tofu', 'rice', 'broccoli', 'soy sauce']
        restrictions = ['vegetarian']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is True
        assert len(violations) == 0
    
    def test_compatible_recipe_vegan(self):
        """Test that vegan-friendly recipe passes"""
        recipe_ingredients = ['chickpeas', 'rice', 'tomato', 'onion']
        restrictions = ['vegan']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is True
        assert len(violations) == 0
    
    def test_no_restrictions(self):
        """Test with no dietary restrictions"""
        recipe_ingredients = ['chicken', 'bread', 'cheese', 'eggs']
        restrictions = []
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is True
        assert len(violations) == 0
    
    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive"""
        recipe_ingredients = ['CHICKEN', 'Rice']
        restrictions = ['vegetarian']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is False
    
    def test_partial_ingredient_matching(self):
        """Test that partial matches are caught (e.g., 'cheddar cheese')"""
        recipe_ingredients = ['pasta', 'cheddar cheese', 'tomato']
        restrictions = ['vegan']
        
        is_compatible, violations = check_recipe_compatibility(
            recipe_ingredients, restrictions
        )
        
        assert is_compatible is False
        # Should catch that 'cheddar cheese' contains 'cheese'
        assert any('cheese' in v['ingredient'] for v in violations)


class TestGetRestrictionInfo:
    """Test getting restriction information"""
    
    def test_get_vegetarian_info(self):
        """Test getting vegetarian restriction info"""
        info = get_restriction_info('vegetarian')
        
        assert info is not None
        assert 'forbidden_ingredients' in info
        assert 'description' in info
        assert 'chicken' in info['forbidden_ingredients']
    
    def test_get_vegan_info(self):
        """Test getting vegan restriction info"""
        info = get_restriction_info('vegan')
        
        assert info is not None
        assert 'eggs' in info['forbidden_ingredients']
        assert 'milk' in info['forbidden_ingredients']
    
    def test_get_invalid_restriction(self):
        """Test getting info for non-existent restriction"""
        info = get_restriction_info('invalid_restriction')
        
        assert info is None
    
    def test_case_insensitive(self):
        """Test that restriction lookup is case-insensitive"""
        info_lower = get_restriction_info('vegetarian')
        info_upper = get_restriction_info('VEGETARIAN')
        
        assert info_lower is not None
        assert info_upper is not None


class TestGetAllRestrictions:
    """Test getting list of all restrictions"""
    
    def test_returns_all_restrictions(self):
        """Test that all restrictions are returned"""
        restrictions = get_all_restrictions()
        
        assert 'vegetarian' in restrictions
        assert 'vegan' in restrictions
        assert 'gluten-free' in restrictions
        assert 'dairy-free' in restrictions
        assert 'nut-free' in restrictions
    
    def test_returns_list(self):
        """Test that result is a list"""
        restrictions = get_all_restrictions()
        
        assert isinstance(restrictions, list)
        assert len(restrictions) > 0


class TestDietaryRestrictionsDataStructure:
    """Test dietary restrictions data structure"""
    
    def test_all_restrictions_have_required_fields(self):
        """Test that all restrictions have required fields"""
        for restriction, data in DIETARY_RESTRICTIONS.items():
            assert 'forbidden_ingredients' in data
            assert 'description' in data
            assert isinstance(data['forbidden_ingredients'], list)
            assert isinstance(data['description'], str)
    
    def test_forbidden_ingredients_are_lowercase(self):
        """Test that all forbidden ingredients are lowercase"""
        for restriction, data in DIETARY_RESTRICTIONS.items():
            for ingredient in data['forbidden_ingredients']:
                assert ingredient == ingredient.lower(), \
                    f"Ingredient '{ingredient}' in {restriction} is not lowercase"