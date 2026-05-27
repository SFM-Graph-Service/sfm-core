"""
Starter Script: Clean Air Act 1972 SFM Model

This script provides a framework for building a Social Fabric Matrix model
of the 1972 Clean Air Act Amendments. Fill in the TODOs with researched data.

Prerequisites:
    - SFM Core API running: uvicorn api.rest.app:app --reload
    - pip install requests

Usage:
    python scenarios/clean_air_act_starter.py
"""

import requests
import json
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime


BASE_URL = "http://localhost:8000/api/v1"


@dataclass
class SourceReference:
    """Represents a verified source for a claim."""
    author: str
    title: str
    publisher: str
    year: int
    page_or_url: str

    def to_citation(self) -> str:
        return f"{self.author}. {self.title}. {self.publisher}, {self.year}. {self.page_or_url}"


class SFMModelBuilder:
    """Helper class for building SFM models via API."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.nodes: Dict[str, str] = {}  # name -> node_id mapping
        self.relationships: List[str] = []  # relationship_id list
        self.sources: Dict[str, List[SourceReference]] = {}  # claim -> sources

    def verify_api(self) -> bool:
        """Check if API is accessible."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def add_source(self, claim: str, source: SourceReference):
        """Document a source for a factual claim."""
        if claim not in self.sources:
            self.sources[claim] = []
        self.sources[claim].append(source)

    def create_institution(self, name: str, label: str, description: str,
                          established: str, layer: str, scope: str,
                          sources: List[SourceReference]) -> str:
        """Create an institution node with verified sources."""
        meta = {
            "established": established,
            "layer": layer,
            "scope": scope,
        }

        # Add source citations to metadata
        for i, source in enumerate(sources, 1):
            meta[f"source_{i}"] = source.to_citation()

        response = requests.post(
            f"{self.base_url}/nodes/",
            json={
                "label": label,
                "description": description,
                "node_type": "Institution",
                "meta": meta
            }
        )
        response.raise_for_status()
        node_id = response.json()["id"]
        self.nodes[name] = node_id
        print(f"✓ Created institution: {label} ({node_id})")
        return node_id

    def create_actor(self, name: str, label: str, description: str,
                    sector: str, role: str, sources: List[SourceReference]) -> str:
        """Create an actor node."""
        meta = {
            "sector": sector,
            "role": role,
        }
        for i, source in enumerate(sources, 1):
            meta[f"source_{i}"] = source.to_citation()

        response = requests.post(
            f"{self.base_url}/nodes/",
            json={
                "label": label,
                "description": description,
                "node_type": "Actor",
                "meta": meta
            }
        )
        response.raise_for_status()
        node_id = response.json()["id"]
        self.nodes[name] = node_id
        print(f"✓ Created actor: {label} ({node_id})")
        return node_id

    def create_policy_instrument(self, name: str, label: str, description: str,
                                 instrument_type: str, target: str,
                                 sources: List[SourceReference]) -> str:
        """Create a policy instrument node."""
        meta = {
            "instrument_type": instrument_type,
            "target_behavior": target,
        }
        for i, source in enumerate(sources, 1):
            meta[f"source_{i}"] = source.to_citation()

        response = requests.post(
            f"{self.base_url}/nodes/",
            json={
                "label": label,
                "description": description,
                "node_type": "PolicyInstrument",
                "meta": meta
            }
        )
        response.raise_for_status()
        node_id = response.json()["id"]
        self.nodes[name] = node_id
        print(f"✓ Created policy instrument: {label} ({node_id})")
        return node_id

    def create_technology(self, name: str, label: str, description: str,
                         maturity: str, sources: List[SourceReference]) -> str:
        """Create a technology node."""
        meta = {"maturity": maturity}
        for i, source in enumerate(sources, 1):
            meta[f"source_{i}"] = source.to_citation()

        response = requests.post(
            f"{self.base_url}/nodes/",
            json={
                "label": label,
                "description": description,
                "node_type": "Technology",
                "meta": meta
            }
        )
        response.raise_for_status()
        node_id = response.json()["id"]
        self.nodes[name] = node_id
        print(f"✓ Created technology: {label} ({node_id})")
        return node_id

    def create_relationship(self, source_name: str, target_name: str,
                           kind: str, weight: float, mechanism: str,
                           sources: List[SourceReference]) -> str:
        """Create a weighted relationship with evidence."""
        if source_name not in self.nodes:
            raise ValueError(f"Source node '{source_name}' not found")
        if target_name not in self.nodes:
            raise ValueError(f"Target node '{target_name}' not found")

        meta = {
            "mechanism": mechanism,
            "weight_justification": f"Based on {len(sources)} sources",
        }
        for i, source in enumerate(sources, 1):
            meta[f"source_{i}"] = source.to_citation()

        response = requests.post(
            f"{self.base_url}/relationships/",
            json={
                "source_id": self.nodes[source_name],
                "target_id": self.nodes[target_name],
                "kind": kind,
                "weight": weight,
                "meta": meta
            }
        )
        response.raise_for_status()
        rel_id = response.json()["id"]
        self.relationships.append(rel_id)
        print(f"✓ Created relationship: {source_name} --[{kind}, {weight}]--> {target_name}")
        return rel_id

    def run_ceremonial_analysis(self, threshold: float = 0.5) -> dict:
        """Run ceremonial vs. instrumental analysis."""
        response = requests.post(
            f"{self.base_url}/query/ceremonial",
            json={"threshold": threshold}
        )
        response.raise_for_status()
        return response.json()

    def find_circular_causation(self, node_name: str) -> dict:
        """Find circular causation loops from a node."""
        if node_name not in self.nodes:
            raise ValueError(f"Node '{node_name}' not found")

        response = requests.get(
            f"{self.base_url}/query/circular-causation/{self.nodes[node_name]}"
        )
        response.raise_for_status()
        return response.json()

    def detect_conflicts(self) -> dict:
        """Detect institutional conflicts."""
        response = requests.get(f"{self.base_url}/query/conflicts")
        response.raise_for_status()
        return response.json()

    def map_holarchy(self, institution_name: str) -> dict:
        """Map institutional hierarchy."""
        if institution_name not in self.nodes:
            raise ValueError(f"Institution '{institution_name}' not found")

        response = requests.get(
            f"{self.base_url}/query/holarchy/{self.nodes[institution_name]}"
        )
        response.raise_for_status()
        return response.json()

    def export_model(self) -> dict:
        """Export the complete model."""
        nodes_response = requests.get(f"{self.base_url}/nodes/")
        relationships_response = requests.get(f"{self.base_url}/relationships/")

        return {
            "metadata": {
                "scenario": "Clean Air Act 1972",
                "created": datetime.now().isoformat(),
                "node_count": len(self.nodes),
                "relationship_count": len(self.relationships),
            },
            "nodes": nodes_response.json(),
            "relationships": relationships_response.json(),
            "sources": {
                claim: [asdict(s) for s in sources]
                for claim, sources in self.sources.items()
            }
        }

    def save_model(self, filename: str):
        """Save model to JSON file."""
        model = self.export_model()
        with open(filename, 'w') as f:
            json.dump(model, f, indent=2)
        print(f"✓ Model saved to {filename}")


def build_clean_air_act_model():
    """Build the Clean Air Act SFM model."""

    print("\n" + "="*60)
    print(" Building Clean Air Act 1972 SFM Model")
    print("="*60)

    builder = SFMModelBuilder()

    # Check API connectivity
    if not builder.verify_api():
        print("\n✗ Error: Cannot connect to SFM API")
        print("Make sure the server is running:")
        print("  uvicorn api.rest.app:app --reload")
        return

    print("\n✓ API connection verified")

    # ==================================================================
    # TODO: Research and add your sources here
    # ==================================================================

    # Example source references - REPLACE WITH ACTUAL RESEARCH
    epa_source_1 = SourceReference(
        author="US EPA",
        title="EPA History",
        publisher="EPA.gov",
        year=2024,
        page_or_url="https://www.epa.gov/history"
    )

    epa_source_2 = SourceReference(
        author="US Government",
        title="Reorganization Plan No. 3 of 1970",
        publisher="Federal Register",
        year=1970,
        page_or_url="35 FR 15623"
    )

    # TODO: Add more verified sources
    # caa_source_1 = SourceReference(...)
    # caa_source_2 = SourceReference(...)

    # ==================================================================
    # PHASE 1: Create Institutions
    # ==================================================================

    print("\n" + "-"*60)
    print(" Creating Institutional Nodes")
    print("-"*60)

    # TODO: Research and create EPA node with accurate data
    builder.create_institution(
        name="epa",
        label="Environmental Protection Agency",
        description="Federal agency created in 1970 to consolidate environmental protection responsibilities",
        established="1970",
        layer="formal_rule",
        scope="federal",
        sources=[epa_source_1, epa_source_2]
    )

    # TODO: Create more institutions
    # - State environmental agencies
    # - Industry associations (Auto Manufacturers Association, etc.)
    # - Environmental advocacy groups (Sierra Club, NRDC)
    # - Congressional committees

    # ==================================================================
    # PHASE 2: Create Actors
    # ==================================================================

    print("\n" + "-"*60)
    print(" Creating Actor Nodes")
    print("-"*60)

    # TODO: Create actor nodes
    # - Federal government (regulator)
    # - Auto manufacturers (industry)
    # - Environmental groups (advocates)
    # - Affected communities (beneficiaries)
    # - Industry lobbying organizations

    # ==================================================================
    # PHASE 3: Create Policy Instruments
    # ==================================================================

    print("\n" + "-"*60)
    print(" Creating Policy Instrument Nodes")
    print("-"*60)

    # TODO: Create policy instrument nodes
    # - National Ambient Air Quality Standards (NAAQS)
    # - State Implementation Plans (SIPs)
    # - Technology-forcing provisions
    # - Enforcement mechanisms

    # ==================================================================
    # PHASE 4: Create Technologies
    # ==================================================================

    print("\n" + "-"*60)
    print(" Creating Technology Nodes")
    print("-"*60)

    # TODO: Create technology nodes
    # - Catalytic converters
    # - Smokestack scrubbers
    # - Air quality monitoring systems
    # - Alternative fuels

    # ==================================================================
    # PHASE 5: Create Relationships
    # ==================================================================

    print("\n" + "-"*60)
    print(" Creating Relationships")
    print("-"*60)

    # TODO: Create influence relationships
    # Example: EPA influences state agencies
    # builder.create_relationship(
    #     source_name="epa",
    #     target_name="state_agencies",
    #     kind="influences",
    #     weight=0.9,
    #     mechanism="Federal mandate authority under CAA Section 110",
    #     sources=[...]
    # )

    # TODO: Create dependency relationships
    # Example: Technology adoption depends on regulations

    # TODO: Create conflict relationships
    # Example: Industry profit vs. compliance costs

    # ==================================================================
    # PHASE 6: Run Analyses
    # ==================================================================

    print("\n" + "-"*60)
    print(" Running SFM Analyses")
    print("-"*60)

    # Ceremonial analysis
    print("\nRunning ceremonial analysis...")
    ceremonial = builder.run_ceremonial_analysis(threshold=0.5)
    print(f"  Ceremonial nodes: {len(ceremonial.get('ceremonial_nodes', []))}")
    print(f"  Instrumental nodes: {len(ceremonial.get('instrumental_nodes', []))}")

    # TODO: Analyze specific nodes for circular causation
    # cycles = builder.find_circular_causation("epa")

    # Conflict detection
    print("\nDetecting conflicts...")
    conflicts = builder.detect_conflicts()
    print(f"  Conflicts found: {conflicts.get('total', 0)}")

    # TODO: Map holarchy for key institutions
    # holarchy = builder.map_holarchy("epa")

    # ==================================================================
    # PHASE 7: Export and Save
    # ==================================================================

    print("\n" + "-"*60)
    print(" Exporting Model")
    print("-"*60)

    builder.save_model("clean_air_act_model.json")

    # ==================================================================
    # PHASE 8: Gap Analysis
    # ==================================================================

    print("\n" + "-"*60)
    print(" Gap Analysis Notes")
    print("-"*60)

    # TODO: Document gaps you discovered while building the model
    print("\nDuring model construction, the following gaps were identified:")
    print("  - [Add gap discoveries here]")
    print("  - Consider: missing node types, relationship kinds, analyses")
    print("  - Consider: usability issues, documentation needs")
    print("  - Consider: theoretical limitations of the framework")

    print("\n" + "="*60)
    print(" Model Building Complete!")
    print("="*60)
    print(f"\nTotal nodes created: {len(builder.nodes)}")
    print(f"Total relationships created: {len(builder.relationships)}")
    print("\nNext steps:")
    print("  1. Review the exported model: clean_air_act_model.json")
    print("  2. Complete the gap analysis documentation")
    print("  3. Validate model against historical outcomes")
    print("  4. Write up findings in docs/scenarios/clean_air_act_1972.md")


if __name__ == "__main__":
    build_clean_air_act_model()
