"""Smoke test for Nebraska SFM -> system dynamics handoff."""

import xml.etree.ElementTree as ET

from graph.exporters import export_to_xmile
from examples.hayden_case_studies.nebraska_k12_finance import build_nebraska_k12_matrix


def test_nebraska_sd_export_generates_parseable_xmile(tmp_path):
    matrix, service = build_nebraska_k12_matrix()
    out = tmp_path / "nebraska.xmile"
    export_to_xmile(matrix=matrix, filepath=out, service=service)

    assert out.exists()
    assert out.stat().st_size > 0

    tree = ET.parse(out)
    root = tree.getroot()
    assert root.tag.endswith("xmile")
    assert tree.find(".//{http://docs.oasis-open.org/xmile/ns/XMILE/v1.0}model") is not None
