"""Tests for Doughnut criteria factory."""

from models.frameworks.doughnut import build_doughnut_criteria


def test_doughnut_factory_shape_and_split():
    criteria = build_doughnut_criteria()
    assert len(criteria) == 21

    social = [c for c in criteria if c.meta.get("boundary_group") == "social"]
    ecological = [c for c in criteria if c.meta.get("boundary_group") == "ecological"]
    assert len(social) == 12
    assert len(ecological) == 9

    assert all(c.meta.get("polarity") == "shortfall" for c in social)
    assert all(c.meta.get("polarity") == "overshoot" for c in ecological)



def test_doughnut_factory_idempotent_and_unique_names():
    first = build_doughnut_criteria()
    second = build_doughnut_criteria()

    assert [c.id for c in first] == [c.id for c in second]
    names = [c.meta.get("boundary_name") for c in first]
    assert len(names) == len(set(names))
