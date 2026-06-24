#!/usr/bin/env python3
"""
Generate synthetic institutional analysis dataset for SFM-Core.

This script creates a realistic network representing the National Climate Policy
ecosystem (2025-2035) with 1000+ nodes and 3000+ relationships.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
# import sys  # unused


class ClimateNetworkGenerator:
    """Generate a synthetic institutional network for climate policy analysis."""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.nodes = []
        self.relationships = []
        self.node_lookup = {}  # name -> node_id mapping

    def generate_id(self) -> str:
        """Generate a unique identifier."""
        return str(uuid.uuid4())

    def random_date(self, start_year: int = 2025, end_year: int = 2035) -> str:
        """Generate random date between start and end years."""
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        delta = end - start
        random_days = random.randint(0, delta.days)
        return (start + timedelta(days=random_days)).isoformat()

    def ceremonial_instrumental_scores(self) -> Tuple[float, float]:
        """
        Generate correlated ceremonial/instrumental scores.
        More ceremonial -> less instrumental (negative correlation).
        """
        ceremonial = random.uniform(0.1, 0.9)
        # Instrumental tends to be inverse with some noise
        instrumental = random.gauss(1.0 - ceremonial, 0.15)
        instrumental = max(0.1, min(0.9, instrumental))
        return round(ceremonial, 3), round(instrumental, 3)

    def create_node(
        self,
        name: str,
        node_type: str,
        category: str,
        description: str = "",
        geographic_scope: str = "national",
        **kwargs
    ) -> Dict:
        """Create a node with standard metadata."""
        node_id = self.generate_id()
        ceremonial, instrumental = self.ceremonial_instrumental_scores()

        node = {
            "id": node_id,
            "name": name,
            "type": node_type,
            "category": category,
            "description": description,
            "metadata": {
                "ceremonial_score": ceremonial,
                "instrumental_score": instrumental,
                "geographic_scope": geographic_scope,
                "created": datetime.now().isoformat(),
                "valid_from": self.random_date(2025, 2027),
                "valid_to": self.random_date(2030, 2035),
                **kwargs
            }
        }

        self.nodes.append(node)
        self.node_lookup[name] = node_id
        return node

    def create_relationship(
        self,
        source_name: str,
        target_name: str,
        relationship_type: str,
        delivery_type: str,
        strength: float = None,
        description: str = "",
        **kwargs
    ) -> Dict:
        """Create a relationship between nodes."""
        if source_name not in self.node_lookup or target_name not in self.node_lookup:
            return None

        if strength is None:
            strength = random.uniform(0.3, 0.9)

        confidence = random.uniform(0.7, 0.95)

        rel = {
            "id": self.generate_id(),
            "source": self.node_lookup[source_name],
            "target": self.node_lookup[target_name],
            "type": relationship_type,
            "delivery_type": delivery_type,
            "strength": round(strength, 3),
            "description": description,
            "metadata": {
                "confidence": round(confidence, 3),
                "established": self.random_date(2025, 2028),
                "last_updated": datetime.now().isoformat(),
                **kwargs
            }
        }

        self.relationships.append(rel)
        return rel

    def generate_federal_agencies(self) -> List[str]:
        """Generate federal government agencies."""
        agencies = [
            ("Environmental Protection Agency", "Primary environmental regulator"),
            ("Department of Energy", "Energy policy and research"),
            ("Department of Interior", "Natural resources management"),
            ("National Oceanic and Atmospheric Administration", "Climate science and monitoring"),
            ("Department of Transportation", "Transportation emissions policy"),
            ("Department of Agriculture", "Agricultural climate policy"),
            ("Federal Energy Regulatory Commission", "Energy market regulation"),
            ("National Science Foundation", "Climate research funding"),
            ("Department of Commerce", "Economic climate policy"),
            ("Council on Environmental Quality", "Executive environmental coordination"),
            ("Office of Science and Technology Policy", "Federal science coordination"),
            ("Department of Treasury", "Climate finance policy"),
            ("Securities and Exchange Commission", "Climate disclosure regulation"),
            ("Department of State", "International climate diplomacy"),
            ("Agency for International Development", "International climate assistance"),
        ]

        names = []
        for name, desc in agencies:
            self.create_node(
                name=name,
                node_type="institution",
                category="federal_agency",
                description=desc,
                geographic_scope="national",
                authority_level="federal",
                budget_category="large" if random.random() > 0.3 else "medium"
            )
            names.append(name)

        return names

    def generate_state_agencies(self) -> List[str]:
        """Generate state-level agencies."""
        states = [
            "California", "New York", "Texas", "Florida", "Illinois",
            "Pennsylvania", "Ohio", "Georgia", "North Carolina", "Michigan",
            "New Jersey", "Virginia", "Washington", "Massachusetts", "Arizona",
            "Minnesota", "Colorado", "Wisconsin", "Oregon", "Maryland"
        ]

        names = []
        for state in states:
            # State environmental agency
            name = f"{state} Department of Environmental Quality"
            self.create_node(
                name=name,
                node_type="institution",
                category="state_agency",
                description=f"State environmental regulation for {state}",
                geographic_scope="state",
                state=state,
                authority_level="state"
            )
            names.append(name)

            # State energy office (for ~half of states)
            if random.random() > 0.5:
                name = f"{state} Energy Office"
                self.create_node(
                    name=name,
                    node_type="institution",
                    category="state_agency",
                    description=f"State energy policy for {state}",
                    geographic_scope="state",
                    state=state,
                    authority_level="state"
                )
                names.append(name)

        return names

    def generate_municipalities(self) -> List[str]:
        """Generate municipal governments."""
        cities = [
            "New York City", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
            "Austin", "Seattle", "Denver", "Boston", "Portland",
            "Atlanta", "Miami", "Minneapolis", "Detroit", "San Francisco",
            "Pittsburgh", "Charlotte", "Baltimore", "Milwaukee", "Columbus"
        ]

        names = []
        for city in cities:
            name = f"{city} Office of Sustainability"
            self.create_node(
                name=name,
                node_type="institution",
                category="municipal_agency",
                description=f"Municipal climate action for {city}",
                geographic_scope="local",
                municipality=city,
                authority_level="local"
            )
            names.append(name)

        return names

    def generate_private_corporations(self) -> List[str]:
        """Generate private sector entities."""

        # Utilities (expanded)
        utilities = [
            "Pacific Gas & Electric", "Duke Energy", "Southern Company",
            "Exelon Corporation", "NextEra Energy", "American Electric Power",
            "Dominion Energy", "Xcel Energy", "Consolidated Edison",
            "Public Service Enterprise Group", "WEC Energy Group",
            "CenterPoint Energy", "Sempra Energy", "Entergy Corporation",
            "Eversource Energy", "NRG Energy", "PPL Corporation",
            "Ameren Corporation", "Alliant Energy", "Avangrid",
            "Portland General Electric", "NorthWestern Energy",
            "Black Hills Energy", "Otter Tail Power", "IDACORP",
            "Hawaiian Electric", "OGE Energy", "Pinnacle West",
            "El Paso Electric", "Unitil Corporation"
        ]

        # Climate tech companies (expanded)
        climate_tech = [
            "Tesla Energy", "Sunrun Solar", "First Solar", "Enphase Energy",
            "ChargePoint Holdings", "Bloom Energy", "QuantumScape",
            "Carbon Engineering", "Climeworks", "LanzaTech",
            "Breakthrough Energy", "Commonwealth Fusion Systems",
            "Form Energy", "Gravity Energy Storage", "Heliogen",
            "Redwood Materials", "Lilac Solutions", "Turntide Technologies",
            "Sila Nanotechnologies", "ESS Tech", "Eavor Technologies",
            "Voltus Energy", "Stem Inc", "Fluence Energy",
            "Energy Vault", "Hydrogenious LOHC", "Twelve",
            "Opus 12", "Solidia Technologies", "CarbonCure",
            "Antora Energy", "Malta Inc", "Quidnet Energy",
            "Baseload Capital", "Greenfire Energy", "Fervo Energy",
            "Sage Geosystems", "Dandelion Energy", "BlocPower",
            "Sealed", "Rewiring America", "Amply Power",
            "Fermata Energy", "Nuvve Corporation", "Electric Hydrogen",
            "ZeroAvia", "Universal Hydrogen", "H2Pro",
            "Electra", "Boston Metal", "Sublime Systems",
            "CarbonBuilt", "Brimstone Energy", "Rondo Energy"
        ]

        # Oil & gas (transitioning)
        oil_gas = [
            "ExxonMobil Clean Energy", "Chevron New Energies",
            "BP Alternative Energy", "Shell Renewables", "ConocoPhillips Sustainability",
            "Occidental Low Carbon Ventures", "TotalEnergies Renewables",
            "Equinor New Energy", "Repsol Renewables", "Eni Green Energy",
            "Marathon Climate Solutions", "Phillips 66 Renewables"
        ]

        # Financial institutions (expanded)
        financial = [
            "BlackRock Sustainable Investing", "Vanguard ESG",
            "State Street Climate Solutions", "Goldman Sachs Clean Energy",
            "Morgan Stanley Sustainable Finance", "Bank of America Climate Transition",
            "Citi Sustainable Finance", "JPMorgan Climate Finance",
            "Wells Fargo Environmental Finance", "HSBC Climate Solutions",
            "Barclays Green Banking", "Credit Suisse ESG",
            "UBS Climate Investing", "Deutsche Bank Climate Finance",
            "BNP Paribas Energy Transition", "Societe Generale Sustainable Finance",
            "ING Climate Finance", "Santander Green Finance",
            "Standard Chartered Sustainable Finance", "Macquarie Green Investment"
        ]

        # Tech companies (expanded)
        tech = [
            "Google Sustainability", "Microsoft Climate Innovation",
            "Apple Environmental Programs", "Amazon Climate Pledge",
            "Meta Sustainability", "IBM Climate Solutions",
            "Intel Environmental Sustainability", "Oracle Cloud Sustainability",
            "Salesforce Net Zero Cloud", "SAP Climate 21",
            "Adobe Sustainability", "Cisco Environmental Sustainability",
            "Dell Technologies Sustainability", "HP Sustainable Impact",
            "Lenovo Climate Action", "VMware Sustainability"
        ]

        # Manufacturing (new category)
        manufacturing = [
            "General Electric Renewables", "Siemens Energy",
            "Vestas Wind Systems", "Orsted North America",
            "Schneider Electric Sustainability", "ABB Electrification",
            "Eaton Power Management", "Emerson Automation Solutions",
            "Honeywell Building Technologies", "Johnson Controls OpenBlue",
            "Carrier Global Sustainability", "Trane Technologies Climate Solutions"
        ]

        # Transportation (new category)
        transportation = [
            "Rivian", "Lucid Motors", "Proterra Electric Buses",
            "Lion Electric", "Arrival Automotive", "Canoo",
            "Nikola Motor", "Hyzon Motors", "Workhorse Group",
            "XOS Trucks", "Lightning eMotors", "BYD North America"
        ]

        names = []

        for name in utilities:
            self.create_node(
                name=name,
                node_type="institution",
                category="private_utility",
                description="Electric utility company",
                geographic_scope="regional",
                sector="utilities",
                ownership="public_traded"
            )
            names.append(name)

        for name in climate_tech:
            self.create_node(
                name=name,
                node_type="institution",
                category="climate_tech",
                description="Climate technology company",
                geographic_scope="national",
                sector="clean_technology",
                ownership="public_traded" if random.random() > 0.4 else "private"
            )
            names.append(name)

        for name in oil_gas:
            self.create_node(
                name=name,
                node_type="institution",
                category="energy_transition",
                description="Energy company transitioning to clean energy",
                geographic_scope="national",
                sector="energy",
                ownership="public_traded"
            )
            names.append(name)

        for name in financial:
            self.create_node(
                name=name,
                node_type="institution",
                category="financial_services",
                description="Financial institution climate division",
                geographic_scope="national",
                sector="finance",
                ownership="public_traded"
            )
            names.append(name)

        for name in tech:
            self.create_node(
                name=name,
                node_type="institution",
                category="technology",
                description="Technology company climate program",
                geographic_scope="national",
                sector="technology",
                ownership="public_traded"
            )
            names.append(name)

        for name in manufacturing:
            self.create_node(
                name=name,
                node_type="institution",
                category="manufacturing",
                description="Industrial equipment manufacturer",
                geographic_scope="national",
                sector="manufacturing",
                ownership="public_traded"
            )
            names.append(name)

        for name in transportation:
            self.create_node(
                name=name,
                node_type="institution",
                category="transportation",
                description="Electric vehicle manufacturer",
                geographic_scope="national",
                sector="transportation",
                ownership="public_traded" if random.random() > 0.3 else "private"
            )
            names.append(name)

        return names

    def generate_nonprofits(self) -> List[str]:
        """Generate non-profit organizations."""

        ngos = [
            ("Natural Resources Defense Council", "Environmental advocacy"),
            ("Sierra Club", "Grassroots environmental organization"),
            ("Environmental Defense Fund", "Market-based environmental solutions"),
            ("The Nature Conservancy", "Conservation organization"),
            ("World Wildlife Fund US", "Wildlife and habitat conservation"),
            ("Union of Concerned Scientists", "Science-based advocacy"),
            ("Climate Action Network US", "Climate policy coalition"),
            ("Citizens Climate Lobby", "Grassroots climate advocacy"),
            ("350.org", "Climate activism network"),
            ("Sunrise Movement", "Youth climate movement"),
            ("Climate Reality Project", "Climate education and advocacy"),
            ("Ceres", "Sustainability business network"),
            ("Rocky Mountain Institute", "Clean energy transition research"),
            ("World Resources Institute", "Environmental research"),
            ("Resources for the Future", "Environmental economics research"),
            ("American Council for an Energy-Efficient Economy", "Energy efficiency advocacy"),
            ("Clean Air Task Force", "Climate and air quality advocacy"),
            ("Carbon Tracker Initiative", "Financial climate risk analysis"),
            ("Climate Central", "Climate science communication"),
            ("Alliance for Climate Protection", "Climate policy advocacy"),
            ("Earthjustice", "Environmental law organization"),
            ("Ocean Conservancy", "Ocean protection advocacy"),
            ("Rainforest Alliance", "Forest conservation"),
            ("Conservation International", "Biodiversity protection"),
            ("Greenpeace USA", "Direct action environmental advocacy"),
            ("Friends of the Earth", "Grassroots environmental network"),
            ("National Wildlife Federation", "Wildlife conservation"),
            ("Audubon Society", "Bird and habitat conservation"),
            ("Defenders of Wildlife", "Endangered species protection"),
            ("Wilderness Society", "Public lands protection"),
            ("Trust for Public Land", "Land conservation"),
            ("American Rivers", "River conservation"),
            ("Oceana", "Ocean conservation"),
            ("Coral Reef Alliance", "Coral reef protection"),
            ("Environmental Working Group", "Research and advocacy"),
            ("League of Conservation Voters", "Political advocacy"),
            ("National Parks Conservation Association", "Parks protection"),
            ("Land Trust Alliance", "Land conservation support"),
            ("Nature Conservancy Canada", "International conservation"),
            ("Conservation Fund", "Conservation finance"),
            ("Sustainable Agriculture Coalition", "Agricultural sustainability"),
            ("National Sustainable Agriculture Coalition", "Farm policy"),
            ("Food Policy Action", "Food system advocacy"),
            ("Center for Food Safety", "Food safety and sustainability"),
            ("Institute for Agriculture and Trade Policy", "Agricultural policy research"),
            ("National Young Farmers Coalition", "Young farmer advocacy"),
            ("Climate Justice Alliance", "Climate justice organizing"),
            ("Indigenous Environmental Network", "Indigenous rights and environment"),
            ("WE ACT for Environmental Justice", "Environmental justice advocacy"),
            ("Green for All", "Green economy and justice"),
            ("Greentech Alliance", "Clean technology promotion"),
            ("Advanced Energy Economy", "Clean energy business advocacy"),
            ("Clean Energy Group", "Clean energy equity"),
            ("Vote Solar", "Solar energy advocacy"),
            ("Solar Energy Industries Association Foundation", "Solar industry support"),
            ("American Wind Energy Association Foundation", "Wind industry support"),
            ("Geothermal Resources Council", "Geothermal promotion"),
            ("Biomass Power Association", "Biomass energy advocacy"),
            ("National Hydropower Association", "Hydropower advocacy"),
            ("Energy Storage Association", "Energy storage promotion"),
            ("Plug In America", "Electric vehicle advocacy"),
            ("Electric Auto Association", "EV education and advocacy"),
            ("Electrification Coalition", "Transportation electrification"),
            ("Atlas Public Policy", "EV policy research"),
            ("Coltura", "Gasoline reduction advocacy"),
            ("Safe Climate Transport Campaign", "Transport decarbonization"),
            ("Transportation and Climate Initiative", "Regional transport policy"),
            ("Rails-to-Trails Conservancy", "Trail and active transport"),
            ("National Association of City Transportation Officials", "Urban transport"),
            ("Institute for Transportation and Development Policy", "Sustainable transport"),
            ("Smart Growth America", "Land use and transport"),
            ("Congress for the New Urbanism", "Urban planning"),
            ("Urban Land Institute Sustainability", "Sustainable development"),
            ("US Green Building Council", "Green building advocacy"),
            ("Architecture 2030", "Building decarbonization"),
            ("New Buildings Institute", "Building efficiency"),
            ("Building Decarbonization Coalition", "Building electrification"),
            ("Passive House Alliance US", "Energy-efficient building"),
            ("American Institute of Architects Climate Action", "Architecture sustainability")
        ]

        names = []
        for name, desc in ngos:
            self.create_node(
                name=name,
                node_type="institution",
                category="nonprofit",
                description=desc,
                geographic_scope="national",
                sector="nonprofit",
                tax_status="501c3"
            )
            names.append(name)

        return names

    def generate_research_institutions(self) -> List[str]:
        """Generate research institutions and universities."""

        institutions = [
            "MIT Climate Lab", "Stanford Woods Institute",
            "Yale Climate Connections", "Harvard Environmental Economics",
            "UC Berkeley Energy Institute", "Carnegie Climate Program",
            "Columbia Climate School", "Princeton Climate Futures",
            "Duke Climate Policy Lab", "Cornell Climate Research",
            "University of Michigan Climate Center",
            "Lawrence Berkeley National Laboratory",
            "National Renewable Energy Laboratory",
            "Argonne National Laboratory", "Oak Ridge Climate Research",
            "Pacific Northwest National Laboratory",
            "Sandia National Laboratories", "Los Alamos Climate Research",
            "Idaho National Laboratory", "Brookhaven National Laboratory",
            "Fermi National Laboratory", "SLAC National Accelerator Laboratory",
            "Ames Laboratory", "Thomas Jefferson National Laboratory",
            "University of California Climate Center",
            "UCLA Institute of the Environment",
            "UC San Diego Scripps Institution",
            "UC Davis Policy Institute",
            "UC Irvine Climate Research",
            "Caltech Environmental Science",
            "University of Washington Climate Impacts",
            "University of Colorado Climate Research",
            "Georgia Tech Climate",
            "University of Texas Energy Institute",
            "Arizona State University Climate",
            "University of Arizona Climate Science",
            "Penn State Earth Systems",
            "Ohio State Climate Research",
            "University of Wisconsin Climate",
            "University of Minnesota Climate",
            "University of Illinois Climate",
            "Northwestern Climate",
            "University of Chicago Climate",
            "Rutgers Climate Institute",
            "University of Maryland Climate",
            "Virginia Tech Climate",
            "North Carolina State Climate",
            "University of Florida Climate",
            "University of Miami Climate",
            "Emory University Climate",
            "Vanderbilt Climate",
            "Rice University Climate",
            "University of Oregon Climate",
            "Oregon State Climate",
            "Boston University Climate",
            "Tufts Climate",
            "Brown University Climate",
            "Dartmouth Climate",
            "University of Vermont Climate",
            "Carnegie Mellon Climate",
            "Case Western Climate",
            "University of Pittsburgh Climate",
            "Iowa State University Climate",
            "Kansas State Climate",
            "University of Nebraska Climate",
            "University of Oklahoma Climate",
            "Colorado State University Climate",
            "University of Wyoming Climate",
            "Montana State Climate",
            "University of Alaska Climate",
            "University of Hawaii Climate"
        ]

        names = []
        for name in institutions:
            self.create_node(
                name=name,
                node_type="institution",
                category="research_institution",
                description="Climate research and education",
                geographic_scope="national",
                sector="education",
                institution_type="university" if "University" in name or "MIT" in name or "Stanford" in name else "national_lab"
            )
            names.append(name)

        return names

    def generate_policy_instruments(self) -> List[str]:
        """Generate policy instruments and regulations."""

        policies = [
            ("Clean Air Act", "Federal air quality regulation", "federal"),
            ("Clean Power Plan", "Power sector emissions regulation", "federal"),
            ("Renewable Portfolio Standards", "State renewable energy mandates", "state"),
            ("Carbon Pricing Mechanisms", "Market-based emissions reduction", "state"),
            ("Clean Energy Standards", "Clean electricity requirements", "state"),
            ("Vehicle Emission Standards", "Transportation emissions limits", "federal"),
            ("Building Energy Codes", "Energy efficiency requirements", "local"),
            ("Green Building Standards", "Sustainable construction requirements", "local"),
            ("Climate Action Plans", "Municipal climate strategies", "local"),
            ("Renewable Energy Tax Credits", "Clean energy incentives", "federal"),
            ("Energy Efficiency Programs", "Utility efficiency mandates", "state"),
            ("Net Metering Policies", "Distributed generation compensation", "state"),
            ("Electric Vehicle Incentives", "EV purchase subsidies", "federal"),
            ("Carbon Capture Tax Credits", "CCS deployment incentives", "federal"),
            ("Climate Disclosure Rules", "Corporate climate reporting", "federal"),
            ("Environmental Impact Assessments", "Project review requirements", "federal"),
            ("Endangered Species Protections", "Biodiversity conservation", "federal"),
            ("Water Quality Standards", "Water pollution limits", "federal"),
            ("Waste Management Regulations", "Solid waste rules", "state"),
            ("Land Use Planning Requirements", "Development controls", "local"),
            ("Public Transit Funding Programs", "Transit infrastructure support", "federal"),
            ("Green Infrastructure Mandates", "Nature-based solutions requirements", "local"),
            ("Climate Adaptation Plans", "Resilience planning requirements", "state"),
            ("Flood Risk Management Standards", "Flood protection requirements", "federal"),
            ("Coastal Zone Management Programs", "Coastal protection policies", "state"),
            ("Energy Modernization Act", "Grid infrastructure modernization", "federal"),
            ("Production Tax Credits Wind", "Wind energy incentives", "federal"),
            ("Investment Tax Credits Solar", "Solar investment incentives", "federal"),
            ("Advanced Manufacturing Tax Credits", "Clean tech manufacturing", "federal"),
            ("Green Bank Programs", "Clean energy financing", "state"),
            ("Feed-in Tariffs", "Renewable energy pricing", "state"),
            ("Community Choice Aggregation", "Municipal energy procurement", "local"),
            ("Property Assessed Clean Energy", "Building efficiency financing", "local"),
            ("Zero Emission Vehicle Mandates", "EV sales requirements", "state"),
            ("Low Carbon Fuel Standards", "Transportation fuel standards", "state"),
            ("Clean Truck Rules", "Heavy vehicle emissions standards", "state"),
            ("Port Electrification Programs", "Maritime emissions reduction", "local"),
            ("Airport Emissions Standards", "Aviation climate policy", "local"),
            ("Methane Emission Regulations", "Natural gas methane rules", "federal"),
            ("Appliance Efficiency Standards", "Equipment efficiency requirements", "federal"),
            ("Lighting Efficiency Standards", "Lighting performance requirements", "federal"),
            ("HVAC Efficiency Requirements", "Heating and cooling standards", "state"),
            ("Window Performance Standards", "Building envelope requirements", "state"),
            ("Cool Roof Requirements", "Reflective roofing mandates", "local"),
            ("Solar Ready Requirements", "Solar preparation mandates", "local"),
            ("EV Ready Building Codes", "EV charging infrastructure prep", "local"),
            ("Grid Interconnection Standards", "Distributed generation connection", "state"),
            ("Energy Storage Mandates", "Battery storage requirements", "state"),
            ("Demand Response Programs", "Load management initiatives", "state"),
            ("Time-of-Use Rates", "Dynamic electricity pricing", "state"),
            ("Renewable Energy Zones", "Transmission planning areas", "state"),
            ("Environmental Justice Policies", "Equity in environmental policy", "federal"),
            ("Climate Equity Programs", "Just transition support", "state"),
            ("Workforce Development Programs", "Green jobs training", "federal"),
            ("Disadvantaged Community Investment", "Environmental justice funding", "state"),
            ("Tribal Climate Programs", "Indigenous climate support", "federal"),
            ("Agricultural Climate Programs", "Farm carbon sequestration", "federal"),
            ("Forest Carbon Programs", "Forestry carbon credits", "federal"),
            ("Wetlands Protection Programs", "Wetland conservation", "federal"),
            ("Soil Health Programs", "Agricultural soil carbon", "state"),
            ("Cover Crop Programs", "Agricultural climate practice", "state"),
            ("Grazing Management Programs", "Rangeland carbon management", "federal"),
            ("Conservation Reserve Programs", "Land conservation payments", "federal"),
            ("Reforestation Programs", "Forest restoration support", "state"),
            ("Urban Forestry Programs", "City tree planting", "local"),
            ("Heat Island Mitigation Programs", "Urban cooling initiatives", "local"),
            ("Stormwater Management Requirements", "Green infrastructure standards", "local"),
            ("Wetland Banking Programs", "Wetland mitigation markets", "state"),
            ("Biodiversity Offset Programs", "Habitat compensation", "state"),
            ("Marine Protected Areas", "Ocean conservation zones", "federal"),
            ("Fisheries Management Plans", "Sustainable fishing regulations", "federal"),
            ("Ocean Acidification Programs", "Marine ecosystem protection", "federal"),
            ("Coastal Resilience Programs", "Shoreline adaptation support", "state"),
            ("Sea Level Rise Adaptation Plans", "Coastal planning requirements", "local"),
            ("Wildfire Risk Reduction Programs", "Fire management policy", "state"),
            ("Drought Management Plans", "Water scarcity policy", "state"),
            ("Water Conservation Programs", "Water efficiency requirements", "local"),
            ("Recycled Water Programs", "Water reuse initiatives", "local"),
            ("Stormwater Capture Programs", "Urban water harvesting", "local"),
            ("Greywater Regulations", "Alternative water use rules", "state"),
            ("Rainwater Harvesting Incentives", "Water collection support", "local")
        ]

        names = []
        for name, desc, scope in policies:
            self.create_node(
                name=name,
                node_type="policy_instrument",
                category="regulation" if "Standard" in name or "Rule" in name else "program",
                description=desc,
                geographic_scope=scope,
                enforcement_level=scope,
                instrument_type="regulatory" if random.random() > 0.4 else "economic"
            )
            names.append(name)

        return names

    def generate_value_systems(self) -> List[str]:
        """Generate value systems and frameworks."""

        values = [
            ("Environmental Justice", "Equitable environmental protection"),
            ("Climate Justice", "Fair climate action"),
            ("Intergenerational Equity", "Future generations consideration"),
            ("Precautionary Principle", "Preventive environmental action"),
            ("Polluter Pays Principle", "Pollution cost internalization"),
            ("Sustainable Development", "Economic-environmental balance"),
            ("Green Growth", "Economic growth with sustainability"),
            ("Degrowth Economics", "Ecological economics framework"),
            ("Circular Economy", "Resource循环 utilization"),
            ("Natural Capital", "Ecosystem services valuation"),
            ("Triple Bottom Line", "Social-environmental-economic accounting"),
            ("ESG Framework", "Corporate sustainability standards"),
            ("Science-Based Targets", "Evidence-based climate goals"),
            ("Net Zero Commitment", "Carbon neutrality objective"),
            ("Just Transition", "Equitable energy transition"),
            ("Indigenous Knowledge Systems", "Traditional ecological knowledge"),
            ("Deep Ecology", "Intrinsic value of nature"),
            ("Stewardship Ethics", "Environmental caretaking"),
            ("Common But Differentiated Responsibility", "International equity principle"),
            ("Planetary Boundaries", "Earth systems limits framework"),
            ("Doughnut Economics", "Social and ecological boundaries"),
            ("Regenerative Economics", "Restorative economic systems"),
            ("Bioregionalism", "Place-based sustainability"),
            ("Eco-Modernism", "Technology-driven sustainability"),
            ("Environmental Pragmatism", "Practical environmental ethics"),
            ("Social Ecology", "Social-ecological integration"),
            ("Industrial Ecology", "Systems-based industrial design"),
            ("Cradle to Cradle", "Closed-loop design philosophy"),
            ("Biomimicry", "Nature-inspired design"),
            ("Systems Thinking", "Holistic problem solving"),
            ("Resilience Thinking", "Adaptive capacity framework"),
            ("Adaptive Management", "Learning-based governance"),
            ("Collaborative Governance", "Multi-stakeholder decision making"),
            ("Deliberative Democracy", "Participatory environmental policy"),
            ("Subsidiarity Principle", "Local decision authority"),
            ("Free Prior and Informed Consent", "Indigenous rights principle"),
            ("Rights of Nature", "Legal personhood for ecosystems"),
            ("Future Generations Principle", "Long-term responsibility"),
            ("Ecological Modernization", "Environmental-economic integration"),
            ("Green New Deal", "Climate and economic justice framework")
        ]

        names = []
        for name, desc in values:
            self.create_node(
                name=name,
                node_type="value_system",
                category="normative_framework",
                description=desc,
                geographic_scope="national",
                adoption_level=random.choice(["emerging", "established", "mainstream"])
            )
            names.append(name)

        return names

    def generate_technology_systems(self) -> List[str]:
        """Generate technology systems and platforms."""

        technologies = [
            ("Solar Photovoltaic Systems", "Solar electricity generation"),
            ("Wind Turbine Technology", "Wind electricity generation"),
            ("Battery Energy Storage", "Grid-scale energy storage"),
            ("Electric Vehicle Platforms", "Zero-emission transportation"),
            ("Heat Pump Technology", "Efficient heating/cooling"),
            ("Carbon Capture Systems", "CO2 removal technology"),
            ("Green Hydrogen Production", "Clean fuel generation"),
            ("Smart Grid Infrastructure", "Advanced electricity grid"),
            ("Building Automation Systems", "Energy management technology"),
            ("Geothermal Energy Systems", "Ground-source energy"),
            ("Advanced Nuclear Reactors", "Next-generation nuclear"),
            ("Biofuel Production", "Renewable liquid fuels"),
            ("Ocean Energy Systems", "Wave and tidal power"),
            ("Energy Modeling Platforms", "Climate analysis tools"),
            ("Emissions Monitoring Systems", "GHG tracking technology"),
            ("Climate Risk Analytics", "Climate data platforms"),
            ("Blockchain Carbon Markets", "Distributed carbon trading"),
            ("AI Climate Optimization", "Machine learning for climate"),
            ("Satellite Climate Monitoring", "Remote sensing systems"),
            ("IoT Environmental Sensors", "Distributed monitoring"),
            ("Concentrated Solar Power", "Thermal solar generation"),
            ("Offshore Wind Technology", "Marine wind generation"),
            ("Floating Solar Arrays", "Water-based solar"),
            ("Pumped Hydro Storage", "Water-based energy storage"),
            ("Compressed Air Storage", "Pneumatic energy storage"),
            ("Flywheel Energy Storage", "Mechanical energy storage"),
            ("Thermal Energy Storage", "Heat and cold storage"),
            ("Liquid Air Storage", "Cryogenic energy storage"),
            ("Gravity Energy Storage Systems", "Potential energy storage"),
            ("Redox Flow Batteries", "Liquid electrolyte batteries"),
            ("Solid State Batteries", "Advanced battery chemistry"),
            ("Lithium Metal Batteries", "High-density batteries"),
            ("Sodium Ion Batteries", "Alternative battery chemistry"),
            ("Zinc Air Batteries", "Metal-air batteries"),
            ("Fuel Cell Technology", "Electrochemical energy conversion"),
            ("Green Ammonia Production", "Carbon-free fuel synthesis"),
            ("Synthetic Fuel Production", "E-fuels technology"),
            ("Bio-CNG Production", "Renewable natural gas"),
            ("Renewable Diesel", "Drop-in biofuel"),
            ("Sustainable Aviation Fuel", "Aviation decarbonization"),
            ("Electric Aircraft", "Zero-emission aviation"),
            ("Hydrogen Aircraft", "Fuel cell aviation"),
            ("Electric Ships", "Maritime electrification"),
            ("Hydrogen Ships", "Hydrogen maritime transport"),
            ("Ammonia Ships", "Ammonia-powered vessels"),
            ("Autonomous Electric Vehicles", "Self-driving EVs"),
            ("Vehicle-to-Grid Technology", "Bidirectional EV charging"),
            ("Wireless EV Charging", "Inductive charging systems"),
            ("Ultra-Fast Charging", "High-power EV charging"),
            ("Battery Swapping Systems", "Removable EV batteries"),
            ("Electric Heavy Trucks", "Zero-emission freight"),
            ("Electric Buses", "Public transit electrification"),
            ("Electric Rail", "Electrified rail transport"),
            ("Hyperloop Technology", "High-speed tube transport"),
            ("Maglev Trains", "Magnetic levitation rail"),
            ("LED Lighting Systems", "Efficient lighting"),
            ("Smart Building Controls", "Automated building management"),
            ("Dynamic Glass Technology", "Adaptive building envelopes"),
            ("Phase Change Materials", "Thermal mass technology"),
            ("Advanced Insulation", "Super-insulation materials"),
            ("Heat Recovery Ventilation", "Energy-efficient ventilation"),
            ("Solar Thermal Systems", "Solar heating technology"),
            ("District Heating Networks", "Centralized heating systems"),
            ("Waste Heat Recovery", "Industrial heat reuse"),
            ("Combined Heat and Power", "Cogeneration systems"),
            ("Microgrids", "Distributed energy systems"),
            ("Virtual Power Plants", "Aggregated distributed resources"),
            ("Demand Response Systems", "Load management technology"),
            ("Grid-Scale Inverters", "Power electronics"),
            ("High Voltage DC Transmission", "Long-distance power transmission"),
            ("Superconducting Cables", "Lossless power transmission"),
            ("Power-to-X Technology", "Electricity conversion systems"),
            ("Direct Air Capture", "Atmospheric CO2 removal"),
            ("Bioenergy with CCS", "Negative emissions technology"),
            ("Enhanced Weathering", "Mineral CO2 sequestration"),
            ("Ocean Alkalinization", "Marine carbon removal"),
            ("Biochar Production", "Agricultural carbon sequestration"),
            ("Soil Carbon Sequestration", "Agricultural carbon storage"),
            ("Afforestation Technology", "Forest establishment systems"),
            ("Precision Agriculture", "Data-driven farming"),
            ("Vertical Farming", "Indoor agriculture"),
            ("Aquaponics Systems", "Integrated agriculture"),
            ("Cultured Meat", "Cell-based protein"),
            ("Plant-Based Proteins", "Alternative proteins"),
            ("Food Waste Digesters", "Organic waste processing"),
            ("Industrial Composting", "Large-scale composting"),
            ("Plasma Gasification", "Waste-to-energy conversion"),
            ("Chemical Recycling", "Advanced plastic recycling"),
            ("Mechanical Recycling", "Materials recovery"),
            ("E-Waste Processing", "Electronics recycling"),
            ("Water Purification Systems", "Advanced water treatment"),
            ("Desalination Technology", "Seawater conversion"),
            ("Atmospheric Water Generation", "Air-to-water systems"),
            ("Smart Water Meters", "Water monitoring technology"),
            ("Leak Detection Systems", "Water loss prevention"),
            ("Drip Irrigation", "Efficient agricultural watering"),
            ("Precision Irrigation", "Data-driven water management"),
            ("Rainwater Harvesting Systems", "Precipitation capture"),
            ("Greywater Recycling", "Wastewater reuse"),
            ("Constructed Wetlands", "Natural wastewater treatment"),
            ("Green Roofs", "Vegetated roof systems"),
            ("Permeable Pavement", "Water-permeable surfaces"),
            ("Bioswales", "Vegetated drainage systems"),
            ("Rain Gardens", "Stormwater management landscaping")
        ]

        names = []
        for name, desc in technologies:
            self.create_node(
                name=name,
                node_type="technology_system",
                category="infrastructure" if "Infrastructure" in name or "Grid" in name else "technology",
                description=desc,
                geographic_scope="national",
                maturity_level=random.choice(["emerging", "growing", "mature"]),
                deployment_scale=random.choice(["pilot", "commercial", "widespread"])
            )
            names.append(name)

        return names

    def generate_international_orgs(self) -> List[str]:
        """Generate international organizations."""

        orgs = [
            ("UNFCCC Secretariat", "UN climate convention"),
            ("Intergovernmental Panel on Climate Change", "Climate science assessment"),
            ("International Energy Agency", "Energy policy coordination"),
            ("World Bank Climate Finance", "Development climate finance"),
            ("International Monetary Fund Climate", "Economic climate policy"),
            ("Green Climate Fund", "Climate finance mechanism"),
            ("Global Environment Facility", "Environmental funding"),
            ("International Renewable Energy Agency", "Renewable energy promotion")
        ]

        names = []
        for name, desc in orgs:
            self.create_node(
                name=name,
                node_type="institution",
                category="international_org",
                description=desc,
                geographic_scope="international",
                governance_level="international"
            )
            names.append(name)

        return names

    def generate_venture_capital(self) -> List[str]:
        """Generate venture capital and investment firms."""

        firms = [
            "Breakthrough Energy Ventures", "Energy Impact Partners",
            "Prelude Ventures", "Congruent Ventures", "Capricorn Investment Group",
            "DBL Partners", "Clean Energy Ventures", "G2VP",
            "Prime Impact Fund", "Elemental Excelerator",
            "The Engine", "Lowercarbon Capital", "Union Square Ventures Climate",
            "Founders Fund Climate", "Sequoia Climate", "Andreessen Horowitz Climate",
            "Khosla Ventures Energy", "Kleiner Perkins Green Growth",
            "NEA Climate Tech", "Accel Climate", "Greylock Energy",
            "Bessemer Climate", "Lightspeed Climate", "Battery Ventures Energy",
            "Index Ventures Climate", "Benchmark Climate", "First Round Climate",
            "Y Combinator Climate", "Techstars Climate", "500 Startups Climate",
            "SOSV Climate", "Plug and Play Energy", "MassChallenge Energy",
            "Greentown Labs Fund", "Prime Coalition", "Activate Capital",
            "Climate Pledge Fund", "Breakthrough Energy Fellows",
            "Clean Energy Trust", "CalSEED", "Cyclotron Road",
            "ARPA-E Bridge", "Wells Fargo Innovation Incubator",
            "PowerHouse Ventures", "Spring Lane Capital", "Generate Capital",
            "Energize Ventures", "Inerjys Ventures", "Clean Growth Fund"
        ]

        names = []
        for name in firms:
            self.create_node(
                name=name,
                node_type="institution",
                category="venture_capital",
                description="Climate tech investment firm",
                geographic_scope="national",
                sector="investment",
                firm_type="venture_capital"
            )
            names.append(name)

        return names

    def generate_consulting_firms(self) -> List[str]:
        """Generate consulting and professional services firms."""

        firms = [
            "McKinsey Sustainability", "BCG Climate", "Bain Sustainability",
            "Deloitte Climate", "PwC Sustainability", "EY Climate Change",
            "KPMG Climate Risk", "Accenture Sustainability",
            "Oliver Wyman Energy", "Roland Berger Sustainability",
            "LEK Energy", "AT Kearney Sustainability", "Strategy& Climate",
            "Willis Towers Watson Climate", "Mercer ESG",
            "Aon Climate Risk", "Marsh Climate Strategy",
            "ICF Climate", "Cadmus Group", "Navigant Energy",
            "DNV Energy Transition", "Wood Mackenzie Power",
            "IHS Markit Energy", "Platts Analytics", "BNEF Research",
            "RMI Consulting", "E3 Energy", "Synapse Energy",
            "Energy Innovation", "Evolved Energy Research"
        ]

        names = []
        for name in firms:
            self.create_node(
                name=name,
                node_type="institution",
                category="consulting",
                description="Sustainability consulting firm",
                geographic_scope="national",
                sector="professional_services",
                firm_type="consulting"
            )
            names.append(name)

        return names

    def generate_think_tanks(self) -> List[str]:
        """Generate think tanks and policy institutes."""

        tanks = [
            "Brookings Climate", "American Enterprise Institute Energy",
            "Center for American Progress Climate", "Heritage Foundation Energy",
            "Cato Institute Energy", "Manhattan Institute Climate",
            "Urban Institute Climate", "RAND Corporation Climate",
            "Aspen Institute Energy", "Council on Foreign Relations Climate",
            "Atlantic Council Climate", "Center for Strategic Studies Energy",
            "Hoover Institution Energy", "American Action Forum Climate",
            "Third Way Climate", "New America Climate",
            "Bipartisan Policy Center Energy", "Climate Leadership Council",
            "Niskanen Center Climate", "R Street Institute Energy",
            "Progressive Policy Institute Climate", "Information Technology Innovation Foundation Energy",
            "Lincoln Institute Land Policy", "Kleinman Center Energy Policy",
            "Payne Institute Energy Research", "Belfer Center Energy",
            "Columbia SIPA Energy", "Georgetown Climate Center",
            "UC Berkeley Goldman School Climate", "MIT CEEPR",
            "Stanford Precourt Energy", "Duke Nicholas Institute",
            "Penn Kleinman Center", "Carnegie Endowment Energy"
        ]

        names = []
        for name in tanks:
            self.create_node(
                name=name,
                node_type="institution",
                category="think_tank",
                description="Policy research institute",
                geographic_scope="national",
                sector="research",
                organization_type="think_tank"
            )
            names.append(name)

        return names

    def generate_industry_associations(self) -> List[str]:
        """Generate industry trade associations."""

        associations = [
            "American Petroleum Institute", "Edison Electric Institute",
            "American Gas Association", "Nuclear Energy Institute",
            "American Public Power Association", "National Rural Electric Cooperative",
            "Large Public Power Council", "Electric Power Supply Association",
            "Independent Petroleum Association", "American Exploration Production Council",
            "Interstate Natural Gas Association", "American Fuel Petrochemical Manufacturers",
            "National Mining Association", "American Coalition for Clean Coal",
            "Clean Energy Business Association", "American Clean Power Association",
            "Solar Energy Industries Association", "American Wind Energy Association",
            "Geothermal Energy Association", "Biomass Power Association Industry",
            "Energy Storage Association Industry", "Fuel Cell Hydrogen Energy Association",
            "American Biogas Council", "Coalition for Renewable Natural Gas",
            "Alliance for Automotive Innovation", "Auto Innovators",
            "Truck Trailer Manufacturers Association", "American Trucking Associations",
            "National Automobile Dealers Association", "EV Charging Infrastructure Association",
            "Airlines for America", "Aerospace Industries Association",
            "American Public Transportation Association", "Association of American Railroads",
            "American Maritime Partnership", "Waterways Council",
            "National Association of Home Builders", "National Association of Realtors",
            "American Institute of Architects", "Associated General Contractors",
            "National Electrical Manufacturers", "Air-Conditioning Heating Refrigeration Institute",
            "American Society of Heating Refrigerating", "Plumbing Heating Cooling Contractors",
            "National Association of Manufacturers", "Business Roundtable",
            "US Chamber of Commerce", "National Federation Independent Business",
            "American Chemistry Council", "American Forest Paper Association",
            "Portland Cement Association", "National Ready Mixed Concrete",
            "American Iron Steel Institute", "Aluminum Association",
            "Semiconductor Industry Association", "Consumer Technology Association",
            "Information Technology Industry Council", "TechNet",
            "National Retail Federation", "Retail Industry Leaders Association",
            "Food Marketing Institute", "National Restaurant Association",
            "American Farm Bureau Federation", "National Farmers Union",
            "National Corn Growers Association", "American Soybean Association",
            "National Cattlemen Beef Association", "National Pork Producers Council",
            "American Beverage Association", "Grocery Manufacturers Association",
            "Real Estate Roundtable", "National Multi Housing Council",
            "National Apartment Association", "Building Owners Managers Association",
            "International Council Shopping Centers", "National Association Industrial Office",
            "Water Environment Federation", "American Water Works Association",
            "National Waste Recycling Association", "Solid Waste Association",
            "Institute of Scrap Recycling Industries", "National Recycling Coalition",
            "American Public Works Association", "Water Utility Climate Alliance",
            "Association of Metropolitan Water Agencies", "National Association Clean Water",
            "American Shore Beach Preservation", "National Association Flood Stormwater",
            "International Economic Development Council", "American Planning Association",
            "National Association of Counties", "US Conference of Mayors",
            "National League of Cities", "National Association of Towns",
            "International City County Management", "Government Finance Officers Association"
        ]

        names = []
        for name in associations:
            self.create_node(
                name=name,
                node_type="institution",
                category="industry_association",
                description="Industry trade association",
                geographic_scope="national",
                sector="trade_association",
                organization_type="membership"
            )
            names.append(name)

        return names

    def generate_labor_unions(self) -> List[str]:
        """Generate labor unions."""

        unions = [
            "AFL-CIO", "International Brotherhood of Electrical Workers",
            "United Steelworkers", "United Auto Workers",
            "International Union Operating Engineers", "Utility Workers Union of America",
            "United Mine Workers of America", "International Association of Machinists",
            "Transport Workers Union", "Amalgamated Transit Union",
            "International Brotherhood of Teamsters", "International Longshoremen",
            "Air Line Pilots Association", "Association of Flight Attendants",
            "United Transportation Union", "Brotherhood of Locomotive Engineers",
            "Service Employees International Union", "American Federation of Teachers",
            "National Education Association", "American Federation of State County Municipal",
            "Communications Workers of America", "International Brotherhood of Boilermakers",
            "United Association of Plumbers", "International Brotherhood of Painters",
            "Laborers International Union", "International Union of Bricklayers",
            "Sheet Metal Air Rail Transportation", "International Association of Heat Insulators",
            "United Farm Workers", "Farm Labor Organizing Committee",
            "Food and Commercial Workers Union", "UNITE HERE",
            "Writers Guild of America", "Screen Actors Guild",
            "American Federation of Musicians", "Actors Equity Association",
            "Office Professional Employees International", "American Postal Workers Union",
            "National Rural Letter Carriers", "National Association of Letter Carriers",
            "International Association of Fire Fighters", "Fraternal Order of Police",
            "American Nurses Association", "National Nurses United",
            "California Labor Federation", "New York State AFL-CIO",
            "Texas AFL-CIO", "Illinois AFL-CIO",
            "Pennsylvania AFL-CIO", "Ohio AFL-CIO"
        ]

        names = []
        for name in unions:
            self.create_node(
                name=name,
                node_type="institution",
                category="labor_union",
                description="Labor union organization",
                geographic_scope="national",
                sector="labor",
                organization_type="union"
            )
            names.append(name)

        return names

    def generate_community_organizations(self) -> List[str]:
        """Generate community-based organizations."""

        orgs = [
            "Uprose Brooklyn", "GreenRoots Chelsea", "PUSH Buffalo",
            "People Organized in Defense of Earth", "Texas Environmental Justice Advocacy",
            "Little Village Environmental Justice Organization Chicago",
            "Communities for a Better Environment California",
            "Asian Pacific Environmental Network", "Strategic Concepts in Organizing Empowerment",
            "Movement for Black Lives Climate Justice", "Hip Hop Caucus",
            "Climate Justice Alliance Network", "It Takes Roots Coalition",
            "Grassroots Global Justice Alliance", "Right to the City Alliance",
            "National Domestic Workers Alliance", "Familias Unidas por la Justicia",
            "Farmworker Association of Florida", "Coalition of Immokalee Workers",
            "Black Farmers Network", "Soul Fire Farm",
            "National Young Farmers Coalition Chapters", "Organización en California de Líderes Campesinas",
            "Urban Habitat Oakland", "SPUR San Francisco",
            "Emerald Cities Collaborative", "Green For All Local Chapters",
            "Alliance for Climate Education", "Center for Earth Ethics",
            "Faith in Place Chicago", "Interfaith Power Light",
            "GreenFaith", "Catholic Climate Covenant",
            "Evangelical Environmental Network", "Coalition on the Environment Jewish Life",
            "Islamic Society of North America Climate", "Hindu American Seva Communities",
            "Buddhist Climate Action Network", "Unitarian Universalist Ministry Earth",
            "National Council of Churches Eco-Justice", "Sojourners Climate Justice",
            "Operation Noah", "Young Evangelicals for Climate Action",
            "Mothers Out Front", "Parents for Future",
            "Moms Clean Air Force", "Our Kids Climate",
            "Zero Hour Youth Movement", "Fridays for Future USA",
            "Youth Climate Strike", "Earth Guardians",
            "Youth Climate Lab", "Alliance for Climate Education Youth",
            "Students for Carbon Dividends", "Climate Cardinals",
            "Sunrise Movement Hubs", "This Is Zero Hour Chapters",
            "Extinction Rebellion US", "Climate Reality Project Chapters",
            "Citizens Climate Lobby Local Chapters", "Cool Block",
            "Mothers of East LA", "West Harlem Environmental Action",
            "North Birmingham United Environmental Justice",
            "St. James Parish Community Action", "Concerned Citizens of St. John",
            "Southeast Louisiana Flood Protection Authority East", "Healthy Gulf",
            "Sankofa Community Empowerment", "Southwest Workers Union San Antonio",
            "New York City Environmental Justice Alliance", "South Bronx Unite",
            "Ironbound Community Corporation Newark", "ACE New Jersey",
            "Clean Water Action Local Groups", "Food Water Watch Chapters",
            "Local Environmental Action Demanded Agency", "Redeemer Community Partnership",
            "Detroit People Platform", "Southwest Detroit Environmental Vision",
            "Michigan Environmental Justice Coalition", "Detroiters Working for Environmental Justice",
            "Neighbors for Clean Air Portland", "Rogue Climate Oregon",
            "Got Green Seattle", "Puget Sound Sage",
            "Front and Centered Washington", "Latino Community Fund Climate",
            "Arizona Environmental Justice Coalition", "Chispa Arizona",
            "New Mexico Environmental Justice Working Group", "Diné CARE",
            "Pueblo Action Alliance", "Conservation Colorado",
            "WildEarth Guardians", "Center for Biological Diversity Local Groups",
            "Sierra Club Local Chapters", "Audubon Society Local Chapters",
            "National Wildlife Federation Affiliates", "Friends Groups National Parks",
            "River Network Affiliates", "Waterkeeper Alliance Local Groups"
        ]

        names = []
        for name in orgs:
            self.create_node(
                name=name,
                node_type="institution",
                category="community_organization",
                description="Community-based advocacy organization",
                geographic_scope="local",
                sector="grassroots",
                organization_type="community"
            )
            names.append(name)

        return names

    def generate_media_organizations(self) -> List[str]:
        """Generate media and communications organizations."""

        media = [
            "Inside Climate News", "Grist Magazine", "Yale Environment 360",
            "E&E News", "Climatewire", "Utility Dive",
            "Canary Media", "Heatmap News", "Drilled Podcast",
            "How to Save a Planet", "Hot Take Podcast", "Volts Podcast",
            "Shift Key Podcast", "Energy Gang Podcast", "Political Climate Podcast",
            "Climate One", "Climate Connections NPR", "PBS Climate Coverage",
            "New York Times Climate Desk", "Washington Post Climate Team",
            "Guardian Climate Coverage", "Reuters Climate Coverage",
            "Bloomberg Green", "Financial Times Climate Capital",
            "Wall Street Journal Energy Coverage", "The Verge Climate",
            "Vox Climate", "ProPublica Climate", "Mother Jones Climate Desk",
            "Rolling Stone Climate Coverage", "The Atlantic Climate",
            "Scientific American Climate", "Popular Science Climate",
            "MIT Technology Review Climate", "Wired Climate",
            "Ars Technica Climate", "The Intercept Climate",
            "Democracy Now Climate", "Earther", "DeSmog Blog",
            "Climate Home News", "Carbon Brief", "Heated Newsletter"
        ]

        names = []
        for name in media:
            self.create_node(
                name=name,
                node_type="institution",
                category="media",
                description="Climate and environmental media",
                geographic_scope="national",
                sector="media",
                organization_type="journalism"
            )
            names.append(name)

        return names

    def generate_professional_associations(self) -> List[str]:
        """Generate professional and scientific associations."""

        associations = [
            "American Meteorological Society", "American Geophysical Union",
            "Ecological Society of America", "Society for Conservation Biology",
            "American Society of Civil Engineers", "American Institute of Chemical Engineers",
            "Institute of Electrical Electronics Engineers Power Energy",
            "American Society of Mechanical Engineers Energy",
            "Society of Petroleum Engineers", "American Association of Petroleum Geologists",
            "Geological Society of America", "Association of Environmental Engineering Science",
            "Water Environment Federation Technical", "Air Waste Management Association",
            "Association of Energy Engineers", "Solar Energy Society",
            "American Solar Energy Society", "International Solar Energy Society",
            "American Council for Energy Efficient Economy Technical",
            "Building Performance Association", "Building Enclosure Science Institute",
            "Building Science Corporation", "Institute for Market Transformation",
            "American Society of Landscape Architects", "Society for Ecological Restoration",
            "Soil Science Society of America", "American Society of Agronomy",
            "Crop Science Society of America", "Society for Range Management",
            "The Wildlife Society", "American Fisheries Society",
            "Society of American Foresters", "Association of Consulting Foresters",
            "American Planning Association Technical", "Urban Land Institute Technical",
            "Congress for New Urbanism Technical", "Institute of Transportation Engineers",
            "American Public Transportation Association Technical",
            "Transportation Research Board", "National Association of City Transportation Officials Technical",
            "Association of Metropolitan Planning Organizations",
            "American Shore Beach Preservation Technical"
        ]

        names = []
        for name in associations:
            self.create_node(
                name=name,
                node_type="institution",
                category="professional_association",
                description="Professional and scientific association",
                geographic_scope="national",
                sector="professional",
                organization_type="membership"
            )
            names.append(name)

        return names

    def generate_relationships(self):
        """Generate realistic relationships between nodes."""

        # Helper to get nodes by category
        def get_nodes_by_category(category: str) -> List[str]:
            return [n["name"] for n in self.nodes if n["category"] == category]

        # Federal agencies regulate state agencies
        federal = get_nodes_by_category("federal_agency")
        states = get_nodes_by_category("state_agency")
        for fed in federal[:5]:  # Top federal agencies
            for state in random.sample(states, min(15, len(states))):
                self.create_relationship(
                    fed, state,
                    relationship_type="regulatory",
                    delivery_type="rules",
                    description="Federal oversight of state implementation"
                )

        # Federal agencies fund research
        research = get_nodes_by_category("research_institution")
        for fed in ["Department of Energy", "National Science Foundation", "Environmental Protection Agency"]:
            if fed in self.node_lookup:
                for inst in random.sample(research, min(10, len(research))):
                    self.create_relationship(
                        fed, inst,
                        relationship_type="funding",
                        delivery_type="money",
                        strength=random.uniform(0.6, 0.9),
                        description="Research grant funding"
                    )

        # State agencies implement federal policies
        policies = get_nodes_by_category("regulation") + get_nodes_by_category("program")
        for state in states:
            for policy in random.sample(policies, min(8, len(policies))):
                self.create_relationship(
                    state, policy,
                    relationship_type="implementation",
                    delivery_type="rules",
                    description="State policy implementation"
                )

        # Utilities regulated by state and federal
        utilities = get_nodes_by_category("private_utility")
        for utility in utilities:
            # Federal regulation
            if "Federal Energy Regulatory Commission" in self.node_lookup:
                self.create_relationship(
                    "Federal Energy Regulatory Commission", utility,
                    relationship_type="regulatory",
                    delivery_type="rules",
                    strength=random.uniform(0.7, 0.9)
                )
            # State regulation
            state_reg = random.choice(states)
            self.create_relationship(
                state_reg, utility,
                relationship_type="regulatory",
                delivery_type="rules",
                strength=random.uniform(0.7, 0.9)
            )

        # Climate tech receives funding from financial institutions
        climate_tech = get_nodes_by_category("climate_tech")
        financial = get_nodes_by_category("financial_services")
        for tech in climate_tech:
            funders = random.sample(financial, min(3, len(financial)))
            for funder in funders:
                self.create_relationship(
                    funder, tech,
                    relationship_type="investment",
                    delivery_type="money",
                    strength=random.uniform(0.5, 0.9),
                    description="Climate technology investment"
                )

        # Federal funding for climate tech
        if "Department of Energy" in self.node_lookup:
            for tech in random.sample(climate_tech, min(12, len(climate_tech))):
                self.create_relationship(
                    "Department of Energy", tech,
                    relationship_type="grant",
                    delivery_type="money",
                    strength=random.uniform(0.6, 0.9),
                    description="Clean energy grant"
                )

        # NGOs advocate for policies
        ngos = get_nodes_by_category("nonprofit")
        for ngo in ngos:
            target_policies = random.sample(policies, min(6, len(policies)))
            for policy in target_policies:
                self.create_relationship(
                    ngo, policy,
                    relationship_type="advocacy",
                    delivery_type="information",
                    strength=random.uniform(0.4, 0.8),
                    description="Policy advocacy"
                )

        # NGOs collaborate with each other
        for i, ngo1 in enumerate(ngos):
            partners = random.sample(ngos[i+1:], min(4, len(ngos) - i - 1))
            for ngo2 in partners:
                self.create_relationship(
                    ngo1, ngo2,
                    relationship_type="collaboration",
                    delivery_type="information",
                    strength=random.uniform(0.5, 0.9),
                    description="Coalition partnership"
                )

        # Research institutions inform policy
        for inst in research:
            target_agencies = random.sample(federal, min(5, len(federal)))
            for agency in target_agencies:
                self.create_relationship(
                    inst, agency,
                    relationship_type="advisory",
                    delivery_type="information",
                    strength=random.uniform(0.6, 0.9),
                    description="Scientific advisory"
                )

        # Municipalities adopt policies
        munis = get_nodes_by_category("municipal_agency")
        for muni in munis:
            local_policies = random.sample(policies, min(5, len(policies)))
            for policy in local_policies:
                self.create_relationship(
                    muni, policy,
                    relationship_type="adoption",
                    delivery_type="rules",
                    strength=random.uniform(0.5, 0.9),
                    description="Local policy adoption"
                )

        # Technology systems deployed by utilities
        techs = get_nodes_by_category("technology") + get_nodes_by_category("infrastructure")
        for utility in utilities:
            deployed = random.sample(techs, min(5, len(techs)))
            for tech in deployed:
                self.create_relationship(
                    utility, tech,
                    relationship_type="deployment",
                    delivery_type="infrastructure",
                    strength=random.uniform(0.4, 0.8),
                    description="Technology deployment"
                )

        # Climate tech develops technologies
        for tech_company in climate_tech:
            technologies = random.sample(techs, min(3, len(techs)))
            for tech in technologies:
                self.create_relationship(
                    tech_company, tech,
                    relationship_type="development",
                    delivery_type="technology",
                    strength=random.uniform(0.6, 0.9),
                    description="Technology development"
                )

        # Value systems influence policies
        values = get_nodes_by_category("normative_framework")
        for value in values:
            influenced = random.sample(policies, min(8, len(policies)))
            for policy in influenced:
                self.create_relationship(
                    value, policy,
                    relationship_type="normative_influence",
                    delivery_type="values",
                    strength=random.uniform(0.3, 0.7),
                    description="Value system influence"
                )

        # International orgs coordinate with federal agencies
        intl = get_nodes_by_category("international_org")
        for org in intl:
            for agency in random.sample(federal, min(8, len(federal))):
                self.create_relationship(
                    org, agency,
                    relationship_type="coordination",
                    delivery_type="information",
                    strength=random.uniform(0.5, 0.8),
                    description="International coordination"
                )

        # Add more cross-category relationships for complexity
        self._add_complex_relationships()

    def _add_complex_relationships(self):
        """Add additional complex relationships for realism."""

        # Tech companies partner with NGOs
        tech = [n["name"] for n in self.nodes if n["category"] == "technology"]
        ngos = [n["name"] for n in self.nodes if n["category"] == "nonprofit"]

        for tech_co in random.sample(tech, min(10, len(tech))):
            partners = random.sample(ngos, min(4, len(ngos)))
            for ngo in partners:
                self.create_relationship(
                    tech_co, ngo,
                    relationship_type="partnership",
                    delivery_type="collaboration",
                    strength=random.uniform(0.4, 0.7)
                )

        # Utilities collaborate with climate tech
        utilities = [n["name"] for n in self.nodes if n["category"] == "private_utility"]
        climate_tech = [n["name"] for n in self.nodes if n["category"] == "climate_tech"]

        for utility in utilities:
            partners = random.sample(climate_tech, min(3, len(climate_tech)))
            for tech in partners:
                self.create_relationship(
                    utility, tech,
                    relationship_type="pilot_program",
                    delivery_type="collaboration",
                    strength=random.uniform(0.5, 0.8)
                )

        # Financial institutions engage with federal regulators
        financial = [n["name"] for n in self.nodes if n["category"] == "financial_services"]
        regulators = ["Securities and Exchange Commission", "Department of Treasury"]

        for fin in financial:
            for reg in regulators:
                if reg in self.node_lookup:
                    self.create_relationship(
                        reg, fin,
                        relationship_type="regulatory",
                        delivery_type="rules",
                        strength=random.uniform(0.7, 0.9)
                    )

        # Research institutions partner with climate tech
        research = [n["name"] for n in self.nodes if n["category"] == "research_institution"]
        for inst in random.sample(research, min(30, len(research))):
            partners = random.sample(climate_tech, min(3, len(climate_tech)))
            for tech in partners:
                self.create_relationship(
                    inst, tech,
                    relationship_type="research_partnership",
                    delivery_type="information",
                    strength=random.uniform(0.6, 0.9)
                )

        # Venture capital invests in climate tech
        vc_firms = [n["name"] for n in self.nodes if n["category"] == "venture_capital"]
        for vc in vc_firms:
            portfolio = random.sample(climate_tech, min(8, len(climate_tech)))
            for company in portfolio:
                self.create_relationship(
                    vc, company,
                    relationship_type="investment",
                    delivery_type="money",
                    strength=random.uniform(0.6, 0.9),
                    description="Venture capital investment"
                )

        # Consulting firms advise corporations and governments
        consulting = [n["name"] for n in self.nodes if n["category"] == "consulting"]
        all_corps = utilities + climate_tech + [n["name"] for n in self.nodes if n["category"] in ["manufacturing", "transportation"]]
        federal = [n["name"] for n in self.nodes if n["category"] == "federal_agency"]

        for firm in consulting:
            # Advise corporations
            clients = random.sample(all_corps, min(10, len(all_corps)))
            for client in clients:
                self.create_relationship(
                    firm, client,
                    relationship_type="advisory",
                    delivery_type="information",
                    strength=random.uniform(0.5, 0.8),
                    description="Strategic consulting"
                )
            # Advise government
            gov_clients = random.sample(federal, min(5, len(federal)))
            for client in gov_clients:
                self.create_relationship(
                    firm, client,
                    relationship_type="advisory",
                    delivery_type="information",
                    strength=random.uniform(0.5, 0.8),
                    description="Policy consulting"
                )

        # Think tanks influence policy and advise government
        think_tanks = [n["name"] for n in self.nodes if n["category"] == "think_tank"]
        policies = [n["name"] for n in self.nodes if n["category"] in ["regulation", "program"]]

        for tank in think_tanks:
            # Influence policy
            influenced = random.sample(policies, min(8, len(policies)))
            for policy in influenced:
                self.create_relationship(
                    tank, policy,
                    relationship_type="policy_influence",
                    delivery_type="information",
                    strength=random.uniform(0.4, 0.7),
                    description="Policy research and advocacy"
                )
            # Advise agencies
            agencies = random.sample(federal, min(5, len(federal)))
            for agency in agencies:
                self.create_relationship(
                    tank, agency,
                    relationship_type="advisory",
                    delivery_type="information",
                    strength=random.uniform(0.5, 0.8),
                    description="Policy advice"
                )

        # Manufacturing companies deploy technologies
        manufacturing = [n["name"] for n in self.nodes if n["category"] == "manufacturing"]
        techs = [n["name"] for n in self.nodes if n["category"] in ["technology", "infrastructure"]]

        for mfg in manufacturing:
            produced = random.sample(techs, min(5, len(techs)))
            for tech in produced:
                self.create_relationship(
                    mfg, tech,
                    relationship_type="production",
                    delivery_type="technology",
                    strength=random.uniform(0.6, 0.9),
                    description="Technology manufacturing"
                )

        # Transportation companies adopt technologies
        transport = [n["name"] for n in self.nodes if n["category"] == "transportation"]
        for trans in transport:
            adopted = random.sample(techs, min(4, len(techs)))
            for tech in adopted:
                self.create_relationship(
                    trans, tech,
                    relationship_type="adoption",
                    delivery_type="technology",
                    strength=random.uniform(0.7, 0.9),
                    description="Technology integration"
                )

        # NGOs collaborate across organizations (more connections)
        for i, ngo1 in enumerate(ngos):
            if i % 2 == 0:  # Do this for half of NGOs to create more connections
                partners = random.sample(ngos[i+1:], min(6, len(ngos) - i - 1))
                for ngo2 in partners:
                    if random.random() > 0.3:  # 70% chance of connection
                        self.create_relationship(
                            ngo1, ngo2,
                            relationship_type="collaboration",
                            delivery_type="information",
                            strength=random.uniform(0.4, 0.8),
                            description="Coalition partnership"
                        )

        # Industry associations lobby for policies
        industry_assocs = [n["name"] for n in self.nodes if n["category"] == "industry_association"]
        for assoc in industry_assocs:
            targets = random.sample(policies, min(6, len(policies)))
            for policy in targets:
                self.create_relationship(
                    assoc, policy,
                    relationship_type="lobbying",
                    delivery_type="information",
                    strength=random.uniform(0.5, 0.9),
                    description="Industry lobbying"
                )

        # Labor unions advocate for policies (especially just transition)
        labor_unions = [n["name"] for n in self.nodes if n["category"] == "labor_union"]
        for union in labor_unions:
            targets = random.sample(policies, min(5, len(policies)))
            for policy in targets:
                self.create_relationship(
                    union, policy,
                    relationship_type="advocacy",
                    delivery_type="information",
                    strength=random.uniform(0.6, 0.9),
                    description="Worker advocacy"
                )

        # Labor unions collaborate with NGOs
        for union in labor_unions:
            if random.random() > 0.4:  # 60% of unions partner with NGOs
                partners = random.sample(ngos, min(3, len(ngos)))
                for ngo in partners:
                    self.create_relationship(
                        union, ngo,
                        relationship_type="collaboration",
                        delivery_type="information",
                        strength=random.uniform(0.5, 0.8),
                        description="Labor-environmental coalition"
                    )

        # Community organizations advocate for local policies and collaborate with NGOs
        community_orgs = [n["name"] for n in self.nodes if n["category"] == "community_organization"]
        for org in community_orgs:
            # Advocate for policies
            targets = random.sample(policies, min(4, len(policies)))
            for policy in targets:
                self.create_relationship(
                    org, policy,
                    relationship_type="advocacy",
                    delivery_type="information",
                    strength=random.uniform(0.5, 0.8),
                    description="Grassroots advocacy"
                )
            # Collaborate with NGOs
            if random.random() > 0.5:
                partners = random.sample(ngos, min(2, len(ngos)))
                for ngo in partners:
                    self.create_relationship(
                        org, ngo,
                        relationship_type="collaboration",
                        delivery_type="information",
                        strength=random.uniform(0.5, 0.8),
                        description="Grassroots-national partnership"
                    )

        # Media organizations cover institutions and issues
        media_orgs = [n["name"] for n in self.nodes if n["category"] == "media"]
        all_institutions = ngos + [n["name"] for n in self.nodes if n["category"] in ["federal_agency", "climate_tech", "think_tank"]]

        for media in media_orgs:
            # Cover institutions
            covered = random.sample(all_institutions, min(8, len(all_institutions)))
            for inst in covered:
                self.create_relationship(
                    media, inst,
                    relationship_type="coverage",
                    delivery_type="information",
                    strength=random.uniform(0.3, 0.7),
                    description="Media coverage"
                )

        # Professional associations provide technical input to policy
        prof_assocs = [n["name"] for n in self.nodes if n["category"] == "professional_association"]
        for assoc in prof_assocs:
            targets = random.sample(policies, min(5, len(policies)))
            for policy in targets:
                self.create_relationship(
                    assoc, policy,
                    relationship_type="technical_input",
                    delivery_type="information",
                    strength=random.uniform(0.6, 0.9),
                    description="Professional technical guidance"
                )
            # Collaborate with research institutions
            if random.random() > 0.5:
                partners = random.sample(research, min(2, len(research)))
                for inst in partners:
                    self.create_relationship(
                        assoc, inst,
                        relationship_type="collaboration",
                        delivery_type="information",
                        strength=random.uniform(0.5, 0.8),
                        description="Professional-academic partnership"
                    )

    def generate_network(self):
        """Generate complete network."""
        print("Generating National Climate Policy Network (2025-2035)...")
        print()

        print("Creating nodes:")
        print("  - Federal agencies...")
        self.generate_federal_agencies()

        print("  - State agencies...")
        self.generate_state_agencies()

        print("  - Municipal agencies...")
        self.generate_municipalities()

        print("  - Private corporations...")
        self.generate_private_corporations()

        print("  - Non-profit organizations...")
        self.generate_nonprofits()

        print("  - Research institutions...")
        self.generate_research_institutions()

        print("  - Policy instruments...")
        self.generate_policy_instruments()

        print("  - Value systems...")
        self.generate_value_systems()

        print("  - Technology systems...")
        self.generate_technology_systems()

        print("  - International organizations...")
        self.generate_international_orgs()

        print("  - Venture capital firms...")
        self.generate_venture_capital()

        print("  - Consulting firms...")
        self.generate_consulting_firms()

        print("  - Think tanks...")
        self.generate_think_tanks()

        print("  - Industry associations...")
        self.generate_industry_associations()

        print("  - Labor unions...")
        self.generate_labor_unions()

        print("  - Community organizations...")
        self.generate_community_organizations()

        print("  - Media organizations...")
        self.generate_media_organizations()

        print("  - Professional associations...")
        self.generate_professional_associations()

        print()
        print(f"Created {len(self.nodes)} nodes")
        print()

        print("Generating relationships...")
        self.generate_relationships()
        print(f"Created {len(self.relationships)} relationships")
        print()

    def get_statistics(self) -> Dict:
        """Calculate network statistics."""
        from collections import Counter

        node_types = Counter(n["category"] for n in self.nodes)
        rel_types = Counter(r["type"] for r in self.relationships)
        delivery_types = Counter(r["delivery_type"] for r in self.relationships)

        # Calculate degree distribution
        out_degrees = Counter()
        in_degrees = Counter()
        for rel in self.relationships:
            out_degrees[rel["source"]] += 1
            in_degrees[rel["target"]] += 1

        avg_out_degree = sum(out_degrees.values()) / len(self.nodes) if self.nodes else 0
        avg_in_degree = sum(in_degrees.values()) / len(self.nodes) if self.nodes else 0

        return {
            "total_nodes": len(self.nodes),
            "total_relationships": len(self.relationships),
            "node_categories": dict(node_types),
            "relationship_types": dict(rel_types),
            "delivery_types": dict(delivery_types),
            "avg_out_degree": round(avg_out_degree, 2),
            "avg_in_degree": round(avg_in_degree, 2),
            "max_out_degree": max(out_degrees.values()) if out_degrees else 0,
            "max_in_degree": max(in_degrees.values()) if in_degrees else 0
        }

    def export_json(self, filepath: Path):
        """Export to JSON format for sfm-core."""
        data = {
            "metadata": {
                "name": "National Climate Policy Network 2025-2035",
                "description": "Synthetic institutional analysis network for climate policy",
                "generated": datetime.now().isoformat(),
                "generator": "sfm-core synthetic data generator v1.0",
                "scenario": "climate_policy_2025_2035"
            },
            "nodes": self.nodes,
            "relationships": self.relationships,
            "statistics": self.get_statistics()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Exported JSON to {filepath}")

    def export_gexf(self, filepath: Path):
        """Export to GEXF format for validation in Gephi."""
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom

            gexf = ET.Element('gexf', {
                'xmlns': 'http://www.gexf.net/1.2draft',
                'version': '1.2'
            })

            meta = ET.SubElement(gexf, 'meta', {
                'lastmodifieddate': datetime.now().isoformat()
            })
            ET.SubElement(meta, 'creator').text = 'SFM-Core Generator'
            ET.SubElement(meta, 'description').text = 'National Climate Policy Network'

            graph = ET.SubElement(gexf, 'graph', {
                'mode': 'static',
                'defaultedgetype': 'directed'
            })

            # Node attributes
            attributes = ET.SubElement(graph, 'attributes', {'class': 'node'})
            ET.SubElement(attributes, 'attribute', {
                'id': '0', 'title': 'category', 'type': 'string'
            })
            ET.SubElement(attributes, 'attribute', {
                'id': '1', 'title': 'ceremonial_score', 'type': 'float'
            })
            ET.SubElement(attributes, 'attribute', {
                'id': '2', 'title': 'instrumental_score', 'type': 'float'
            })

            # Nodes
            nodes = ET.SubElement(graph, 'nodes')
            for node in self.nodes:
                n = ET.SubElement(nodes, 'node', {
                    'id': node['id'],
                    'label': node['name']
                })
                attvalues = ET.SubElement(n, 'attvalues')
                ET.SubElement(attvalues, 'attvalue', {
                    'for': '0',
                    'value': node['category']
                })
                ET.SubElement(attvalues, 'attvalue', {
                    'for': '1',
                    'value': str(node['metadata']['ceremonial_score'])
                })
                ET.SubElement(attvalues, 'attvalue', {
                    'for': '2',
                    'value': str(node['metadata']['instrumental_score'])
                })

            # Edges
            edges = ET.SubElement(graph, 'edges')
            for i, rel in enumerate(self.relationships):
                ET.SubElement(edges, 'edge', {
                    'id': str(i),
                    'source': rel['source'],
                    'target': rel['target'],
                    'weight': str(rel['strength']),
                    'label': rel['type']
                })

            # Pretty print
            xml_str = minidom.parseString(
                ET.tostring(gexf)
            ).toprettyxml(indent="  ")

            with open(filepath, 'w') as f:
                f.write(xml_str)

            print(f"Exported GEXF to {filepath}")
        except Exception as e:
            print(f"Warning: Could not export GEXF: {e}")

    def print_statistics(self):
        """Print detailed network statistics."""
        stats = self.get_statistics()

        print("\n" + "="*60)
        print("NETWORK STATISTICS")
        print("="*60)
        print(f"\nTotal Nodes: {stats['total_nodes']}")
        print(f"Total Relationships: {stats['total_relationships']}")
        print(f"Average Out-Degree: {stats['avg_out_degree']}")
        print(f"Average In-Degree: {stats['avg_in_degree']}")
        print(f"Max Out-Degree: {stats['max_out_degree']}")
        print(f"Max In-Degree: {stats['max_in_degree']}")

        print("\n" + "-"*60)
        print("NODE CATEGORIES")
        print("-"*60)
        for category, count in sorted(
            stats['node_categories'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {category:30s} {count:4d}")

        print("\n" + "-"*60)
        print("RELATIONSHIP TYPES")
        print("-"*60)
        for rel_type, count in sorted(
            stats['relationship_types'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {rel_type:30s} {count:4d}")

        print("\n" + "-"*60)
        print("DELIVERY TYPES")
        print("-"*60)
        for delivery, count in sorted(
            stats['delivery_types'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {delivery:30s} {count:4d}")

        print("\n" + "="*60)


def main():
    """Main execution."""
    output_dir = Path(__file__).parent

    generator = ClimateNetworkGenerator(seed=42)
    generator.generate_network()
    generator.print_statistics()

    # Export files
    print("\nExporting files...")
    generator.export_json(output_dir / "climate_network.json")
    generator.export_gexf(output_dir / "climate_network.gexf")

    print("\n✓ Generation complete!")
    print(f"\nOutput files in: {output_dir}")
    print("  - climate_network.json (SFM-Core format)")
    print("  - climate_network.gexf (Gephi format)")


if __name__ == "__main__":
    main()
