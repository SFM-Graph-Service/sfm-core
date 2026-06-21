"""
Unit tests for Doughnut Economics criteria factory.

Validates that build_doughnut_criteria() correctly implements Kate Raworth's
Doughnut Economics framework as SFM criterion nodes.
"""

from models.frameworks.doughnut import build_doughnut_criteria
from models.matrix_components import SFMCriteria
from models.enums import CriteriaType, CriteriaPriority, MeasurementApproach


def test_doughnut_criteria_count():
    """Test that factory creates exactly 21 criteria."""
    criteria = build_doughnut_criteria()
    assert len(criteria) == 21, f"Expected 21 criteria, got {len(criteria)}"


def test_doughnut_criteria_split():
    """Test correct 12 social foundation + 9 ecological ceiling split."""
    criteria = build_doughnut_criteria()

    social_foundation = [c for c in criteria if c.meta.get("polarity") == "shortfall"]
    ecological_ceiling = [c for c in criteria if c.meta.get("polarity") == "overshoot"]

    assert len(social_foundation) == 12, \
        f"Expected 12 social foundation criteria, got {len(social_foundation)}"
    assert len(ecological_ceiling) == 9, \
        f"Expected 9 ecological ceiling criteria, got {len(ecological_ceiling)}"


def test_doughnut_all_are_sfm_criteria():
    """Test that all returned nodes are SFMCriteria instances."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        assert isinstance(criterion, SFMCriteria), \
            f"Criterion '{criterion.label}' is not an SFMCriteria instance"


def test_doughnut_valid_types():
    """Test that each criterion has valid criteria_type."""
    criteria = build_doughnut_criteria()

    valid_types = {
        CriteriaType.SOCIAL,
        CriteriaType.ENVIRONMENTAL,
        CriteriaType.ECONOMIC,
        CriteriaType.POLITICAL,
    }

    for criterion in criteria:
        assert criterion.criteria_type in valid_types, \
            f"Criterion '{criterion.label}' has invalid type: {criterion.criteria_type}"


def test_doughnut_valid_polarity():
    """Test that each criterion has valid polarity tag (shortfall or overshoot)."""
    criteria = build_doughnut_criteria()

    valid_polarities = {"shortfall", "overshoot"}

    for criterion in criteria:
        polarity = criterion.meta.get("polarity")
        assert polarity in valid_polarities, \
            f"Criterion '{criterion.label}' has invalid polarity: {polarity}"


def test_doughnut_unique_names():
    """Test that all criterion labels are unique."""
    criteria = build_doughnut_criteria()

    labels = [c.label for c in criteria]
    assert len(labels) == len(set(labels)), \
        f"Duplicate labels found: {[l for l in labels if labels.count(l) > 1]}"


def test_doughnut_expected_social_foundation():
    """Test that all 12 expected social foundation criteria are present."""
    criteria = build_doughnut_criteria()

    social_labels = {
        c.label for c in criteria
        if c.meta.get("polarity") == "shortfall"
    }

    expected_social = {
        "Food",
        "Health",
        "Education",
        "Income & Work",
        "Peace & Justice",
        "Political Voice",
        "Social Equity",
        "Gender Equality",
        "Housing",
        "Networks",
        "Energy",
        "Water",
    }

    assert social_labels == expected_social, \
        f"Missing: {expected_social - social_labels}, Extra: {social_labels - expected_social}"


def test_doughnut_expected_ecological_ceiling():
    """Test that all 9 expected planetary boundaries are present."""
    criteria = build_doughnut_criteria()

    ecological_labels = {
        c.label for c in criteria
        if c.meta.get("polarity") == "overshoot"
    }

    expected_ecological = {
        "Climate Change",
        "Ocean Acidification",
        "Chemical Pollution",
        "Nitrogen & Phosphorus Loading",
        "Freshwater Withdrawals",
        "Land-System Change",
        "Biodiversity Loss",
        "Air Pollution",
        "Ozone Depletion",
    }

    assert ecological_labels == expected_ecological, \
        f"Missing: {expected_ecological - ecological_labels}, Extra: {ecological_labels - expected_ecological}"


def test_doughnut_factory_idempotent():
    """Test that factory creates distinct instances but with identical configurations."""
    criteria1 = build_doughnut_criteria()
    criteria2 = build_doughnut_criteria()

    # Should have same count and labels
    assert len(criteria1) == len(criteria2)

    labels1 = sorted([c.label for c in criteria1])
    labels2 = sorted([c.label for c in criteria2])
    assert labels1 == labels2

    # But should be distinct object instances
    for c1, c2 in zip(criteria1, criteria2):
        if c1.label == c2.label:
            assert c1.id != c2.id, \
                f"Criteria with label '{c1.label}' have same ID - not distinct instances"


def test_doughnut_all_have_descriptions():
    """Test that all criteria have non-empty descriptions."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        assert criterion.description, \
            f"Criterion '{criterion.label}' has empty description"
        assert len(criterion.description) > 20, \
            f"Criterion '{criterion.label}' has suspiciously short description"


def test_doughnut_all_have_metadata():
    """Test that all criteria have required metadata fields."""
    criteria = build_doughnut_criteria()

    required_meta_fields = {"polarity", "doughnut_dimension", "source"}

    for criterion in criteria:
        assert criterion.meta, \
            f"Criterion '{criterion.label}' has no meta"

        for field in required_meta_fields:
            assert field in criterion.meta, \
                f"Criterion '{criterion.label}' missing meta field: {field}"


def test_doughnut_dimension_tags():
    """Test that doughnut_dimension metadata correctly separates social/ecological."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        dimension = criterion.meta.get("doughnut_dimension")
        polarity = criterion.meta.get("polarity")

        if polarity == "shortfall":
            assert dimension == "social_foundation", \
                f"Social criterion '{criterion.label}' has wrong dimension tag: {dimension}"
        elif polarity == "overshoot":
            assert dimension == "ecological_ceiling", \
                f"Ecological criterion '{criterion.label}' has wrong dimension tag: {dimension}"


def test_doughnut_primary_criteria_have_high_relevance():
    """Test that PRIMARY criteria have high life_process_relevance."""
    criteria = build_doughnut_criteria()

    primary_criteria = [c for c in criteria if c.priority == CriteriaPriority.PRIMARY]

    # Most Doughnut criteria should be PRIMARY (core human needs and planetary boundaries)
    assert len(primary_criteria) >= 18, \
        f"Expected at least 18 PRIMARY criteria, got {len(primary_criteria)}"

    for criterion in primary_criteria:
        if criterion.life_process_relevance is not None:
            assert criterion.life_process_relevance >= 0.80, \
                f"PRIMARY criterion '{criterion.label}' has low life_process_relevance: {criterion.life_process_relevance}"


def test_doughnut_all_have_evaluation_method():
    """Test that all criteria specify evaluation_method."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        assert criterion.evaluation_method, \
            f"Criterion '{criterion.label}' has no evaluation_method specified"


def test_doughnut_all_have_data_requirements():
    """Test that all criteria specify data_requirements."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        assert criterion.data_requirements, \
            f"Criterion '{criterion.label}' has no data_requirements specified"
        assert len(criterion.data_requirements) > 0, \
            f"Criterion '{criterion.label}' has empty data_requirements list"


def test_doughnut_all_have_measurement_frequency():
    """Test that all criteria specify measurement_frequency."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        assert criterion.measurement_frequency, \
            f"Criterion '{criterion.label}' has no measurement_frequency specified"


def test_doughnut_all_have_normative_justification():
    """Test that all criteria have normative_justification per Hayden framework."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        assert criterion.normative_justification, \
            f"Criterion '{criterion.label}' has no normative_justification"
        # Should reference Hayden framework concepts (life process, community, instrumental, etc.)
        framework_keywords = ["hayden", "life process", "community", "instrumental", "ceremonial"]
        has_framework_reference = any(
            keyword in criterion.normative_justification.lower()
            for keyword in framework_keywords
        )
        assert has_framework_reference, \
            f"Criterion '{criterion.label}' normative_justification doesn't reference Hayden framework concepts"


def test_doughnut_source_attribution():
    """Test that all criteria properly attribute sources."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        source = criterion.meta.get("source")
        assert source, f"Criterion '{criterion.label}' has no source attribution"

        # Social foundation should reference Raworth 2017
        if criterion.meta.get("polarity") == "shortfall":
            assert "Raworth 2017" in source, \
                f"Social criterion '{criterion.label}' should cite Raworth 2017"

        # Ecological ceiling should reference planetary boundaries research
        if criterion.meta.get("polarity") == "overshoot":
            assert "Rockström" in source or "Steffen" in source, \
                f"Ecological criterion '{criterion.label}' should cite planetary boundaries research"


def test_doughnut_climate_change_specifics():
    """Test Climate Change criterion has correct configuration."""
    criteria = build_doughnut_criteria()

    climate = next((c for c in criteria if c.label == "Climate Change"), None)
    assert climate is not None, "Climate Change criterion not found"

    assert climate.meta.get("polarity") == "overshoot"
    assert climate.meta.get("doughnut_dimension") == "ecological_ceiling"
    assert climate.criteria_type == CriteriaType.ENVIRONMENTAL
    assert climate.priority == CriteriaPriority.PRIMARY
    assert climate.life_process_relevance == 1.0
    assert "350 ppm" in climate.evaluation_method or "CO2" in climate.evaluation_method


def test_doughnut_food_security_specifics():
    """Test Food criterion has correct configuration."""
    criteria = build_doughnut_criteria()

    food = next((c for c in criteria if c.label == "Food"), None)
    assert food is not None, "Food criterion not found"

    assert food.meta.get("polarity") == "shortfall"
    assert food.meta.get("doughnut_dimension") == "social_foundation"
    assert food.criteria_type == CriteriaType.SOCIAL
    assert food.priority == CriteriaPriority.PRIMARY
    assert food.life_process_relevance == 1.0


def test_doughnut_measurement_approaches_appropriate():
    """Test that criteria have appropriate measurement approaches."""
    criteria = build_doughnut_criteria()

    for criterion in criteria:
        assert criterion.measurement_approach in {
            MeasurementApproach.QUANTITATIVE,
            MeasurementApproach.QUALITATIVE,
        }, f"Criterion '{criterion.label}' has invalid measurement approach"

        # Most Doughnut criteria should be quantifiable
        if criterion.label not in {"Political Voice", "Chemical Pollution"}:
            assert criterion.measurement_approach == MeasurementApproach.QUANTITATIVE, \
                f"Expected '{criterion.label}' to be QUANTITATIVE"
