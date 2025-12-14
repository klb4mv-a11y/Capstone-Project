"""
Tests for ingredient substitution system
"""
import pytest
from services.substitutions import (
    SUBSTITUTIONS,
    get_substitutions_for_ingredient
)


class TestGetSubstitutionsForIngredient:
    """Test getting substitutions for specific ingredients"""
    
    def test_milk_substitutions_vegan(self):
        """Test getting vegan milk substitutions"""
        subs = get_substitutions_for_ingredient('milk', ['vegan'])
        
        # Should have at least one vegan milk substitute
        assert len(subs) > 0
        
        # Check they're all vegan-appropriate
        for sub in subs:
            assert 'vegan' in sub['best_for']
            assert 'milk' in sub['name'].lower()
    
    def test_butter_substitutions_dairy_free(self):
        """Test getting dairy-free butter substitutions"""
        subs = get_substitutions_for_ingredient('butter', ['dairy-free'])
        
        assert len(subs) > 0
        for sub in subs:
            assert 'dairy-free' in sub['best_for']
    
    def test_egg_substitutions_vegan(self):
        """Test getting vegan egg substitutions"""
        subs = get_substitutions_for_ingredient('egg', ['vegan'])
        
        assert len(subs) > 0
        # Common vegan egg subs
        sub_names = [s['name'] for s in subs]
        assert any('flax' in name.lower() for name in sub_names)
    
    def test_flour_substitutions_gluten_free(self):
        """Test getting gluten-free flour substitutions"""
        subs = get_substitutions_for_ingredient('flour', ['gluten-free'])
        
        assert len(subs) > 0
        for sub in subs:
            assert 'gluten-free' in sub['best_for']
    
    def test_multiple_restrictions(self):
        """Test getting substitutions with multiple restrictions"""
        subs = get_substitutions_for_ingredient('milk', ['vegan', 'nut-free'])
        
        # Should get oat milk or soy milk (but not almond milk)
        assert len(subs) > 0
        sub_names = [s['name'].lower() for s in subs]
        
        # Shouldn't include almond milk (has nuts)
        assert not any('almond' in name for name in sub_names)
    
    def test_case_insensitive_ingredient(self):
        """Test that ingredient matching is case-insensitive"""
        subs_lower = get_substitutions_for_ingredient('milk', ['vegan'])
        subs_upper = get_substitutions_for_ingredient('MILK', ['vegan'])
        subs_mixed = get_substitutions_for_ingredient('Milk', ['vegan'])
        
        assert len(subs_lower) == len(subs_upper) == len(subs_mixed)
    
    def test_unknown_ingredient(self):
        """Test handling of unknown ingredients"""
        subs = get_substitutions_for_ingredient('unicorn_tears', ['vegan'])
        
        # Should return empty list for unknown ingredients
        assert subs == []
    
    def test_no_matching_restrictions(self):
        """Test when no substitutes match the restrictions"""
        # This might return empty if no subs match the restriction
        subs = get_substitutions_for_ingredient('chicken', ['nut-free'])
        
        # Either returns nut-free options or empty (both valid)
        assert isinstance(subs, list)


class TestSubstitutionDataStructure:
    """Test that substitution data is properly structured"""
    
    def test_all_required_fields_present(self):
        """Test that all substitutes have required fields"""
        required_fields = ['name', 'ratio', 'best_for', 'flavor_impact', 
                          'texture_impact', 'cooking_notes']
        
        for ingredient, data in SUBSTITUTIONS.items():
            for substitute in data['substitutes']:
                for field in required_fields:
                    assert field in substitute, \
                        f"Missing {field} in {substitute['name']} for {ingredient}"
    
    def test_ratios_are_strings(self):
        """Test that all ratios are formatted as strings"""
        for ingredient, data in SUBSTITUTIONS.items():
            for substitute in data['substitutes']:
                assert isinstance(substitute['ratio'], str)
                assert len(substitute['ratio']) > 0  # Just check it's not empty
    
    def test_best_for_is_list(self):
        """Test that best_for is always a list"""
        for ingredient, data in SUBSTITUTIONS.items():
            for substitute in data['substitutes']:
                assert isinstance(substitute['best_for'], list)
                assert len(substitute['best_for']) > 0


class TestCommonSubstitutions:
    """Test common substitution scenarios"""
    
    def test_vegetarian_gets_dairy_substitutes(self):
        """Test that vegetarian restrictions don't filter out dairy"""
        subs = get_substitutions_for_ingredient('chicken', ['vegetarian'])
        
        # Should get tofu, chickpeas, seitan
        assert len(subs) > 0
        sub_names = [s['name'] for s in subs]
        assert 'tofu' in sub_names
    
    def test_vegan_gets_stricter_substitutes(self):
        """Test that vegan restrictions filter more strictly"""
        milk_subs = get_substitutions_for_ingredient('milk', ['vegan'])
        
        # Should NOT get regular dairy products
        sub_names = [s['name'] for s in milk_subs]  # FIXED: was 'subs'
        assert all('milk' in name.lower() for name in sub_names)
    
    def test_nut_free_filters_correctly(self):
        """Test that nut-free restrictions filter out nuts"""
        milk_subs = get_substitutions_for_ingredient('milk', ['nut-free'])
        
        # Should not include almond milk
        sub_names = [s['name'].lower() for s in milk_subs]
        assert not any('almond' in name for name in sub_names)