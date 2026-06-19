"""
Resource and flow enumerations for the Social Fabric Matrix (SFM) framework.

Covers resource types, flow nature, flow types, provisioning stages,
and delivery quantification methods.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
    "ResourceType",
    "FlowNature",
    "FlowType",
    "ProvisioningStage",
    "DeliveryQuantificationMethod",
]

class ResourceType(Enum):
    """
      Classification of resource types within Social Fabric Matrix analysis.

      Categorizes different forms of resources that flow through socio-economic systems,
      including traditional economic resources and expanded categories relevant to
      institutional and technological analysis. This taxonomy enables detailed tracking
      of resource flows, dependencies, and transformations in SFM models.

      ## Theoretical Background

      Resource classification in SFM analysis extends beyond traditional economic
      categories to include social, institutional, and informational resources crucial
      for understanding modern socio-economic systems. This approach reflects the
      institutional economics recognition that economic activity depends on diverse
      resource types, many of which are not captured in conventional economic accounting.

      ## Core Resource Categories

      **Traditional Economic Resources** (Hayden's original framework):
      - NATURAL: Land, water, raw minerals, biological resources
      - PRODUCED: Machinery, infrastructure, manufactured capital goods
      - HUMAN: Labor, human capital, skills, knowledge embodied in people
      - INFORMATION: Data, R&D findings, patents, codified knowledge

      ## Usage Examples

      ### Basic Resource Creation
      ```python
      # Natural resource
      farmland = Resource(
          label="Agricultural Land",
          rtype=ResourceType.NATURAL,
          description="Fertile soil suitable for crop production"
      )

      # Produced capital resource
      manufacturing_equipment = Resource(
          label="Factory Equipment",
          rtype=ResourceType.PRODUCED,
          description="Industrial machinery for production"
      )

      # Human capital resource
      skilled_workforce = Resource(
          label="Skilled Engineering Team",
          rtype=ResourceType.HUMAN,
          description="Engineers with renewable energy expertise"
      )

      # Information resource
      climate_data = Resource(
          label="Climate Research Database",
          rtype=ResourceType.INFORMATION,
          description="Historical weather and climate datasets"
      )
      ```

      ### Financial and Economic Resources
      ```python
      # Financial capital
      investment_fund = Resource(
          label="Green Technology Investment Fund",
          rtype=ResourceType.FINANCIAL,
          description="Capital available for renewable energy projects"
      )

      # Credit resource
      development_loan = Resource(
          label="Infrastructure Development Loan",
          rtype=ResourceType.CREDIT,
          description="Long-term financing for public infrastructure"
      )
      ```

      ### Social and Network Resources
      ```python
      # Social capital
      community_networks = Resource(
          label="Local Business Networks",
          rtype=ResourceType.SOCIAL_CAPITAL,
          description="Trust relationships between local enterprises"
      )

      # Reputational resource
      brand_credibility = Resource(
          label="Corporate Environmental Reputation",
          rtype=ResourceType.REPUTATIONAL,
          description="Public trust in company's sustainability practices"
      )
      ```

      ### Infrastructure and Physical Resources
      ```python
      # Built infrastructure
      transportation_network = Resource(
          label="Regional Transportation System",
          rtype=ResourceType.TRANSPORTATION,
          description="Roads, rail, and public transit infrastructure"
      )

      # Utility infrastructure
      power_grid = Resource(
          label="Electrical Grid System",
          rtype=ResourceType.UTILITY,
          description="Electricity generation and distribution network"
      )
      ```

      ## Resource Flow Analysis

      Resources in SFM analysis participate in various flow relationships:

      ```python
      # Resource transformation flow
      iron_ore = Resource(label="Iron Ore", rtype=ResourceType.MINERAL)
      steel = Resource(label="Steel", rtype=ResourceType.PRODUCED)

      transformation_flow = Flow(
          label="Steel Production",
          nature=FlowNature.CONVERSION,
          flow_type=FlowType.MATERIAL
      )

      # Relationships showing resource transformation
      input_rel = Relationship(
          source_id=iron_ore.id,
          target_id=transformation_flow.id,
          kind=RelationshipKind.PROVIDES_INPUT
      )

      output_rel = Relationship(
          source_id=transformation_flow.id,
          target_id=steel.id,
          kind=RelationshipKind.PRODUCES
      )
      ```

      ## Extended Resource Categories

      **Energy Resources**: FOSSIL_FUEL, RENEWABLE, NUCLEAR, BIOENERGY
      - Enable detailed energy system analysis

      **Digital Resources**: DIGITAL, COMPUTATIONAL, DATA, NETWORK_INFRASTRUCTURE
      - Support analysis of digital economy and information systems

      **Institutional Resources**: ORGANIZATIONAL, REGULATORY, MANAGERIAL
      - Capture institutional capacity and governance resources

      **Temporal Resources**: TEMPORAL, HISTORICAL, FUTURE_OPTION
      - Enable analysis of time-dependent and path-dependent processes

      ## Integration with SFM Models

      ResourceType integrates with:
      - `Resource`: Primary classification for all resource entities
      - `Flow`: Specification of what type of resource is flowing
      - `Actor`: Understanding resource ownership and control
      - `PolicyInstrument`: Targeting specific resource types for policy intervention

      ## References

      - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 5:
    Resource Systems
      - Commons, J.R. (1924). "Legal Foundations of Capitalism"
      - Ostrom, E. (1990). "Governing the Commons: The Evolution of Institutions
    for Collective Action"
      - Lin, N. (2001). "Social Capital: A Theory of Social Structure and Action"
    """

    # Existing values
    NATURAL = auto()  # Land, water, raw minerals
    PRODUCED = auto()  # Machinery, infrastructures
    HUMAN = auto()  # Labor, human capital, skills
    INFORMATION = auto()  # Data, R&D findings, patents

    # Financial and Economic Resources
    FINANCIAL = auto()  # Money, securities, investments, financial instruments
    MONETARY = auto()  # Currency, liquid assets, reserves
    CREDIT = auto()  # Loans, debt instruments, financing capabilities
    EQUITY = auto()  # Ownership shares, stock, investment capital

    # Knowledge and Intellectual Resources
    INTELLECTUAL = auto()  # Patents, copyrights, trademarks, intellectual property
    KNOWLEDGE = auto()  # Explicit knowledge, theories, methodologies
    CULTURAL = auto()  # Cultural heritage, traditions, practices, languages
    CREATIVE = auto()  # Artistic, design, and creative works

    # Social and Network Resources
    SOCIAL_CAPITAL = auto()  # Trust networks, relationships, community bonds
    REPUTATIONAL = auto()  # Brand value, goodwill, credibility
    POLITICAL = auto()  # Influence, power, representation
    ACCESS = auto()  # Rights of entry or use, permissions, privileges

    # Infrastructure and Physical Resources
    BUILT = auto()  # Buildings, physical structures, permanent installations
    UTILITY = auto()  # Water systems, energy grids, telecommunications networks
    TRANSPORTATION = auto()  # Mobility infrastructure, vehicles, transit systems
    HOUSING = auto()  # Residential structures and communities

    # Energy Resources
    FOSSIL_FUEL = auto()  # Coal, oil, natural gas
    RENEWABLE = auto()  # Solar, wind, hydro, geothermal
    NUCLEAR = auto()  # Fission and fusion materials and facilities
    BIOENERGY = auto()  # Biomass, biofuels, organic energy sources

    # Natural Resources Subcategories
    LAND = auto()  # Territory, real estate, soil
    WATER = auto()  # Fresh water, marine resources, aquifers
    MINERAL = auto()  # Metals, stones, extractive resources
    BIOLOGICAL = auto()  # Flora, fauna, genetic resources
    ECOSYSTEM_SERVICE = auto()  # Natural processes, climate regulation, pollination

    # Technological Resources
    DIGITAL = auto()  # Software, algorithms, digital assets
    COMPUTATIONAL = auto()  # Computing capacity, processing power
    DATA = auto()  # Organized information, datasets, records
    NETWORK_INFRASTRUCTURE = auto()  # Internet, telecommunications, connectivity

    # Time-based Resources
    TEMPORAL = auto()  # Time availability, scheduling capacity
    HISTORICAL = auto()  # Past events, precedent, legacy resources
    FUTURE_OPTION = auto()  # Rights to future resources or opportunities

    # Capacity and System Resources
    ORGANIZATIONAL = auto()  # Structural capacity, institutional frameworks
    LOGISTICAL = auto()  # Supply chains, distribution capabilities
    REGULATORY = auto()  # Permits, certifications, compliance assets
    MANAGERIAL = auto()  # Coordination capabilities, administration
    RESILIENCE = auto()  # Adaptive capacity, redundancy, backup systems


class FlowNature(Enum):
    """
    Classification of flow types and patterns in Social Fabric Matrix systems.

    Describes the nature, direction, timing, and purpose of flows of resources,
    information, value, and other elements through socio-economic systems.
    Essential for understanding system dynamics and transformation processes
    in Hayden's institutional analysis framework.

    ## Theoretical Foundation

    Flow analysis in SFM recognizes that socio-economic systems are fundamentally
    characterized by movements of resources, information, and value between actors
    and institutions. Understanding flow patterns is crucial for identifying
    system bottlenecks, dependencies, and transformation opportunities.

    ## Core Flow Types

    **Basic Flow Directions**:
    - INPUT: Resources or value entering a process or actor
    - OUTPUT: Products, services, or value leaving a process or actor
    - TRANSFER: Direct exchange between actors without transformation

    ## Usage Examples

    ### Basic Flow Creation
    ```python
    # Input flow - resources entering production
    raw_materials_flow = Flow(
        label="Raw Material Supply",
        nature=FlowNature.INPUT,
        flow_type=FlowType.MATERIAL
    )

    # Output flow - products leaving production
    finished_goods_flow = Flow(
        label="Manufactured Products",
        nature=FlowNature.OUTPUT,
        flow_type=FlowType.MATERIAL
    )

    # Transfer flow - direct exchange
    payment_flow = Flow(
        label="Payment for Goods",
        nature=FlowNature.TRANSFER,
        flow_type=FlowType.FINANCIAL
    )
    ```

    ### Transformation-Based Flows
    ```python
    # Conversion of one resource type to another
    energy_conversion = Flow(
        label="Solar to Electrical Conversion",
        nature=FlowNature.CONVERSION,
        flow_type=FlowType.ENERGY
    )

    # Resource extraction from natural systems
    mining_flow = Flow(
        label="Mineral Extraction",
        nature=FlowNature.EXTRACTION,
        flow_type=FlowType.MATERIAL
    )

    # Recycling and circular economy flows
    recycling_flow = Flow(
        label="Waste Paper Recycling",
        nature=FlowNature.RECYCLING,
        flow_type=FlowType.MATERIAL
    )
    ```

    ### Medium-Specific Flows
    ```python
    # Financial flows
    investment_flow = Flow(
        label="Venture Capital Investment",
        nature=FlowNature.FINANCIAL,
        flow_type=FlowType.FINANCIAL
    )

    # Information flows
    data_sharing = Flow(
        label="Research Data Sharing",
        nature=FlowNature.INFORMATION,
        flow_type=FlowType.INFORMATION
    )

    # Social flows
    knowledge_transfer = Flow(
        label="Skills Transfer Program",
        nature=FlowNature.SOCIAL,
        flow_type=FlowType.SOCIAL
    )
    ```

    ### Temporal Pattern Flows
    ```python
    # Continuous steady flows
    utility_service = Flow(
        label="Electrical Power Supply",
        nature=FlowNature.CONTINUOUS,
        flow_type=FlowType.ENERGY
    )

    # Seasonal or cyclical flows
    agricultural_cycle = Flow(
        label="Seasonal Crop Harvesting",
        nature=FlowNature.SEASONAL,
        flow_type=FlowType.MATERIAL
    )

    # Feedback information flows
    performance_feedback = Flow(
        label="Performance Monitoring Data",
        nature=FlowNature.FEEDBACK,
        flow_type=FlowType.INFORMATION
    )
    ```

    ## Flow Integration with SFM Models

    ### Actor-to-Actor Flows
    ```python
    # Create actors
    manufacturer = Actor(label="Manufacturing Company", sector="Industry")
    supplier = Actor(label="Raw Material Supplier", sector="Industry")

    # Create flow between actors
    supply_chain_flow = Flow(
        label="Component Supply",
        nature=FlowNature.TRANSFER,
        flow_type=FlowType.MATERIAL
    )

    # Establish flow relationships
    supply_rel = Relationship(
        source_id=supplier.id,
        target_id=manufacturer.id,
        kind=RelationshipKind.SUPPLIES,
        flows=[supply_chain_flow.id]
    )
    ```

    ### Complex Flow Networks
    ```python
    # Multi-directional flows in circular economy
    waste_flow = Flow(
        label="Organic Waste Collection",
        nature=FlowNature.WASTE,
        flow_type=FlowType.MATERIAL
    )

    compost_flow = Flow(
        label="Compost Production",
        nature=FlowNature.RECYCLING,
        flow_type=FlowType.MATERIAL
    )

    nutrient_flow = Flow(
        label="Soil Nutrient Return",
        nature=FlowNature.CIRCULAR,
        flow_type=FlowType.MATERIAL
    )
    ```

    ## Flow Pattern Categories

    **Transformation Flows**: CONVERSION, EXTRACTION, PROCESSING, RECYCLING
    - Track resource transformation processes

    **Directional Flows**: CIRCULAR, CASCADING, RECIPROCAL, DISTRIBUTIVE
    - Analyze flow patterns and system structure

    **Purpose Flows**: PROVISIONING, REGULATING, SUPPORTING, INVESTMENT
    - Understand functional roles of different flows

    **Governance Flows**: MANDATE, COMPLIANCE, AUTHORIZATION, REPORTING
    - Track institutional control and coordination mechanisms

    ## Integration with Flow Validation

    FlowNature works with FlowType and validation systems:

    ```python
    # Valid combination - automatically validated
    financial_transfer = Flow(
        label="Grant Payment",
        nature=FlowNature.FINANCIAL,  # Financial nature
        flow_type=FlowType.FINANCIAL  # Financial type
    )

    # Invalid combination - will raise validation error
    # Flow(nature=FlowNature.FINANCIAL, flow_type=FlowType.MATERIAL)
    ```

    ## References

    - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 6: System Flows
    - Georgescu-Roegen, N. (1971). "The Entropy Law and the Economic Process"
    - Meadows, D.H. (2008). "Thinking in Systems: A Primer"
    - Checkland, P. (1999). "Systems Thinking, Systems Practice"
    """

    # Current basic flow types
    INPUT = auto()  # Resource or value entering a process
    OUTPUT = auto()  # Product, waste, or value leaving a process
    TRANSFER = auto()  # Exchange between actors without transformation

    # Transformation-based flows
    CONVERSION = auto()  # Resources transformed from one form to another
    EXTRACTION = auto()  # Removal of resources from natural systems
    PROCESSING = auto()  # Intermediate transformation steps
    RECYCLING = auto()  # Reprocessing of materials for reuse
    WASTE = auto()  # Unwanted byproducts or residuals
    DEGRADATION = auto()  # Reduction in quality or utility
    RESTORATION = auto()  # Renewal or repair of resources

    # Medium-based flows
    FINANCIAL = auto()  # Money, credit, financial instruments
    MATERIAL = auto()  # Physical goods and substances
    ENERGY = auto()  # Power, heat, electricity flows
    INFORMATION = auto()  # Data, knowledge, signals
    CULTURAL = auto()  # Values, practices, symbols
    SOCIAL = auto()  # Relationships, trust, social capital
    SERVICE = auto()  # Non-physical value delivery
    REGULATORY = auto()  # Control signals, permissions, constraints

    # Directionality flows
    CIRCULAR = auto()  # Returns to origin after processing
    CASCADING = auto()  # Sequential flows through multiple processes
    RECIPROCAL = auto()  # Bidirectional exchanges
    DISTRIBUTIVE = auto()  # One-to-many flows (distribution)
    CUMULATIVE = auto()  # Flows that build up or accumulate over time
    FEEDBACK = auto()  # Information returned to control processes

    # Temporal pattern flows
    CONTINUOUS = auto()  # Steady, uninterrupted flows
    INTERMITTENT = auto()  # Irregular or sporadic flows
    PULSED = auto()  # Regular bursts of flow
    SEASONAL = auto()  # Flows tied to natural or social cycles
    ACCELERATING = auto()  # Flows increasing in rate
    DECELERATING = auto()  # Flows decreasing in rate
    THRESHOLD = auto()  # Flows that occur after conditions are met

    # Purpose-based flows
    PROVISIONING = auto()  # Providing goods or services
    REGULATING = auto()  # Controlling system processes
    SUPPORTING = auto()  # Enabling other flows or processes
    MAINTENANCE = auto()  # Preserving system functions
    GROWTH = auto()  # Expanding system capacity
    INVESTMENT = auto()  # Building future capacity
    CONSUMPTION = auto()  # Using up resources for immediate benefit

    # Boundary-crossing flows
    IMPORT = auto()  # Flows entering from outside the system
    EXPORT = auto()  # Flows leaving the system
    INTERNAL = auto()  # Flows contained within system boundaries
    TRANSBOUNDARY = auto()  # Flows crossing multiple boundaries
    SPILLOVER = auto()  # Unintended flows across boundaries
    LEAKAGE = auto()  # Unintended escape of resources from system

    # Specific economic flows
    TAXATION = auto()  # Mandatory payments to governmental entities
    SUBSIDY = auto()  # Support payments from government to entities
    DIVIDEND = auto()  # Distribution of profits to shareholders
    WAGE = auto()  # Compensation for labor
    RENT = auto()  # Payment for use of property or resources
    INTEREST = auto()  # Payment for use of borrowed capital

    # Governance and institutional flows
    MANDATE = auto()  # Authoritative directives or requirements
    COMPLIANCE = auto()  # Conformity with rules or standards
    AUTHORIZATION = auto()  # Formal permission or approval
    CERTIFICATION = auto()  # Verification of adherence to standards
    REPORTING = auto()  # Required information disclosure


class FlowType(Enum):
    """
    Classification of flow types by medium/content in Social Fabric Matrix systems.

    Defines the fundamental types of flows that can occur between actors, processes,
    and resources in socio-economic systems. This classification complements FlowNature
    by specifying the medium or content type of what flows through the system.

    ## Usage with FlowNature

    FlowType works in combination with FlowNature to provide complete flow
    specification:

    ```python
    # Financial payment flow
    payment = Flow(
        label="Service Payment",
        nature=FlowNature.TRANSFER,     # How it flows (direct transfer)
        flow_type=FlowType.FINANCIAL    # What flows (money/financial instruments)
    )

    # Information sharing flow
    data_sharing = Flow(
        label="Research Data Sharing",
        nature=FlowNature.INFORMATION,  # How it flows (information pattern)
        flow_type=FlowType.INFORMATION  # What flows (data/knowledge)
    )

    # Material production flow
    manufacturing = Flow(
        label="Product Manufacturing",
        nature=FlowNature.CONVERSION,   # How it flows (transformation)
        flow_type=FlowType.MATERIAL     # What flows (physical goods)
    )
    ```

    ## Flow Type Categories

    - **MATERIAL**: Physical goods, substances, manufactured products
    - **ENERGY**: Power, heat, electricity, mechanical energy
    - **INFORMATION**: Data, knowledge, signals, communications
    - **FINANCIAL**: Money, credit, financial instruments, investments
    - **SOCIAL**: Relationships, trust, social capital, cultural practices

    ## Integration with Validation

    FlowType combinations with FlowNature are automatically validated:

    ```python
    # Valid combinations
    Flow(nature=FlowNature.FINANCIAL, flow_type=FlowType.FINANCIAL)  # ✓
    Flow(nature=FlowNature.MATERIAL, flow_type=FlowType.MATERIAL)    # ✓
    Flow(nature=FlowNature.ENERGY, flow_type=FlowType.ENERGY)        # ✓

    # Invalid combinations (will raise validation error)
    # Flow(nature=FlowNature.FINANCIAL, flow_type=FlowType.MATERIAL)  # ✗
    ```
    """

    MATERIAL = auto()  # Physical goods and substances
    ENERGY = auto()  # Power, heat, electricity flows
    INFORMATION = auto()  # Data, knowledge, signals
    FINANCIAL = auto()  # Money, credit, financial instruments
    SOCIAL = auto()  # Relationships, trust, social capital


class ProvisioningStage(Enum):
    """Stages in the societal provisioning process."""

    RESOURCE_EXTRACTION = auto()  # Resource extraction from environment
    PRODUCTION = auto()  # Transformation of resources
    DISTRIBUTION = auto()  # Distribution of goods/services
    CONSUMPTION = auto()  # Use of goods/services
    WASTE_DISPOSAL = auto()  # Waste and disposal management
    REGENERATION = auto()  # Environmental regeneration


class DeliveryQuantificationMethod(Enum):
    """Methods for quantifying institutional deliveries."""

    VOLUME_BASED = auto()  # Quantity of deliveries
    QUALITY_WEIGHTED = auto()  # Quality-adjusted volume
    VALUE_BASED = auto()  # Monetary or value measurement
    IMPACT_BASED = auto()  # Measured by outcomes/impact
    BENEFICIARY_COUNT = auto()  # Number of recipients
    TIME_BASED = auto()  # Delivery frequency/timing
    COMPOSITE_INDEX = auto()  # Multiple measures combined

