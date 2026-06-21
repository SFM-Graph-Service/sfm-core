"""
Ostrom SES/IAD ↔ SFM Bridge Example

Demonstrates encoding SFM institutional analysis in Ostrom's Social-Ecological
Systems (SES) and Nodeal Analysis and Development (IAD) framework vocabulary.

Key Mappings
------------
- **Rules-in-Use** (Ostrom) → **Nodes** (SFM)
- **Action Arena** (Ostrom) → **Node Cluster** (SFM)
- **Action Situations** (Ostrom) → **Delivery Cells** (SFM)
- **Actors** (Ostrom) → **Nodeal Components** (SFM)
- **Outcomes** (Ostrom) → **Criteria Evaluations** (SFM)

Conceptual Alignment
--------------------
Both frameworks analyze institutional structures and their effects:

**Ostrom SES/IAD Framework:**
- Focus: Common-pool resource governance
- Core concept: Rules-in-use shape action arenas where actors interact
- Output: Patterns of interaction → outcomes → feedback to rules
- Level: Typically meso-level (community/regional governance)

**Hayden SFM Framework:**
- Focus: Nodeal delivery chains in socio-economic systems
- Core concept: Nodes deliver benefits/harms through network relationships
- Output: Normative evaluation against social criteria
- Level: Multi-scalar (local to global)

**Bridge Value:**
SFM adds normative evaluation and delivery chain analysis to Ostrom's
structural institutional analysis. Ostrom's action situations become
traceable delivery paths that can be evaluated against social criteria.

Example Context
---------------
This example encodes a simplified common-pool resource management scenario:
- Resource: Community forest
- Action Arena: Forest management decisions
- Rules-in-Use: Harvesting quotas, monitoring protocols, sanctioning rules
- Actors: Local community association, forest users, monitoring authority
- Action Situations: Quota setting, harvesting, monitoring, sanctioning

The SFM encoding reveals:
1. How rules-in-use (institutions) deliver governance benefits
2. Which delivery chains strengthen sustainability vs. degradation
3. How outcomes feed back into institutional adaptation

References
----------
- Ostrom, E. (2005). *Understanding Nodeal Diversity*. Princeton University Press.
- Ostrom, E. (2007). A diagnostic approach for going beyond panaceas.
  *Proceedings of the National Academy of Sciences*, 104(39), 15181-15187.
- McGinnis, M. D., & Ostrom, E. (2014). Social-ecological system framework:
  initial changes and continuing challenges. *Ecology and Society*, 19(2), 30.
- Hayden, F. G. (2006). *Policymaking for a Good Society*. Springer.
- Hayden, F. G., & Bolduc, S. R. (2000). A social fabric matrix/multi-regional
  input-output analysis of low-level radioactive waste management in the United States.
  *Journal of Economic Issues*, 34(2), 367-378.

Example Output
--------------
When run, this example creates:
- SFM delivery matrix with Ostrom-compatible structure
- Action arena encoded as node cluster
- Rules-in-use as institutional nodes
- Delivery chains representing governance flows
- Normative evaluation showing sustainability outcomes

Usage
-----
>>> python examples/framework_bridges/ostrom_ses_iad_example.py
"""

from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery, SFMDeliveryMatrix
from models.matrix_components import SFMCriteria
from models.enums import CriteriaType


def build_ostrom_ses_iad_sfm() -> tuple[SFMDeliveryMatrix, SFMService]:
    """
    Build SFM encoding of Ostrom SES/IAD framework.

    Returns
    -------
    tuple[SFMDeliveryMatrix, SFMService]
        The delivery matrix and service instance

    SES/IAD → SFM Mapping
    ----------------------
    **Actors (Ostrom) → Nodeal Components (SFM):**
    - Community Association: Collective action organization
    - Forest Users: Resource appropriators
    - Monitoring Authority: Enforcement institution
    - External Authority: Government oversight

    **Rules-in-Use (Ostrom) → Nodes (SFM):**
    - Harvesting Quota Rule: Boundary rule (who can take how much)
    - Monitoring Protocol: Information rule (who knows what when)
    - Sanctioning Rule: Payoff rule (consequences of violation)
    - Deliberation Rule: Aggregation rule (collective choice process)

    **Action Arena (Ostrom) → Node Cluster (SFM):**
    - Forest Management Arena: All actors + rules in governance space

    **Action Situations (Ostrom) → Delivery Cells (SFM):**
    - Quota Setting: Association → Forest Users (authority delivery)
    - Harvesting: Forest Users → Forest Resource (extraction delivery)
    - Monitoring: Authority → Users (surveillance delivery)
    - Sanctioning: Authority → Violators (punishment delivery)
    - Deliberation: Users → Association (voice delivery)

    **Outcomes (Ostrom) → Criteria (SFM):**
    - Forest Sustainability: Environmental criterion
    - Equity: Social criterion
    - Efficiency: Economic criterion
    - Legitimacy: Political criterion
    """
    service = SFMService()

    # -------------------------------------------------------------------------
    # Define Actors (Ostrom) as Nodeal Components (SFM)
    # -------------------------------------------------------------------------

    community_association = Node(
        label="Community Forest Association",
        description="Collective action organization managing forest commons",
        meta={
            "ostrom_type": "actor",
            "ostrom_role": "collective_choice_authority",
            "sfm_category": "voluntarist_organization",
            "ses_variable": "A1 - Number of relevant actors"
        }
    )

    forest_users = Node(
        label="Forest Users (Appropriators)",
        description="Local community members harvesting forest resources",
        meta={
            "ostrom_type": "actor",
            "ostrom_role": "resource_appropriators",
            "sfm_category": "community",
            "ses_variable": "A2 - Socioeconomic attributes"
        }
    )

    monitoring_authority = Node(
        label="Forest Monitoring Authority",
        description="Node responsible for monitoring compliance",
        meta={
            "ostrom_type": "actor",
            "ostrom_role": "monitor",
            "sfm_category": "regulatory_institution",
            "ses_variable": "GS6 - Monitoring and sanctioning"
        }
    )

    external_authority = Node(
        label="External Government Authority",
        description="Higher-level government providing oversight",
        meta={
            "ostrom_type": "actor",
            "ostrom_role": "external_authority",
            "sfm_category": "government",
            "ses_variable": "GS4 - Governance systems"
        }
    )

    # -------------------------------------------------------------------------
    # Define Rules-in-Use (Ostrom) as Nodes (SFM)
    # -------------------------------------------------------------------------

    harvesting_quota_rule = Node(
        label="Harvesting Quota Rule",
        description="Boundary rule specifying who can harvest and how much",
        meta={
            "ostrom_type": "rule_in_use",
            "ostrom_rule_type": "boundary_rule",
            "iad_component": "institutional_statement",
            "sfm_category": "regulatory_rule",
            "rule_statement": "Attribute: Community members | Deontic: May | Aim: Harvest | Conditions: Up to 5 cubic meters per year | Or Else: Fine"
        }
    )

    monitoring_protocol = Node(
        label="Monitoring Protocol",
        description="Information rule defining monitoring procedures",
        meta={
            "ostrom_type": "rule_in_use",
            "ostrom_rule_type": "information_rule",
            "iad_component": "institutional_statement",
            "sfm_category": "regulatory_rule",
            "rule_statement": "Attribute: Monitors | Must: Conduct monthly forest surveys | Conditions: Random plot sampling"
        }
    )

    sanctioning_rule = Node(
        label="Sanctioning Rule",
        description="Payoff rule defining consequences for rule violations",
        meta={
            "ostrom_type": "rule_in_use",
            "ostrom_rule_type": "payoff_rule",
            "iad_component": "institutional_statement",
            "sfm_category": "regulatory_rule",
            "rule_statement": "Attribute: Violators | Must: Pay graduated fines | Or Else: Exclusion from commons"
        }
    )

    deliberation_rule = Node(
        label="Deliberation Rule",
        description="Aggregation rule for collective choice processes",
        meta={
            "ostrom_type": "rule_in_use",
            "ostrom_rule_type": "aggregation_rule",
            "iad_component": "institutional_statement",
            "sfm_category": "decision_making_rule",
            "rule_statement": "Attribute: Association members | May: Propose quota changes | Conditions: Two-thirds majority required"
        }
    )

    # -------------------------------------------------------------------------
    # Define Resource System and Resource Units (SES framework)
    # -------------------------------------------------------------------------

    forest_resource_system = Node(
        label="Community Forest (Resource System)",
        description="Common-pool forest resource system providing timber and ecosystem services",
        meta={
            "ostrom_type": "resource_system",
            "ses_variable": "RS - Resource System",
            "resource_sector": "forestry",
            "clarity_of_boundaries": "high"
        }
    )

    # -------------------------------------------------------------------------
    # Define Outcomes (Ostrom) as Criteria (SFM)
    # -------------------------------------------------------------------------

    forest_sustainability = SFMCriteria(
        label="Forest Sustainability",
        description="Maintenance of forest ecological health and regeneration capacity",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        meta={
            "ostrom_type": "outcome",
            "ses_variable": "O1 - Social performance measures",
            "measurement": "Forest biomass stability, species diversity"
        }
    )

    equity_outcome = SFMCriteria(
        label="Equity in Access",
        description="Fair distribution of harvesting rights and benefits",
        criteria_type=CriteriaType.SOCIAL,
        meta={
            "ostrom_type": "outcome",
            "ses_variable": "O2 - Ecological performance measures",
            "measurement": "Gini coefficient of harvest distribution"
        }
    )

    legitimacy_outcome = SFMCriteria(
        label="Rule Legitimacy",
        description="Community acceptance and compliance with governance rules",
        criteria_type=CriteriaType.POLITICAL,
        meta={
            "ostrom_type": "outcome",
            "ses_variable": "O3 - Externalities to other SES",
            "measurement": "Compliance rate, participation in deliberation"
        }
    )

    # Create all nodes
    service.create_node(community_association)
    service.create_node(forest_users)
    service.create_node(monitoring_authority)
    service.create_node(external_authority)
    service.create_node(harvesting_quota_rule)
    service.create_node(monitoring_protocol)
    service.create_node(sanctioning_rule)
    service.create_node(deliberation_rule)
    service.create_node(forest_resource_system)
    service.create_node(forest_sustainability)
    service.create_node(equity_outcome)
    service.create_node(legitimacy_outcome)

    # -------------------------------------------------------------------------
    # Create SFM Delivery Matrix
    # -------------------------------------------------------------------------

    matrix = service.create_delivery_matrix(
        label="Ostrom SES/IAD Forest Governance Matrix",
        description="Common-pool forest management encoded in SFM framework",
        components=[
            community_association.id,
            forest_users.id,
            monitoring_authority.id,
            external_authority.id,
            harvesting_quota_rule.id,
            monitoring_protocol.id,
            sanctioning_rule.id,
            deliberation_rule.id,
            forest_resource_system.id
        ]
    )

    # -------------------------------------------------------------------------
    # Action Situation 1: Quota Setting (Rule Delivery)
    # -------------------------------------------------------------------------

    service.add_delivery_to_matrix(
        matrix,
        community_association.id,
        forest_users.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Harvesting quota of 5 cubic meters per member per year",
            quantity=5.0,
            units="cubic_meters/member/year",
            temporal_rate="annual"
        ),
        cell_description="Association establishes and communicates harvesting quotas to forest users per boundary rule"
    )

    # -------------------------------------------------------------------------
    # Action Situation 2: Harvesting (Resource Extraction)
    # -------------------------------------------------------------------------

    service.add_delivery_to_matrix(
        matrix,
        forest_users.id,
        forest_resource_system.id,
        Delivery(
            delivery_type="extraction",
            delivery_content="Timber harvesting within quota limits",
            quantity=500.0,
            units="cubic_meters/year",
            temporal_rate="annual"
        ),
        cell_description="Forest users harvest timber following quota rule (100 members × 5 m³/member)"
    )

    # -------------------------------------------------------------------------
    # Action Situation 3: Monitoring (Information Gathering)
    # -------------------------------------------------------------------------

    service.add_delivery_to_matrix(
        matrix,
        monitoring_authority.id,
        forest_users.id,
        Delivery(
            delivery_type="information",
            delivery_content="Monthly random plot monitoring to verify compliance",
            quantity=12.0,
            units="surveys/year",
            temporal_rate="monthly"
        ),
        cell_description="Monitoring authority conducts surveillance per information rule"
    )

    # -------------------------------------------------------------------------
    # Action Situation 4: Sanctioning (Enforcement)
    # -------------------------------------------------------------------------

    service.add_delivery_to_matrix(
        matrix,
        monitoring_authority.id,
        forest_users.id,
        Delivery(
            delivery_type="sanction",
            delivery_content="Graduated fines for quota violations",
            quantity=3.0,
            units="violations_detected/year",
            temporal_rate="annual"
        ),
        cell_description="Authority applies sanctions to violators per payoff rule"
    )

    # -------------------------------------------------------------------------
    # Action Situation 5: Deliberation (Collective Choice)
    # -------------------------------------------------------------------------

    service.add_delivery_to_matrix(
        matrix,
        forest_users.id,
        community_association.id,
        Delivery(
            delivery_type="voice",
            delivery_content="Participation in annual quota deliberation meetings",
            quantity=85.0,
            units="percent_participation",
            temporal_rate="annual"
        ),
        cell_description="Users exercise voice in collective choice per aggregation rule"
    )

    # -------------------------------------------------------------------------
    # External Oversight
    # -------------------------------------------------------------------------

    service.add_delivery_to_matrix(
        matrix,
        external_authority.id,
        community_association.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Recognition of community forest management rights",
            temporal_rate="continuous"
        ),
        cell_description="External government recognizes and supports community governance"
    )

    # -------------------------------------------------------------------------
    # Link Deliveries to Outcomes (Criteria Evaluation)
    # -------------------------------------------------------------------------

    from graph.sfm_graph import Relationship

    # Forest sustainability outcome
    sustainability_rel = Relationship(
        source_id=forest_resource_system.id,
        target_id=forest_sustainability.id,
        kind="evaluates_to",
        weight=0.7  # Positive: sustainable harvest within regeneration capacity
    )
    sustainability_rel.meta["description"] = "Quota-limited harvesting maintains forest health"
    sustainability_rel.meta["correlation"] = "positive"
    service.create_relationship(sustainability_rel)

    # Equity outcome
    equity_rel = Relationship(
        source_id=community_association.id,
        target_id=equity_outcome.id,
        kind="evaluates_to",
        weight=0.8  # Positive: equal per-member quotas promote fairness
    )
    equity_rel.meta["description"] = "Equal quota allocation ensures equitable access"
    equity_rel.meta["correlation"] = "positive"
    service.create_relationship(equity_rel)

    # Legitimacy outcome
    legitimacy_rel = Relationship(
        source_id=forest_users.id,
        target_id=legitimacy_outcome.id,
        kind="evaluates_to",
        weight=0.85  # Positive: high participation indicates rule acceptance
    )
    legitimacy_rel.meta["description"] = "85% deliberation participation demonstrates rule legitimacy"
    legitimacy_rel.meta["correlation"] = "positive"
    service.create_relationship(legitimacy_rel)

    return matrix, service


def main():
    """Build and analyze Ostrom SES/IAD encoded in SFM."""
    print("Building Ostrom SES/IAD ↔ SFM Bridge Example...")
    print("=" * 80)

    matrix, service = build_ostrom_ses_iad_sfm()

    # Print matrix summary
    print("\nMatrix Summary:")
    summary = matrix.get_summary()
    print(f"  Components: {summary['components']}")
    print(f"  Non-empty cells: {summary['non_empty_cells']}")
    print(f"  Total deliveries: {summary['total_deliveries']}")

    # Print Ostrom → SFM mapping
    print("\nOstrom SES/IAD → SFM Mapping:")
    print("  Actors → Nodeal Components")
    print("  Rules-in-Use → Nodes")
    print("  Action Arena → Node Cluster (all components)")
    print("  Action Situations → Delivery Cells")
    print("  Outcomes → Criteria Evaluations")

    # List action situations (delivery cells)
    print("\nAction Situations (Delivery Cells):")
    non_empty_cells = matrix.get_non_empty_cells()
    for i, cell in enumerate(non_empty_cells, 1):
        src_node = service.get_node(cell.source_component_id)
        tgt_node = service.get_node(cell.target_component_id)
        print(f"\n  {i}. {src_node.label} → {tgt_node.label}")
        print(f"     Description: {cell.cell_description}")
        for delivery in cell.deliveries:
            print(f"     Delivery: {delivery.delivery_type} - {delivery.delivery_content}")

    # Print outcomes
    print("\nOutcomes (Criteria Evaluations):")
    all_relationships = service.list_relationships()
    criteria_rels = [rel for rel in all_relationships if rel.kind == "evaluates_to"]
    for rel in criteria_rels:
        src_node = service.get_node(rel.source_id)
        tgt_node = service.get_node(rel.target_id)
        print(f"  {src_node.label} → {tgt_node.label}")
        desc = rel.meta.get("description", "No description")
        print(f"    Weight: {rel.weight:.2f} ({desc})")

    print("\n" + "=" * 80)
    print("SFM-Ostrom Bridge Demonstrates:")
    print("  1. Rules-in-use as institutional nodes")
    print("  2. Action arena as node cluster")
    print("  3. Action situations as delivery cells")
    print("  4. Outcomes as normative criteria")
    print("  5. SFM adds delivery chain tracing + evaluation")
    print("\nSee docs/framework_bridges.md for full conceptual discussion.")


if __name__ == "__main__":
    main()
