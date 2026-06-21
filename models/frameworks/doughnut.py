"""
Doughnut Economics criteria factory for Social Fabric Matrix (SFM).

Implements Kate Raworth's Doughnut Economics framework (2017) as reusable
SFM criterion nodes. The Doughnut defines a safe and just space for humanity
bounded by:
- **Social foundation (12 dimensions)**: minimum standards for human well-being
- **Ecological ceiling (9 planetary boundaries)**: maximum stress on Earth systems

This module encodes all 21 Doughnut boundaries as SFMCriteria nodes, tagged
with polarity (shortfall/overshoot) to enable systematic evaluation of
deliveries against Doughnut principles.

## References
- Raworth, K. (2017). *Doughnut Economics: Seven Ways to Think Like a 21st-Century Economist*. Chelsea Green Publishing.
- Raworth, K. (2012). "A Safe and Just Space for Humanity: Can we live within the doughnut?" *Oxfam Discussion Paper*. Oxfam.
- Rockström, J., et al. (2009). "A safe operating space for humanity." *Nature*, 461(7263), 472-475.
- Steffen, W., et al. (2015). "Planetary boundaries: Guiding human development on a changing planet." *Science*, 347(6223), 1259855.

## Usage

```python
from models.frameworks.doughnut import build_doughnut_criteria

# Create all 21 Doughnut criteria
criteria = build_doughnut_criteria()

# Add to SFM service
for criterion in criteria:
    service.add_node(criterion)

# Filter by polarity
social_criteria = [c for c in criteria if c.meta.get("polarity") == "shortfall"]
ecological_criteria = [c for c in criteria if c.meta.get("polarity") == "overshoot"]
```
"""

from typing import List
from models.matrix_components import SFMCriteria
from models.enums import (
    CriteriaType,
    CriteriaPriority,
    MeasurementApproach,
)


def build_doughnut_criteria() -> List[SFMCriteria]:
    """
    Create all 21 Doughnut Economics criteria (12 social + 9 planetary).

    Returns list of SFMCriteria nodes configured per Raworth's framework.
    Each criterion is tagged with:
    - polarity: "shortfall" (social foundation) or "overshoot" (ecological ceiling)
    - doughnut_dimension: "social_foundation" or "ecological_ceiling"
    - source: "Raworth 2017"

    Factory is idempotent - multiple calls create distinct Node instances
    but with identical labels and configurations.

    Returns:
        List[SFMCriteria]: 21 criterion nodes (12 social, 9 ecological)
    """
    criteria: List[SFMCriteria] = []

    # SOCIAL FOUNDATION (12 dimensions) - polarity: "shortfall"
    # Below these thresholds indicates social deprivation

    criteria.append(SFMCriteria(
        label="Food",
        description="Access to sufficient, safe, and nutritious food to meet dietary needs (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        instrumental_capacity=0.95,
        normative_justification="Food security is fundamental to human dignity and life process continuity per Hayden's framework",
        evaluation_method="% population with adequate caloric and nutritional intake",
        data_requirements=["FAO food security indicators", "WHO nutritional surveys", "household consumption data"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "2",  # SDG 2: Zero Hunger
        },
    ))

    criteria.append(SFMCriteria(
        label="Health",
        description="Access to healthcare, sanitation, and freedom from preventable disease (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        instrumental_capacity=0.95,
        normative_justification="Health is prerequisite for full participation in life processes",
        evaluation_method="Life expectancy, mortality rates, healthcare access metrics",
        data_requirements=["WHO health statistics", "national health surveys", "morbidity/mortality data"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "3",  # SDG 3: Good Health and Well-Being
        },
    ))

    criteria.append(SFMCriteria(
        label="Education",
        description="Access to quality education and learning opportunities (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.95,
        instrumental_capacity=0.90,
        normative_justification="Education enables instrumental problem-solving and cultural development",
        evaluation_method="Literacy rates, school enrollment, educational attainment levels",
        data_requirements=["UNESCO education statistics", "national enrollment data", "literacy surveys"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "4",  # SDG 4: Quality Education
        },
    ))

    criteria.append(SFMCriteria(
        label="Income & Work",
        description="Access to decent work, fair wages, and adequate income (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.ECONOMIC,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.90,
        instrumental_capacity=0.85,
        normative_justification="Economic security enables participation in community and supports life processes",
        evaluation_method="Employment rates, income distribution, poverty metrics, wage adequacy",
        data_requirements=["ILO employment data", "national income surveys", "poverty line statistics"],
        measurement_frequency="quarterly",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "1, 8",  # SDG 1: No Poverty, SDG 8: Decent Work
        },
    ))

    criteria.append(SFMCriteria(
        label="Peace & Justice",
        description="Freedom from violence, crime, and access to fair legal systems (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.POLITICAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.95,
        instrumental_capacity=0.85,
        normative_justification="Security and justice are prerequisites for community continuity and life process flourishing",
        evaluation_method="Crime rates, conflict intensity, judicial access, human rights indicators",
        data_requirements=["UNODC crime statistics", "conflict data", "human rights reports"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "16",  # SDG 16: Peace, Justice and Strong Institutions
        },
    ))

    criteria.append(SFMCriteria(
        label="Political Voice",
        description="Freedom of expression, association, and participation in governance (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.POLITICAL,
        measurement_approach=MeasurementApproach.QUALITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.90,
        instrumental_capacity=0.85,
        normative_justification="Democratic participation enables instrumental institutional adaptation per Hayden",
        evaluation_method="Voter turnout, civil liberties indices, freedom of press metrics",
        data_requirements=["Freedom House indices", "Polity IV scores", "electoral participation data"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "16",  # SDG 16: Peace, Justice and Strong Institutions
        },
    ))

    criteria.append(SFMCriteria(
        label="Social Equity",
        description="Freedom from discrimination and access to equal opportunities (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.95,
        instrumental_capacity=0.80,
        normative_justification="Equity is central to Hayden's distributional value criterion in SFM",
        evaluation_method="Gini coefficient, wealth distribution, discrimination indices, access equality metrics",
        data_requirements=["World Bank inequality data", "discrimination surveys", "access gap statistics"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "5, 10",  # SDG 5: Gender Equality, SDG 10: Reduced Inequalities
        },
    ))

    criteria.append(SFMCriteria(
        label="Gender Equality",
        description="Equal rights, opportunities, and treatment regardless of gender (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.95,
        instrumental_capacity=0.85,
        normative_justification="Gender equity is prerequisite for full community participation in life processes",
        evaluation_method="Gender pay gap, educational access parity, political representation, violence rates",
        data_requirements=["UN Women statistics", "gender parity indices", "violence against women data"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "5",  # SDG 5: Gender Equality
        },
    ))

    criteria.append(SFMCriteria(
        label="Housing",
        description="Access to affordable, secure, and adequate shelter (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.90,
        instrumental_capacity=0.85,
        normative_justification="Secure housing is fundamental to community continuity and life process stability",
        evaluation_method="Homelessness rates, housing affordability ratios, overcrowding metrics, slum population",
        data_requirements=["UN-Habitat data", "national housing surveys", "affordability indices"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "11",  # SDG 11: Sustainable Cities and Communities
        },
    ))

    criteria.append(SFMCriteria(
        label="Networks",
        description="Access to information, communication, and social connections (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.SECONDARY,
        life_process_relevance=0.85,
        instrumental_capacity=0.80,
        normative_justification="Social networks enable community continuity and information flow per Hayden's framework",
        evaluation_method="Internet access, mobile connectivity, social capital indices, community participation",
        data_requirements=["ITU connectivity data", "social capital surveys", "digital divide metrics"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "9",  # SDG 9: Industry, Innovation and Infrastructure
        },
    ))

    criteria.append(SFMCriteria(
        label="Energy",
        description="Access to affordable, reliable, and modern energy services (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.90,
        instrumental_capacity=0.90,
        normative_justification="Energy access is prerequisite for modern life processes and instrumental capacity",
        evaluation_method="Electricity access rate, clean cooking fuel access, energy poverty metrics",
        data_requirements=["IEA energy statistics", "World Bank electrification data", "energy poverty surveys"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "7",  # SDG 7: Affordable and Clean Energy
        },
    ))

    criteria.append(SFMCriteria(
        label="Water",
        description="Access to safe drinking water and adequate sanitation (Raworth 2017, Social Foundation)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        instrumental_capacity=0.95,
        normative_justification="Water security is fundamental to life processes and human dignity",
        evaluation_method="Access to improved water sources, sanitation coverage, water stress indices",
        data_requirements=["WHO/UNICEF JMP data", "national water surveys", "sanitation coverage statistics"],
        measurement_frequency="annual",
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Raworth 2017",
            "related_sdgs": "6",  # SDG 6: Clean Water and Sanitation
        },
    ))

    # ECOLOGICAL CEILING (9 planetary boundaries) - polarity: "overshoot"
    # Above these thresholds indicates ecological overshoot

    criteria.append(SFMCriteria(
        label="Climate Change",
        description="CO2 atmospheric concentration and energy imbalance (Rockström et al. 2009, Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        instrumental_capacity=0.90,
        ceremonial_bias_risk=0.70,  # High ceremonial resistance to climate action
        normative_justification="Climate stability is prerequisite for long-term life process continuity globally",
        evaluation_method="Atmospheric CO2 ppm (threshold: 350), radiative forcing (threshold: +1 W/m²)",
        data_requirements=["NOAA Mauna Loa CO2 data", "IPCC climate reports", "global temperature records"],
        measurement_frequency="continuous",
        responsible_party="UNFCCC, IPCC",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Rockström et al. 2009, Steffen et al. 2015",
            "planetary_boundary": "350 ppm CO2 (current ~420 ppm - EXCEEDED)",
            "related_sdgs": "13",  # SDG 13: Climate Action
        },
    ))

    criteria.append(SFMCriteria(
        label="Ocean Acidification",
        description="Carbonate ion concentration in seawater (Rockström et al. 2009, Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.95,
        instrumental_capacity=0.85,
        normative_justification="Ocean chemistry stability maintains marine ecosystems critical to global life processes",
        evaluation_method="Aragonite saturation state (threshold: ≥80% of pre-industrial)",
        data_requirements=["NOAA ocean chemistry monitoring", "pH measurements", "carbonate saturation data"],
        measurement_frequency="continuous",
        responsible_party="NOAA, IOC-UNESCO",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Rockström et al. 2009, Steffen et al. 2015",
            "planetary_boundary": "Aragonite ≥80% pre-industrial (current 84% - within boundary)",
            "related_sdgs": "14",  # SDG 14: Life Below Water
        },
    ))

    criteria.append(SFMCriteria(
        label="Chemical Pollution",
        description="Novel entities (synthetic chemicals, plastics, radioactive materials) in environment (Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUALITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.90,
        instrumental_capacity=0.75,  # Difficult to measure comprehensively
        normative_justification="Chemical safety protects life processes from persistent toxic disruption",
        evaluation_method="Concentration of novel entities, plastic pollution, endocrine disruptors, PFAS (boundary not yet quantified)",
        data_requirements=["Chemical monitoring networks", "plastic pollution surveys", "toxicology databases"],
        measurement_frequency="annual",
        responsible_party="UNEP, national environmental agencies",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Steffen et al. 2015",
            "planetary_boundary": "Not yet quantified - likely EXCEEDED",
            "related_sdgs": "12",  # SDG 12: Responsible Consumption and Production
        },
    ))

    criteria.append(SFMCriteria(
        label="Nitrogen & Phosphorus Loading",
        description="Industrial and agricultural fixation of nitrogen and phosphorus (Rockström et al. 2009, Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.90,
        instrumental_capacity=0.85,
        normative_justification="Nutrient cycle integrity is instrumental for maintaining agricultural capacity and preventing ecosystem collapse that would disrupt life processes",
        evaluation_method="N: industrial + biological fixation (threshold: 62 Tg N/yr), P: flow to oceans (threshold: 6.2 Tg P/yr)",
        data_requirements=["FAO fertilizer data", "biogeochemical models", "nutrient runoff measurements"],
        measurement_frequency="annual",
        responsible_party="FAO, UNEP",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Rockström et al. 2009, Steffen et al. 2015",
            "planetary_boundary": "N: 62 Tg/yr (current ~150 Tg/yr - EXCEEDED), P: 6.2 Tg/yr (current ~8 Tg/yr - EXCEEDED)",
            "related_sdgs": "2, 14, 15",  # SDG 2: Zero Hunger, SDG 14/15: Aquatic/Terrestrial Life
        },
    ))

    criteria.append(SFMCriteria(
        label="Freshwater Withdrawals",
        description="Global freshwater use (Rockström et al. 2009, Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.95,
        instrumental_capacity=0.90,
        normative_justification="Freshwater availability sustains life processes and agricultural systems globally",
        evaluation_method="Blue water consumption (threshold: 4,000 km³/yr)",
        data_requirements=["FAO AQUASTAT", "national water use statistics", "hydrological models"],
        measurement_frequency="annual",
        responsible_party="FAO, World Water Council",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Rockström et al. 2009, Steffen et al. 2015",
            "planetary_boundary": "4,000 km³/yr (current ~2,600 km³/yr - within boundary globally, exceeded regionally)",
            "related_sdgs": "6",  # SDG 6: Clean Water and Sanitation
        },
    ))

    criteria.append(SFMCriteria(
        label="Land-System Change",
        description="Conversion of natural ecosystems to agricultural or urban use (Rockström et al. 2009, Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.90,
        instrumental_capacity=0.85,
        normative_justification="Land integrity maintains ecosystem services and biodiversity essential to life processes",
        evaluation_method="Forest cover as % of original (threshold: 75%), cropland area",
        data_requirements=["FAO land use data", "satellite imagery", "forest cover monitoring"],
        measurement_frequency="annual",
        responsible_party="FAO, UNEP",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Rockström et al. 2009, Steffen et al. 2015",
            "planetary_boundary": "75% forest cover remaining (current ~62% - EXCEEDED)",
            "related_sdgs": "15",  # SDG 15: Life on Land
        },
    ))

    criteria.append(SFMCriteria(
        label="Biodiversity Loss",
        description="Extinction rate and genetic diversity loss (Rockström et al. 2009, Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=0.95,
        instrumental_capacity=0.85,
        normative_justification="Biodiversity underpins ecosystem resilience and evolutionary capacity of life processes",
        evaluation_method="Extinctions per million species-years (threshold: <10), Biodiversity Intactness Index (threshold: 90%)",
        data_requirements=["IUCN Red List", "Living Planet Index", "national biodiversity assessments"],
        measurement_frequency="annual",
        responsible_party="IUCN, CBD, UNEP",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Rockström et al. 2009, Steffen et al. 2015",
            "planetary_boundary": "<10 extinctions/MSY (current >100 E/MSY - EXCEEDED), BII 90% (current ~84% - EXCEEDED)",
            "related_sdgs": "14, 15",  # SDG 14: Life Below Water, SDG 15: Life on Land
        },
    ))

    criteria.append(SFMCriteria(
        label="Air Pollution",
        description="Atmospheric aerosol loading affecting monsoon systems and regional climate (Rockström et al. 2009, Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.SECONDARY,
        life_process_relevance=0.85,
        instrumental_capacity=0.80,
        normative_justification="Air quality is instrumental for protecting human health and maintaining regional climate stability that supports life processes",
        evaluation_method="Aerosol optical depth (AOD), particulate matter PM2.5 concentration (boundary not fully quantified)",
        data_requirements=["NASA MODIS AOD data", "WHO air quality database", "national monitoring networks"],
        measurement_frequency="continuous",
        responsible_party="WHO, WMO, national environmental agencies",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Rockström et al. 2009, Steffen et al. 2015",
            "planetary_boundary": "Regional boundaries, not globally quantified - likely EXCEEDED in South Asia",
            "related_sdgs": "3, 11",  # SDG 3: Good Health, SDG 11: Sustainable Cities
        },
    ))

    criteria.append(SFMCriteria(
        label="Ozone Depletion",
        description="Stratospheric ozone concentration (Rockström et al. 2009, Steffen et al. 2015)",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.SECONDARY,
        life_process_relevance=0.90,
        instrumental_capacity=0.95,  # Successfully addressed via Montreal Protocol
        normative_justification="Ozone layer protects terrestrial life processes from harmful UV radiation",
        evaluation_method="Stratospheric O3 concentration (threshold: <5% reduction from 1964-1980 baseline, ~276 DU)",
        data_requirements=["NASA Ozone Watch", "WMO ozone assessments", "satellite monitoring"],
        measurement_frequency="continuous",
        responsible_party="WMO, UNEP Ozone Secretariat",
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Rockström et al. 2009, Steffen et al. 2015",
            "planetary_boundary": "<5% reduction (currently within boundary thanks to Montreal Protocol - RECOVERING)",
            "related_sdgs": "13",  # SDG 13: Climate Action
        },
    ))

    return criteria
