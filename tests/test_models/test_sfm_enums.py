"""
Unit tests for sfm_enums module.
"""

import pytest
from models.sfm_enums import (
    ValueCategory,
    InstitutionLayer,
    ResourceType,
    FlowNature,
    FlowType,
    PolicyInstrumentType,
    ChangeType,
    BehaviorPatternType,
    FeedbackPolarity,
    FeedbackType,
    TemporalFunctionType,
    ValidationRuleType,
    SystemPropertyType,
    RelationshipKind,
    PowerResourceType,
    ToolSkillTechnologyType,
    validate_enum_operation,
)


class TestEnumExistence:
    """Test that all major enums exist."""

    def test_value_category_enum(self):
        assert hasattr(ValueCategory, "ECONOMIC")
        assert hasattr(ValueCategory, "SOCIAL")
        assert hasattr(ValueCategory, "ENVIRONMENTAL")

    def test_institution_layer_enum(self):
        assert hasattr(InstitutionLayer, "FORMAL_RULE")
        assert hasattr(InstitutionLayer, "INFORMAL_NORM")

    def test_resource_type_enum(self):
        assert hasattr(ResourceType, "NATURAL")
        assert hasattr(ResourceType, "PRODUCED")
        assert hasattr(ResourceType, "HUMAN")

    def test_flow_nature_enum(self):
        assert hasattr(FlowNature, "INPUT")
        assert hasattr(FlowNature, "OUTPUT")

    def test_flow_type_enum(self):
        assert hasattr(FlowType, "MATERIAL")
        assert hasattr(FlowType, "ENERGY")

    def test_policy_instrument_type_enum(self):
        assert hasattr(PolicyInstrumentType, "REGULATORY")
        assert hasattr(PolicyInstrumentType, "ECONOMIC")

    def test_relationship_kind_enum(self):
        assert hasattr(RelationshipKind, "GOVERNS")
        assert hasattr(RelationshipKind, "USES")


class TestEnumUtilityFunctions:
    """Test utility functions for enums."""

    def test_validate_enum_operation(self):
        # validate_enum_operation is a decorator
        result = validate_enum_operation("test_operation")
        assert callable(result)


class TestEnumValues:
    """Test specific enum values."""

    def test_value_category_values(self):
        assert ValueCategory.ECONOMIC.name == "ECONOMIC"
        assert ValueCategory.SOCIAL.name == "SOCIAL"

    def test_feedback_polarity(self):
        assert hasattr(FeedbackPolarity, "REINFORCING")
        assert hasattr(FeedbackPolarity, "BALANCING")

    def test_system_property_type(self):
        assert hasattr(SystemPropertyType, "DYNAMIC")
        assert hasattr(SystemPropertyType, "STRUCTURAL")


class TestEnumIntegration:
    """Integration tests for enum usage."""

    def test_enum_in_comparisons(self):
        """Test enum equality comparisons."""
        assert ValueCategory.ECONOMIC == ValueCategory.ECONOMIC
        assert ValueCategory.ECONOMIC != ValueCategory.SOCIAL

    def test_enum_name_access(self):
        """Test accessing enum member names."""
        assert ValueCategory.ECONOMIC.name == "ECONOMIC"
        assert FlowNature.INPUT.name == "INPUT"

    def test_enum_iteration(self):
        """Test iterating over enum members."""
        categories = list(ValueCategory)
        assert len(categories) > 0
        assert ValueCategory.ECONOMIC in categories

    def test_multiple_enum_types(self):
        """Test multiple enum types are distinct."""
        assert type(ValueCategory.ECONOMIC) != type(FlowNature.INPUT)

    def test_enum_membership(self):
        """Test enum membership checking."""
        assert ValueCategory.ECONOMIC in ValueCategory
        assert FlowNature.INPUT in FlowNature

    def test_relationship_kind_variety(self):
        """Test variety of relationship kinds."""
        assert hasattr(RelationshipKind, "ENABLES")
        assert hasattr(RelationshipKind, "INHIBITS")
        assert hasattr(RelationshipKind, "REINFORCES")

    def test_policy_instrument_types(self):
        """Test policy instrument type variety."""
        assert hasattr(PolicyInstrumentType, "REGULATORY")
        assert hasattr(PolicyInstrumentType, "ECONOMIC")
        assert hasattr(PolicyInstrumentType, "INFORMATION")

    def test_change_type_enum(self):
        """Test change type enum."""
        assert hasattr(ChangeType, "INCREMENTAL")
        assert hasattr(ChangeType, "REVOLUTIONARY")

    def test_behavior_pattern_enum(self):
        """Test behavior pattern enum."""
        assert hasattr(BehaviorPatternType, "HABITUAL")
        assert hasattr(BehaviorPatternType, "STRATEGIC")

    def test_feedback_types(self):
        """Test feedback-related enums."""
        assert hasattr(FeedbackPolarity, "REINFORCING")
        assert hasattr(FeedbackPolarity, "BALANCING")
        assert hasattr(FeedbackType, "POSITIVE")
        assert hasattr(FeedbackType, "NEGATIVE")

    def test_temporal_function_type(self):
        """Test temporal function type enum."""
        assert hasattr(TemporalFunctionType, "LINEAR")
        assert hasattr(TemporalFunctionType, "EXPONENTIAL")

    def test_validation_rule_type(self):
        """Test validation rule type enum."""
        assert hasattr(ValidationRuleType, "REQUIRED")
        assert hasattr(ValidationRuleType, "RANGE")

    def test_system_property_types(self):
        """Test system property type variety."""
        assert hasattr(SystemPropertyType, "DYNAMIC")
        assert hasattr(SystemPropertyType, "STRUCTURAL")
        assert hasattr(SystemPropertyType, "PERFORMANCE")

    def test_power_resource_type(self):
        """Test power resource type enum."""
        assert hasattr(PowerResourceType, "INSTITUTIONAL_AUTHORITY")
        assert hasattr(PowerResourceType, "ECONOMIC_CONTROL")

    def test_tool_skill_technology_type(self):
        """Test tool/skill/technology type enum."""
        assert hasattr(ToolSkillTechnologyType, "PHYSICAL_TOOL")
        assert hasattr(ToolSkillTechnologyType, "DIGITAL_CAPABILITY")
