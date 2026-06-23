"""
Clean Air Act of 1970: Partial/Demo SFM Analysis

A demonstration of the Social Fabric Matrix analysis of the Clean Air Act of 1970,
the 1977 amendments, and the institutional framework that emerged.

SFM Methodology:
    Hayden, F. G. (2006). Policymaking for a Good Society: The Social Fabric Matrix
    Approach to Policy Analysis and Program Evaluation. Springer.

This analysis uses verified data from the EPA, Congressional Research Service,
peer-reviewed journals, and government reports.

Key Sources:
1. EPA - Evolution of the Clean Air Act
   https://www.epa.gov/clean-air-act-overview/evolution-clean-air-act

2. Congressional Research Service - Clean Air Act Summary
   https://www.congress.gov/crs-product/RL30853

3. Nature Communications - Environmental Justice Analysis (1970-2010)
   https://www.nature.com/articles/s41467-023-43492-9

4. Resources for the Future - 50 Years of the Clean Air Act
   https://www.resources.org/archives/looking-back-50-years-clean-air-act-1970/

5. University of Chicago AQLI - Clean Air Act 1970
   https://aqli.epic.uchicago.edu/post/united-states-clean-air-act-1970

6. ScienceDirect - Impact on Particulate Matter in the 1970s
   https://www.sciencedirect.com/science/article/abs/pii/S0095069623000852

Components represent the institutional framework that emerged,
with deliveries based on documented policy mechanisms, emissions data,
and verified compliance requirements.

What the Analysis Reveals:
    The SFM analysis battery demonstrates the Clean Air Act's institutional structure
    as a multi-level holarchy (federal→state→local) with strong ceremonial-instrumental
    balance. The analysis identifies:

    1. Circular causation paths: EPA standards → state implementation → emissions
       reductions → health improvements → public support → stronger standards

    2. Institutional holarchy: Three distinct governance levels (federal, state, local)
       with clear authority deliveries and compliance requirements

    3. Ceremonial vs instrumental: Technology-forcing requirements (instrumental)
       balanced by cooperative federalism and state autonomy (ceremonial preservation)

    4. Feedback cycles: Emission monitoring → violations → enforcement → compliance
       creates closed-loop regulatory system

    5. Conflicts: Environmental justice gaps reveal contradictions between universal
       air quality goals and disproportionate exposure in EJ communities
"""

from pathlib import Path
from datetime import timedelta
from api.sfm_service import SFMService
from models import Node, SFMCriteria
from models.sfm_enums import CriteriaType, CriteriaPriority
from models.delivery_matrix import Delivery, SFMDeliveryMatrix
from models.temporal_clocks import TemporalClock, TemporalPhase
from graph.exporters import export_delivery_matrix_to_xlsx
from graph.analysis_report import run_analysis_battery, format_report
from graph.criteria_evaluation import evaluate_against_criteria, format_evaluation_report
from graph.centrality import compute_centrality_metrics, format_centrality_report, identify_power_brokers
from graph import Relationship


def create_clean_air_act_matrix():
    """
    Create demonstration SFM for Clean Air Act of 1970.

    Uses verified data from EPA, CRS, and peer-reviewed sources.
    Demonstrates key institutional relationships and documented deliveries.
    """
    service = SFMService()

    # =========================================================================
    # STEP 1: Federal Institutions
    # =========================================================================

    # Congress passed the Clean Air Act in December 1970
    congress = Node(
        label="U.S. Congress",
        description="Legislative body that passed Clean Air Act of 1970 and 1977 amendments"
    )

    # EPA created December 2, 1970 to implement the Act
    epa = Node(
        label="Environmental Protection Agency (EPA)",
        description="Federal agency created 1970 to implement Clean Air Act, headed by William D. Ruckelshaus"
    )

    # President Nixon signed the Act and created EPA
    executive_branch = Node(
        label="Executive Branch (Nixon Administration)",
        description="Presidential authority over EPA and enforcement"
    )

    # DOJ enforces violations
    doj = Node(
        label="Department of Justice",
        description="Enforcement of Clean Air Act violations through civil and criminal penalties"
    )

    # =========================================================================
    # STEP 2: State and Local Institutions
    # =========================================================================

    # All 50 states had air pollution programs by 1970
    # Source: EPA Evolution of the Clean Air Act
    state_agencies = Node(
        label="State Air Pollution Control Agencies (50 states)",
        description="State agencies responsible for State Implementation Plans (SIPs), all 50 states had programs by 1970"
    )

    # Local air quality management districts
    local_aqmd = Node(
        label="Local Air Quality Management Districts",
        description="Regional agencies implementing local air quality programs (e.g., South Coast AQMD in Los Angeles)"
    )

    # =========================================================================
    # STEP 3: Regulated Industries
    # =========================================================================

    # Automobile manufacturers - required 90% reduction by 1975
    # Source: CRS Clean Air Act Summary
    auto_manufacturers = Node(
        label="Automobile Manufacturers (GM, Ford, Chrysler)",
        description="Big Three automakers required to reduce emissions 90% by 1975, forced to adopt catalytic converters"
    )

    # Electric utilities - major source of SO2 and NOx
    # Source: Nature Communications emissions data
    electric_utilities = Node(
        label="Electric Power Plants",
        description="Coal-fired power plants, major sources of SO2 (9.0 kg/km²/day in 1970) and NOx (2.5 kg/km²/day)"
    )

    # Industrial sources - steel, chemical, manufacturing
    industrial_sources = Node(
        label="Industrial Facilities (Steel, Chemical, Manufacturing)",
        description="Stationary sources subject to New Source Performance Standards (NSPS), SO2 emissions 5.6 kg/km²/day in 1970"
    )

    # Oil refineries
    oil_refineries = Node(
        label="Oil Refineries",
        description="Petroleum refining operations subject to NSPS and hazardous air pollutant standards"
    )

    # =========================================================================
    # STEP 4: Technology Providers
    # =========================================================================

    # Catalytic converter manufacturers - mandated 1975
    # Source: EPA motor vehicle compliance program
    catalytic_converter_industry = Node(
        label="Catalytic Converter Manufacturers",
        description="Suppliers of emission control technology mandated for 1975+ vehicles, $300-1000 per unit"
    )

    # Pollution control equipment manufacturers
    pollution_control_industry = Node(
        label="Pollution Control Equipment Industry",
        description="Manufacturers of scrubbers, electrostatic precipitators, baghouses for industrial facilities"
    )

    # =========================================================================
    # STEP 5: Scientific and Advisory Bodies
    # =========================================================================

    # Created by 1977 amendments
    # Source: EPA Evolution of the Clean Air Act
    casac = Node(
        label="Clean Air Scientific Advisory Committee (CASAC)",
        description="Independent scientific review committee created 1977 to provide technical input on NAAQS to EPA"
    )

    # Research institutions
    research_institutions = Node(
        label="Air Quality Research Institutions",
        description="Universities and national labs conducting emissions research and health studies"
    )

    # =========================================================================
    # STEP 6: Affected Populations
    # =========================================================================

    # American public - health beneficiaries
    # Source: University of Chicago AQLI - PM2.5 reduced to 35.1% of 1970 levels
    american_public = Node(
        label="American Public (210 million in 1970)",
        description="Population exposed to air pollution, PM2.5 reduced to 35.1% of 1970 levels by 2020"
    )

    # Environmental health communities
    # Focus on disproportionate impacts
    environmental_justice_communities = Node(
        label="Environmental Justice Communities",
        description="Low-income and minority communities disproportionately exposed to air pollution from industrial sources"
    )

    # =========================================================================
    # STEP 7: Advocacy and Interest Groups
    # =========================================================================

    environmental_groups = Node(
        label="Environmental Advocacy Organizations (NRDC, Sierra Club, EDF)",
        description="NGOs advocating for strong air quality standards and enforcement"
    )

    industry_associations = Node(
        label="Industry Trade Associations (NAM, API, Motor Vehicle Manufacturers Assoc.)",
        description="Business groups lobbying for flexible compliance timelines and cost considerations"
    )

    # =========================================================================
    # Register all components
    # =========================================================================

    components = [
        congress, epa, executive_branch, doj,
        state_agencies, local_aqmd,
        auto_manufacturers, electric_utilities, industrial_sources, oil_refineries,
        catalytic_converter_industry, pollution_control_industry,
        casac, research_institutions,
        american_public, environmental_justice_communities,
        environmental_groups, industry_associations
    ]

    for comp in components:
        service.create_node(comp)

    # =========================================================================
    # Create delivery matrix
    # =========================================================================

    matrix = service.create_delivery_matrix(
        label="Clean Air Act of 1970: Institutional Framework",
        description="Comprehensive analysis of Clean Air Act implementation with verified emissions data and institutional relationships",
        components=[c.id for c in components],
        matrix_scope="national"
    )

    # =========================================================================
    # DELIVERIES: Legislative Framework (Congress → Federal Agencies)
    # =========================================================================

    # Congress → EPA: Legislative authority
    service.add_delivery_to_matrix(
        matrix,
        congress.id,
        epa.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Legislative authority to set National Ambient Air Quality Standards (NAAQS) for six criteria pollutants",
            certainty=1.0,
            data_sources=["Clean Air Act of 1970, 42 U.S.C. §7401 et seq."]
        ),
        cell_description="Congress grants EPA regulatory authority over air pollution through NAAQS, NSPS, NESHAPS, and mobile source standards"
    )

    service.add_delivery_to_matrix(
        matrix,
        congress.id,
        epa.id,
        Delivery(
            delivery_type="money",
            delivery_content="Federal appropriations for EPA operations and grants to states",
            quantity=1_400_000_000,  # EPA budget grew from ~$1.4B in early 1970s
            units="USD/year",
            temporal_rate="annual",
            certainty=0.90,
            data_sources=["EPA Historical Budget Authority"]
        ),
        cell_description="Congress grants EPA regulatory authority over air pollution through NAAQS, NSPS, NESHAPS, and mobile source standards"
    )

    service.add_delivery_to_matrix(
        matrix,
        congress.id,
        epa.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Mandatory deadlines: NAAQS by 1971, state compliance by 1975 (later extended to 1977)",
            certainty=1.0,
            data_sources=["Clean Air Act §109, §110"]
        ),
        cell_description="Congress grants EPA regulatory authority over air pollution through NAAQS, NSPS, NESHAPS, and mobile source standards"
    )

    # Congress → States: Cooperative federalism mandate
    service.add_delivery_to_matrix(
        matrix,
        congress.id,
        state_agencies.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Requirement to develop State Implementation Plans (SIPs) to achieve NAAQS",
            certainty=1.0,
            data_sources=["Clean Air Act §110"]
        ),
        cell_description="Congress mandates state leadership in air quality management through State Implementation Plans"
    )

    service.add_delivery_to_matrix(
        matrix,
        congress.id,
        state_agencies.id,
        Delivery(
            delivery_type="money",
            delivery_content="Federal planning grants to state air pollution control agencies (authorized under 1967 Air Quality Act, continued)",
            certainty=0.85,
            data_sources=["Clean Air Act §105, EPA State/Local Grant Programs"]
        ),
        cell_description="Congress mandates state leadership in air quality management through State Implementation Plans"
    )

    # =========================================================================
    # DELIVERIES: EPA → States (Federal-State Relationship)
    # =========================================================================

    # EPA → States: NAAQS standards
    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        state_agencies.id,
        Delivery(
            delivery_type="rule",
            delivery_content="National Ambient Air Quality Standards for six criteria pollutants (CO, lead, NO2, ozone, PM, SO2)",
            certainty=1.0,
            data_sources=["40 CFR Part 50"]
        ),
        cell_description="EPA sets national air quality standards that states must achieve through SIPs"
    )

    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        state_agencies.id,
        Delivery(
            delivery_type="information",
            delivery_content="Technical guidance for SIP development, emissions inventories, and monitoring requirements",
            certainty=0.95,
            data_sources=["EPA SIP Requirements, 40 CFR Part 51"]
        ),
        cell_description="EPA sets national air quality standards that states must achieve through SIPs"
    )

    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        state_agencies.id,
        Delivery(
            delivery_type="authority",
            delivery_content="SIP approval authority and enforcement backstop (EPA can impose Federal Implementation Plan if state fails)",
            certainty=1.0,
            data_sources=["Clean Air Act §110(c)"]
        ),
        cell_description="EPA sets national air quality standards that states must achieve through SIPs"
    )

    # States → EPA: SIP submissions
    service.add_delivery_to_matrix(
        matrix,
        state_agencies.id,
        epa.id,
        Delivery(
            delivery_type="information",
            delivery_content="State Implementation Plans detailing how state will achieve NAAQS (Utah submitted January 1972)",
            certainty=1.0,
            data_sources=["Clean Air Act §110(a)", "Utah SIP history"]
        ),
        cell_description="States submit implementation plans for EPA approval, demonstrating path to NAAQS compliance"
    )

    service.add_delivery_to_matrix(
        matrix,
        state_agencies.id,
        epa.id,
        Delivery(
            delivery_type="information",
            delivery_content="Emissions inventories, air quality monitoring data, and compliance reports",
            temporal_rate="continuous",
            certainty=0.95,
            data_sources=["40 CFR Part 51"]
        ),
        cell_description="States submit implementation plans for EPA approval, demonstrating path to NAAQS compliance"
    )

    # =========================================================================
    # DELIVERIES: EPA → Regulated Industries
    # =========================================================================

    # EPA → Auto manufacturers: Emissions standards
    # Source: 90% reduction requirement by 1975, catalytic converter forced 1975
    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        auto_manufacturers.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Mobile source emission standards: 90% reduction in hydrocarbons and CO by 1975, NOx by 1976",
            certainty=1.0,
            data_sources=["Clean Air Act §202(b)", "40 CFR Part 86"]
        ),
        cell_description="EPA imposes technology-forcing emissions standards on automobile manufacturers"
    )

    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        auto_manufacturers.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Certification requirements for new vehicles and warranty requirements for emission control equipment (8 years/80,000 miles)",
            certainty=1.0,
            data_sources=["Clean Air Act §207", "40 CFR §85.2122"]
        ),
        cell_description="EPA imposes technology-forcing emissions standards on automobile manufacturers"
    )

    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        auto_manufacturers.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Enforcement authority with penalties up to $45,268 per noncompliant vehicle",
            quantity=45_268,
            units="USD per vehicle",
            certainty=1.0,
            data_sources=["Clean Air Act §205", "EPA enforcement penalties 2024"]
        ),
        cell_description="EPA imposes technology-forcing emissions standards on automobile manufacturers"
    )

    # EPA → Electric utilities: SO2 and NOx standards
    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        electric_utilities.id,
        Delivery(
            delivery_type="rule",
            delivery_content="New Source Performance Standards (NSPS) for coal-fired power plants limiting SO2 and NOx emissions",
            certainty=1.0,
            data_sources=["40 CFR Part 60, Subpart D and Da"]
        ),
        cell_description="EPA regulates electric power plant emissions through NSPS and SIP requirements"
    )

    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        electric_utilities.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Continuous emissions monitoring requirements for compliance verification",
            temporal_rate="continuous",
            certainty=1.0,
            data_sources=["40 CFR Part 75"]
        ),
        cell_description="EPA regulates electric power plant emissions through NSPS and SIP requirements"
    )

    # EPA → Industrial sources: NSPS and NESHAPS
    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        industrial_sources.id,
        Delivery(
            delivery_type="rule",
            delivery_content="New Source Performance Standards for major industrial categories (steel, cement, chemicals)",
            certainty=1.0,
            data_sources=["40 CFR Part 60"]
        ),
        cell_description="EPA regulates industrial emissions through technology-based standards"
    )

    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        industrial_sources.id,
        Delivery(
            delivery_type="rule",
            delivery_content="National Emission Standards for Hazardous Air Pollutants (NESHAPS)",
            certainty=1.0,
            data_sources=["40 CFR Part 61"]
        ),
        cell_description="EPA regulates industrial emissions through technology-based standards"
    )

    # =========================================================================
    # DELIVERIES: Industry Compliance (Pollution Deliveries)
    # =========================================================================

    # Auto manufacturers → American public: Vehicle emissions
    # Source: Nature Communications - Transportation NOx 5.2 → 2.2 kg/km²/day (57.7% reduction)
    service.add_delivery_to_matrix(
        matrix,
        auto_manufacturers.id,
        american_public.id,
        Delivery(
            delivery_type="pollution",
            delivery_content="Nitrogen oxides from vehicles: 5.2 kg/km²/day (1970) reduced to 2.2 kg/km²/day by 2010",
            quantity=5.2,  # 1970 baseline
            units="kg/km²/day",
            temporal_rate="continuous",
            threshold=2.2,  # Target level achieved by 2010
            threshold_direction="below",
            certainty=0.95,
            data_sources=["Nature Communications s41467-023-43492-9, Transportation NOx emissions data"]
        ),
        cell_description="Automobile manufacturers emit air pollutants that impact public health, with dramatic reductions post-1975 due to catalytic converters"
    )

    service.add_delivery_to_matrix(
        matrix,
        auto_manufacturers.id,
        american_public.id,
        Delivery(
            delivery_type="pollution",
            delivery_content="Particulate matter from vehicles: >90% reduction from 1970 levels due to diesel particulate filters and cleaner engines",
            certainty=0.95,
            data_sources=["Clean Air Act 55 Years progress report"]
        ),
        cell_description="Automobile manufacturers emit air pollutants that impact public health, with dramatic reductions post-1975 due to catalytic converters"
    )

    # Electric utilities → American public: Power plant emissions
    # Source: Nature Communications - Energy SO2 9.0 → 3.0 kg/km²/day (66.7% reduction)
    service.add_delivery_to_matrix(
        matrix,
        electric_utilities.id,
        american_public.id,
        Delivery(
            delivery_type="pollution",
            delivery_content="Sulfur dioxide from power plants: 9.0 kg/km²/day (1970) reduced to 3.0 kg/km²/day by 2010",
            quantity=9.0,  # 1970 baseline
            units="kg/km²/day",
            temporal_rate="continuous",
            threshold=3.0,  # 2010 level (66.7% reduction)
            threshold_direction="below",
            certainty=0.95,
            data_sources=["Nature Communications s41467-023-43492-9, Energy sector SO2 emissions"]
        ),
        cell_description="Electric power plants emit SO2 and NOx causing acid rain and respiratory health impacts"
    )

    service.add_delivery_to_matrix(
        matrix,
        electric_utilities.id,
        american_public.id,
        Delivery(
            delivery_type="pollution",
            delivery_content="Nitrogen oxides from power plants: 2.5 kg/km²/day (1970) reduced to 1.5 kg/km²/day by 2010",
            quantity=2.5,
            units="kg/km²/day",
            temporal_rate="continuous",
            threshold=1.5,
            threshold_direction="below",
            certainty=0.95,
            data_sources=["Nature Communications s41467-023-43492-9, Energy sector NOx emissions"]
        ),
        cell_description="Electric power plants emit SO2 and NOx causing acid rain and respiratory health impacts"
    )

    # Industrial sources → American public and EJ communities
    # Source: Nature Communications - Industry SO2 5.6 → 0.6 kg/km²/day (89.3% reduction)
    service.add_delivery_to_matrix(
        matrix,
        industrial_sources.id,
        american_public.id,
        Delivery(
            delivery_type="pollution",
            delivery_content="Sulfur dioxide from industrial sources: 5.6 kg/km²/day (1970) reduced to 0.6 kg/km²/day by 2010",
            quantity=5.6,
            units="kg/km²/day",
            temporal_rate="continuous",
            threshold=0.6,
            threshold_direction="below",
            certainty=0.95,
            data_sources=["Nature Communications s41467-023-43492-9, Industry sector SO2 emissions"]
        ),
        cell_description="Industrial facilities emit criteria pollutants and hazardous air pollutants affecting nearby populations"
    )

    service.add_delivery_to_matrix(
        matrix,
        industrial_sources.id,
        american_public.id,
        Delivery(
            delivery_type="pollution",
            delivery_content="Particulate matter from industry: 50% reduction by 1980 through industrial emission controls",
            certainty=0.95,
            data_sources=["ScienceDirect - Impact on particulate matter in the 1970s"]
        ),
        cell_description="Industrial facilities emit criteria pollutants and hazardous air pollutants affecting nearby populations"
    )

    # Industrial sources → Environmental justice communities
    # Disproportionate exposure documented in Nature Communications paper
    service.add_delivery_to_matrix(
        matrix,
        industrial_sources.id,
        environmental_justice_communities.id,
        Delivery(
            delivery_type="pollution",
            delivery_content="Disproportionate exposure to industrial air pollution in low-income and minority communities located near facilities",
            certainty=0.90,
            data_sources=["Nature Communications s41467-023-43492-9, Environmental justice analysis 1970-2010"]
        ),
        cell_description="Industrial facilities disproportionately impact environmental justice communities through proximity and exposure patterns"
    )

    # =========================================================================
    # DELIVERIES: Technology Adoption (Industry → Technology Providers)
    # =========================================================================

    # Auto manufacturers → Catalytic converter industry
    # Source: EPA forced adoption of catalytic converter in 1975
    service.add_delivery_to_matrix(
        matrix,
        auto_manufacturers.id,
        catalytic_converter_industry.id,
        Delivery(
            delivery_type="money",
            delivery_content="Purchase of catalytic converters for all 1975+ model year vehicles at $300-1000 per unit",
            quantity=500,  # Approximate mid-range cost
            units="USD per vehicle",
            temporal_rate="continuous",
            certainty=0.90,
            data_sources=["EPA catalytic converter requirements", "Replacement cost data $300-1000"]
        ),
        cell_description="Automobile manufacturers forced to adopt catalytic converter technology beginning 1975 model year"
    )

    # Catalytic converter industry → Auto manufacturers
    service.add_delivery_to_matrix(
        matrix,
        catalytic_converter_industry.id,
        auto_manufacturers.id,
        Delivery(
            delivery_type="energy",  # Using "energy" type for technology/service delivery
            delivery_content="Catalytic converter technology enabling 90% reduction in hydrocarbons and CO emissions",
            certainty=0.95,
            data_sources=["EPA successfully forced adoption of catalytic converter 1975"]
        ),
        cell_description="Technology suppliers provide emission control equipment enabling regulatory compliance"
    )

    # Electric utilities → Pollution control industry
    service.add_delivery_to_matrix(
        matrix,
        electric_utilities.id,
        pollution_control_industry.id,
        Delivery(
            delivery_type="money",
            delivery_content="Purchase and installation of scrubbers, electrostatic precipitators, and baghouses for SO2 and particulate control",
            temporal_rate="continuous",
            certainty=0.90,
            data_sources=["40 CFR Part 60 - NSPS requirements for power plants"]
        ),
        cell_description="Electric utilities install pollution control equipment to meet NSPS and SIP requirements"
    )

    # Industrial sources → Pollution control industry
    service.add_delivery_to_matrix(
        matrix,
        industrial_sources.id,
        pollution_control_industry.id,
        Delivery(
            delivery_type="money",
            delivery_content="Investment in pollution control technology to meet NSPS standards",
            temporal_rate="continuous",
            certainty=0.90,
            data_sources=["40 CFR Part 60 - NSPS for industrial categories"]
        ),
        cell_description="Industrial facilities install control technology to comply with federal and state emissions limits"
    )

    # =========================================================================
    # DELIVERIES: Scientific Input
    # =========================================================================

    # Research institutions → EPA
    service.add_delivery_to_matrix(
        matrix,
        research_institutions.id,
        epa.id,
        Delivery(
            delivery_type="information",
            delivery_content="Air quality research on health effects, emissions modeling, and control technology effectiveness",
            temporal_rate="continuous",
            certainty=0.90,
            data_sources=["EPA air quality research programs"]
        ),
        cell_description="Research institutions provide scientific basis for NAAQS and regulatory decisions"
    )

    # CASAC → EPA (created 1977)
    service.add_delivery_to_matrix(
        matrix,
        casac.id,
        epa.id,
        Delivery(
            delivery_type="information",
            delivery_content="Independent scientific review of NAAQS criteria documents and recommendations (established 1977 amendments)",
            temporal_rate="continuous",
            certainty=1.0,
            data_sources=["Clean Air Act 1977 amendments - CASAC creation"]
        ),
        cell_description="CASAC provides independent scientific peer review of air quality standards since 1977"
    )

    # =========================================================================
    # DELIVERIES: Advocacy and Public Participation
    # =========================================================================

    # Environmental groups → EPA
    service.add_delivery_to_matrix(
        matrix,
        environmental_groups.id,
        epa.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Advocacy for stringent NAAQS, petitions for new standards, and litigation to enforce deadlines",
            temporal_rate="continuous",
            certainty=0.85,
            data_sources=["NRDC, Sierra Club, EDF historical advocacy"]
        ),
        cell_description="Environmental organizations advocate for strong air quality protections and sue to enforce compliance"
    )

    # Environmental groups → Congress
    service.add_delivery_to_matrix(
        matrix,
        environmental_groups.id,
        congress.id,
        Delivery(
            delivery_type="information",
            delivery_content="Legislative advocacy for Clean Air Act passage and amendments, public health documentation",
            certainty=0.85,
            data_sources=["Environmental organization legislative advocacy 1970, 1977"]
        ),
        cell_description="Environmental groups mobilize public support and provide legislative advocacy for air quality laws"
    )

    # Industry associations → EPA
    service.add_delivery_to_matrix(
        matrix,
        industry_associations.id,
        epa.id,
        Delivery(
            delivery_type="information",
            delivery_content="Technical comments on proposed rules, compliance cost analyses, requests for deadline extensions",
            temporal_rate="continuous",
            certainty=0.90,
            data_sources=["Industry participation in EPA rulemakings"]
        ),
        cell_description="Industry trade groups advocate for flexible compliance timelines and cost considerations in rulemaking"
    )

    # Industry associations → Congress
    service.add_delivery_to_matrix(
        matrix,
        industry_associations.id,
        congress.id,
        Delivery(
            delivery_type="information",
            delivery_content="Lobbying for technology feasibility timelines and economic impact considerations in legislation",
            certainty=0.90,
            data_sources=["Industry lobbying on 1970 Act and 1977 amendments"]
        ),
        cell_description="Industry associations lobby Congress on compliance timelines and economic impacts"
    )

    # =========================================================================
    # DELIVERIES: Enforcement
    # =========================================================================

    # EPA → DOJ: Enforcement referrals
    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        doj.id,
        Delivery(
            delivery_type="information",
            delivery_content="Referrals of Clean Air Act violations for civil and criminal prosecution",
            temporal_rate="continuous",
            certainty=0.95,
            data_sources=["Clean Air Act §113 enforcement authority"]
        ),
        cell_description="EPA refers significant violations to Department of Justice for enforcement actions"
    )

    # DOJ → Violating industries: Penalties
    service.add_delivery_to_matrix(
        matrix,
        doj.id,
        auto_manufacturers.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Civil penalties and consent decrees for violations (e.g., 2024 enforcement actions: $13M+ in penalties)",
            quantity=13_000_000,
            units="USD in penalties",
            temporal_rate="event_triggered",
            certainty=0.95,
            data_sources=["EPA 2024 enforcement actions - over $13 million in penalties"]
        ),
        cell_description="DOJ enforces Clean Air Act through civil and criminal penalties against violators"
    )

    # =========================================================================
    # DELIVERIES: Health Benefits
    # =========================================================================

    # Reduced pollution → American public: Health benefits
    # Source: PM2.5 reduced to 35.1% of 1970 levels, combined pollutants down 78%
    service.add_delivery_to_matrix(
        matrix,
        epa.id,
        american_public.id,
        Delivery(
            delivery_type="energy",  # Using "energy" for health/service delivery
            delivery_content="Dramatic air quality improvements: PM2.5 reduced to 35.1% of 1970 levels, combined six pollutants down 78% (1970-2020)",
            certainty=0.95,
            data_sources=["University of Chicago AQLI - PM2.5 at 35.1% of 1970 levels", "EPA - 78% reduction in six pollutants 1970-2020"]
        ),
        cell_description="Clean Air Act implementation delivers substantial public health benefits through dramatic pollution reductions"
    )

    # =========================================================================
    # CRITERIA: Normative Evaluation Framework
    # =========================================================================
    # Add criteria to evaluate deliveries against social goals

    # Criterion 1: Public Health Protection
    public_health = SFMCriteria(
        label="Public Health Protection",
        description="Protection of public health from air pollution hazards",
        criteria_type=CriteriaType.SOCIAL,
        priority=CriteriaPriority.PRIMARY,
        weight=1.0,
        life_process_relevance=0.95,
        instrumental_capacity=0.90,
        ceremonial_bias_risk=0.10,
        normative_justification="Primary purpose of Clean Air Act (Section 101) is to 'protect and enhance the quality of the Nation's air resources so as to promote the public health and welfare'"
    )
    service.create_node(public_health)

    # Criterion 2: Environmental Justice
    environmental_justice = SFMCriteria(
        label="Environmental Justice",
        description="Equitable distribution of air quality benefits and burdens across communities",
        criteria_type=CriteriaType.SOCIAL,
        priority=CriteriaPriority.PRIMARY,
        weight=0.85,
        life_process_relevance=0.90,
        instrumental_capacity=0.70,
        ceremonial_bias_risk=0.40,
        normative_justification="Executive Order 12898 (1994) and EPA's environmental justice mandate require fair treatment of all communities"
    )
    service.create_node(environmental_justice)

    # Criterion 3: Technology Forcing & Innovation
    technology_forcing = SFMCriteria(
        label="Technology Forcing & Innovation",
        description="Stimulation of pollution control technology development",
        criteria_type=CriteriaType.TECHNOLOGICAL,
        priority=CriteriaPriority.SECONDARY,
        weight=0.75,
        life_process_relevance=0.80,
        instrumental_capacity=0.95,
        ceremonial_bias_risk=0.15,
        normative_justification="Clean Air Act's technology-forcing provisions drive innovation in pollution control (catalytic converter, scrubbers)"
    )
    service.create_node(technology_forcing)

    # =========================================================================
    # LINK DELIVERIES TO CRITERIA via Relationships
    # =========================================================================
    # Create relationships that link delivery cells to criteria they serve/undermine
    # Uses SFMDeliveryMatrix cells (not DeliveryRelationship nodes)

    # Get the delivery matrix
    matrices = [n for n in service.list_nodes() if isinstance(n, SFMDeliveryMatrix)]
    if matrices:
        delivery_matrix = matrices[0]  # Should only be one matrix in this case study

        # Link: EPA → american_public cell SERVES public health criterion
        epa_to_public_cell = delivery_matrix.get_cell(epa.id, american_public.id)
        if epa_to_public_cell:
            service.create_relationship(
                Relationship(
                    source_id=epa_to_public_cell.id,
                    target_id=public_health.id,
                    kind="evaluates_to",
                    weight=0.95  # Strong positive alignment - health deliveries serve health criterion
                )
            )

        # Link: EPA → auto_manufacturers cell SERVES technology forcing criterion
        # (EPA standards drive catalytic converter innovation)
        epa_to_auto_cell = delivery_matrix.get_cell(epa.id, auto_manufacturers.id)
        if epa_to_auto_cell:
            service.create_relationship(
                Relationship(
                    source_id=epa_to_auto_cell.id,
                    target_id=technology_forcing.id,
                    kind="evaluates_to",
                    weight=0.90  # Strong positive - technology-forcing standards
                )
            )

        # Link: auto_manufacturers → american_public cell also SERVES public health
        # (Catalytic converters reduce pollution exposure)
        auto_to_public_cell = delivery_matrix.get_cell(auto_manufacturers.id, american_public.id)
        if auto_to_public_cell:
            service.create_relationship(
                Relationship(
                    source_id=auto_to_public_cell.id,
                    target_id=public_health.id,
                    kind="evaluates_to",
                    weight=0.75  # Positive - cleaner cars improve health
                )
            )

        # Link: industrial_facilities → american_public cell UNDERMINES environmental justice
        # (Pollution disproportionately impacts EJ communities)
        # Note: Looking for cells where industrial facilities deliver pollution to public
        for (source_id, target_id), cell in delivery_matrix.cells.items():
            # Check if this is an industrial facility delivering pollution
            source_node = service.get_node(source_id)
            target_node = service.get_node(target_id)

            if (source_node and target_node and
                source_node.label in ["Steel Mill", "Chemical Plant", "Oil Refinery"] and
                target_node.label == "American Public"):
                # Industrial pollution deliveries undermine environmental justice
                service.create_relationship(
                    Relationship(
                        source_id=cell.id,
                        target_id=environmental_justice.id,
                        kind="evaluates_to",
                        weight=-0.80  # Strong negative - disproportionate harm
                    )
                )

    return matrix, service


def create_clean_air_temporal_clock(service):
    """
    Create temporal clock for Clean Air Act implementation timeline.

    Key dates (verified):
    - December 31, 1970: Clean Air Act signed
    - April 30, 1971: NAAQS promulgation deadline
    - May 31, 1972: SIP submission deadline (9 months after NAAQS)
    - 1975: Original attainment deadline (extended to 1977)
    - 1977: Clean Air Act Amendments
    """

    # Create implementation clock with phases
    clock = TemporalClock(
        label="Clean Air Act Implementation Timeline",
        clock_name="clean_air_act_timeline",
        description="Major implementation milestones from 1970 Act passage through 1977 amendments",
        period_length=timedelta(days=2585),  # ~7.1 years (1970-1977)
    )

    # Phase 1: NAAQS Development (1970-1971)
    clock.add_phase(TemporalPhase(
        phase_name="naaqs_development",
        duration=timedelta(days=486),  # ~16 months
        activities=["EPA establishment", "NAAQS promulgation for six criteria pollutants"]
    ))

    # Phase 2: SIP Development (1971-1972)
    clock.add_phase(TemporalPhase(
        phase_name="sip_development",
        duration=timedelta(days=274),  # ~9 months
        activities=["States develop implementation plans", "Public comment and hearings"]
    ))

    # Phase 3: Initial Implementation (1972-1975)
    clock.add_phase(TemporalPhase(
        phase_name="initial_implementation",
        duration=timedelta(days=1095),  # 3 years
        activities=["State enforcement begins", "NSPS for new sources", "Auto emission standards phase-in", "Catalytic converter adoption 1975"]
    ))

    # Phase 4: Deadline Failure and Extension (1975-1977)
    clock.add_phase(TemporalPhase(
        phase_name="deadline_extension",
        duration=timedelta(days=730),  # 2 years
        activities=["Many areas fail to meet 1975 deadline", "1977 amendments set new goals", "CASAC established"]
    ))

    clock.current_phase = "naaqs_development"
    service.create_node(clock)

    return clock


def main():
    """Generate Clean Air Act SFM with verified data."""

    print("=" * 80)
    print("CLEAN AIR ACT OF 1970: DEMONSTRATION SFM ANALYSIS")
    print("Using Verified Data from EPA, CRS, Nature Communications, and Peer-Reviewed Sources")
    print("=" * 80)

    # Create matrix
    matrix, service = create_clean_air_act_matrix()

    # Create temporal clock
    clock = create_clean_air_temporal_clock(service)

    # Display summary
    summary = matrix.get_summary()

    print("\nMatrix Summary:")
    print(f"  Components: {summary['components']}")
    print(f"  Non-empty cells: {summary['non_empty_cells']}")
    print(f"  Total deliveries: {summary['total deliveries']}")
    print("\nDeliveries by type:")
    for dtype, count in summary['deliveries_by_type'].items():
        print(f"  {dtype}: {count}")

    print(f"\nCells with multiple deliveries: {summary['cells_with_multiple_deliveries']}")
    print(f"Quantified deliveries: {summary['quantified_deliveries']}")

    # Check thresholds (pollution monitoring)
    alerts = service.check_delivery_thresholds(matrix)
    if alerts:
        print(f"\nTHRESHOLD ALERTS: {len(alerts)}")
        for alert in alerts:
            print(f"  ⚠️  {alert.delivery.delivery_content}")
            print(f"     Current: {alert.current_value}, Target: {alert.threshold} {alert.delivery.units}")
    else:
        print("\n✓ All emissions below target thresholds (1970 baselines → 2010 achievements)")

    # Run SFM analysis battery
    print("\n" + "=" * 80)
    print("RUNNING SFM ANALYSIS BATTERY")
    print("=" * 80)
    report = run_analysis_battery(service)
    analysis_text = format_report(report)
    print(analysis_text)

    # Run criteria evaluation
    print("\n" + "=" * 80)
    print("CRITERIA EVALUATION REPORT")
    print("=" * 80)
    criteria_results = evaluate_against_criteria(service)
    evaluation_text = format_evaluation_report(criteria_results, include_details=True)
    print(evaluation_text)

    # Network centrality analysis
    print("\n" + "=" * 80)
    print("NETWORK CENTRALITY ANALYSIS")
    print("=" * 80)
    centrality = compute_centrality_metrics(matrix, service)
    print(format_centrality_report(centrality, title="Clean Air Act Regulatory Network Centrality"))

    brokers = identify_power_brokers(centrality)
    if brokers:
        print("\nCentral Regulatory Agencies (betweenness >= 0.10):")
        for label, score in brokers:
            print(f"  {label}: {score:.3f}")
    else:
        print("\nNo nodes exceed the 0.10 betweenness threshold.")

    # Export to XLSX
    output_path = Path(__file__).parent / "clean_air_act_1970.xlsx"
    export_delivery_matrix_to_xlsx(
        matrix,
        output_path,
        service,
        include_cell_descriptions=True,
        include_delivery_details=True
    )

    print(f"\nExported to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

    # Key findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS (VERIFIED DATA):")
    print("=" * 80)

    print("\n1. EMISSIONS REDUCTIONS (1970-2010):")
    print("   Source: Nature Communications s41467-023-43492-9")
    print("   • Transportation NOx: 5.2 → 2.2 kg/km²/day (57.7% reduction)")
    print("   • Energy sector SO2: 9.0 → 3.0 kg/km²/day (66.7% reduction)")
    print("   • Energy sector NOx: 2.5 → 1.5 kg/km²/day (40.0% reduction)")
    print("   • Industrial SO2: 5.6 → 0.6 kg/km²/day (89.3% reduction)")
    print("   • PM2.5: Reduced to 35.1% of 1970 levels (University of Chicago AQLI)")
    print("   • Combined six pollutants: 78% reduction 1970-2020 (EPA)")

    print("\n2. INSTITUTIONAL FRAMEWORK:")
    print("   • EPA created December 2, 1970 to implement Act")
    print("   • All 50 states had air pollution programs by 1970")
    print("   • CASAC created 1977 for independent scientific review")
    print("   • Cooperative federalism: EPA sets standards, states implement")

    print("\n3. TECHNOLOGY FORCING:")
    print("   • 90% auto emission reduction required by 1975")
    print("   • Catalytic converter adoption forced 1975 (EPA)")
    print("   • Three-way catalyst forced 1981")
    print("   • >90% particulate reduction from vehicles (cleaner engines, filters)")

    print("\n4. ENFORCEMENT:")
    print("   • Civil penalties up to $45,268 per noncompliant vehicle")
    print("   • 2024 enforcement: $13M+ in penalties (EPA actions)")
    print("   • Section 113 enforcement authority expanded 1970")

    print("\n5. TEMPORAL IMPLEMENTATION:")
    print("   Clock phases:")
    for phase in clock.phases:
        print(f"   • {phase.phase_name}: {phase.duration.days} days")

    print("\n6. ENVIRONMENTAL JUSTICE:")
    print("   • Disproportionate exposure in low-income/minority communities")
    print("   • Industrial facilities proximity to EJ communities documented")
    print("   Source: Nature Communications environmental justice analysis 1970-2010")

    print("\n" + "=" * 80)
    print("SOURCES:")
    print("=" * 80)
    print("1. EPA - Evolution of the Clean Air Act")
    print("   https://www.epa.gov/clean-air-act-overview/evolution-clean-air-act")
    print("\n2. Congressional Research Service - Clean Air Act Summary")
    print("   https://www.congress.gov/crs-product/RL30853")
    print("\n3. Nature Communications - Environmental Justice Analysis (1970-2010)")
    print("   https://www.nature.com/articles/s41467-023-43492-9")
    print("\n4. Resources for the Future - 50 Years of the Clean Air Act")
    print("   https://www.resources.org/archives/looking-back-50-years-clean-air-act-1970/")
    print("\n5. University of Chicago AQLI - Clean Air Act 1970")
    print("   https://aqli.epic.uchicago.edu/post/united-states-clean-air-act-1970")
    print("\n6. ScienceDirect - Impact on Particulate Matter in the 1970s")
    print("   https://www.sciencedirect.com/science/article/abs/pii/S0095069623000852")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
