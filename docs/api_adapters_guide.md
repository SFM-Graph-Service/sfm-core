# API Adapters Guide - OECD and World Bank

**Note**: This is research software under active development. Claude AI was used to assist with documentation. Verify imported data against original sources.

## Overview

SFM Core supports importing institutional economics data directly from public APIs:

- **OECD.Stat API** - Environmental indicators, national accounts, economic statistics
- **World Bank API** - Development indicators, GDP, population, emissions

Both adapters handle automatic pagination, rate limiting, response caching, and error recovery.

## OECD Adapter

### Quick Start

```python
from api.sfm_service import SFMService
from data.importers import OECDAdapter

service = SFMService()

# Quarterly national accounts for the USA from the OECD Data Explorer API
adapter = OECDAdapter(
    dataset_id="OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.0",
    filters={"FREQ": "Q", "REF_AREA": "USA"}
)

result = service.import_bulk("oecd:OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.0", adapter=adapter)
print(f"Imported {result.nodes_created} indicators in {result.elapsed_time:.2f}s")
```

> The legacy `stats.oecd.org` endpoint was retired in 2024. `OECDAdapter` now talks to
> `https://sdmx.oecd.org/public/rest`, where dataflow ids are agency-qualified
> (`AGENCY,DATAFLOW,VERSION`) and the country dimension is `REF_AREA`. Copy the id from the
> Data Explorer's *API* panel. Parsing is shared with `SDMXAdapter`, which you can also use
> directly with `agency="OECD"`.

### REST API

```bash
# Import OECD GREEN_GROWTH dataset for USA
curl -X POST "http://localhost:8000/api/v1/import/oecd" \
  -F "dataset_id=GREEN_GROWTH" \
  -F 'filters={"LOCATION": "USA"}'

# Response:
{
  "nodes_created": 24,
  "nodes_failed": 0,
  "elapsed_time": 1.2
}
```

### Finding Dataflow IDs

OECD dataflow ids follow the `AGENCY,DATAFLOW,VERSION` convention (for example the quarterly national accounts flow is of the form `OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.0`), and the OECD revises them. Rather than copying ids from documentation, list them from the live service:

```python
from data.importers import SDMXAdapter

catalogue = SDMXAdapter(agency="OECD", flow="")
for flow in catalogue.list_dataflows(query="national accounts")[:5]:
    print(flow["flow_ref"], "-", flow["name"])
# OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.0 - Quarterly national accounts   (illustrative)

adapter = OECDAdapter(dataset_id=catalogue.list_dataflows(query="QNA")[0]["flow_ref"],
                      filters={"FREQ": "Q", "REF_AREA": "USA"})
```

`list_dataflows()` works for every agency the SDMX adapter knows (`SDMXAdapter(agency="ECB", flow="").list_dataflows()`), and the Data Explorer's *API* panel shows the same id for any table you are viewing.

### Filter Dimensions

OECD datasets use dimension-based filtering:

```python
# Single country
filters = {"LOCATION": "USA"}

# Country + measure
filters = {"LOCATION": "FRA", "MEASURE": "CO2"}

# Multiple dimensions
filters = {
    "LOCATION": "GBR",
    "MEASURE": "RENEWABLE",
    "TIME_PERIOD": "2020"
}
```

### Data Mapping

OECD data is mapped to `SocialFabricIndicator` nodes:

```python
# OECD SDMX-JSON structure:
{
  "LOCATION": "USA",
  "Value": 5000000000,
  "TIME_PERIOD": "2020",
  "MEASURE": "CO2",
  "dataset_id": "GREEN_GROWTH"
}

# Mapped to SFM node:
SocialFabricIndicator(
    label="GREEN_GROWTH",
    current_value=5000000000,
    meta={
        "country": "USA",
        "year": 2020,
        "measure": "CO2",
        "data_source": "OECD"
    }
)
```

### Advanced Usage

#### Rate Limiting

```python
# Slower rate limit for API restrictions
adapter = OECDAdapter(
    dataset_id="GREEN_GROWTH",
    rate_limit_delay=1.0  # 1 second between requests
)
```

#### Custom Mapping

```python
from data.importers import MappingConfig, FieldMapping

# Custom mapping for specific use case
mapping = MappingConfig(node_type="SocialCost")
mapping.add_mapping(FieldMapping(
    source_field="Value",
    target_field="cost_amount",
    transform=float
))

adapter = OECDAdapter(
    dataset_id="GOV_DEBT",
    mapping=mapping
)
```

#### Error Handling

```python
from data.importers import ImportConfig

config = ImportConfig(
    dry_run=True,  # Preview before importing
    continue_on_error=True
)

adapter = OECDAdapter(dataset_id="GREEN_GROWTH", config=config)
result = service.import_bulk("oecd:GREEN_GROWTH", adapter=adapter)

if result.errors:
    print("Validation errors found:")
    for error in result.errors:
        print(f"  {error.message}")
```

## World Bank Adapter

### Quick Start

```python
from api.sfm_service import SFMService
from data.importers import WorldBankAdapter

service = SFMService()

# Import GDP data for USA (2010-2020)
adapter = WorldBankAdapter(
    country="USA",
    indicator="GDP",
    start_year=2010,
    end_year=2020
)

result = service.import_bulk("worldbank:USA:GDP", adapter=adapter)
print(f"Imported {result.nodes_created} data points")
```

### REST API

```bash
# Import World Bank GDP data
curl -X POST "http://localhost:8000/api/v1/import/worldbank" \
  -F "country=USA" \
  -F "indicator=GDP" \
  -F "start_year=2010" \
  -F "end_year=2020"

# Using indicator code directly
curl -X POST "http://localhost:8000/api/v1/import/worldbank" \
  -F "country=GBR" \
  -F "indicator=NY.GDP.MKTP.CD"
```

### Common Indicators

| Name | Code | Description |
|------|------|-------------|
| `GDP` | `NY.GDP.MKTP.CD` | GDP (current US$) |
| `GDP_GROWTH` | `NY.GDP.MKTP.KD.ZG` | GDP growth (annual %) |
| `POPULATION` | `SP.POP.TOTL` | Population, total |
| `CO2_EMISSIONS` | `EN.ATM.CO2E.KT` | CO2 emissions (kilotons) |
| `POVERTY` | `SI.POV.DDAY` | Poverty headcount ratio |
| `GINI` | `SI.POV.GINI` | GINI inequality index |
| `UNEMPLOYMENT` | `SL.UEM.TOTL.ZS` | Unemployment (% of labor force) |

### Country Codes

World Bank uses ISO 3166-1 alpha-3 codes:

- `USA` - United States
- `GBR` - United Kingdom  
- `CHN` - China
- `FRA` - France
- `DEU` - Germany
- `ALL` - All countries (use with caution - large dataset)

### Data Mapping

World Bank data is mapped to `SocialFabricIndicator` nodes:

```python
# World Bank API response:
{
  "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
  "country": {"id": "USA", "value": "United States"},
  "value": 21000000000000,
  "date": "2020"
}

# Mapped to SFM node:
SocialFabricIndicator(
    label="GDP (current US$)",
    current_value=21000000000000,
    meta={
        "country": "USA",
        "year": 2020,
        "data_source": "World Bank"
    }
)
```

### Advanced Usage

#### Multiple Countries

```python
# Import for multiple countries (sequential)
countries = ["USA", "GBR", "CHN", "FRA"]

for country in countries:
    adapter = WorldBankAdapter(
        country=country,
        indicator="GDP",
        start_year=2015,
        end_year=2020
    )
    result = service.import_bulk(f"worldbank:{country}:GDP", adapter=adapter)
    print(f"{country}: {result.nodes_created} data points")
```

#### All Available Years

```python
# Import all available years (no year range)
adapter = WorldBankAdapter(
    country="USA",
    indicator="POPULATION"
    # No start_year/end_year = all available data
)
```

#### Custom Rate Limiting

```python
# Slower rate for API restrictions
adapter = WorldBankAdapter(
    country="USA",
    indicator="GDP",
    rate_limit_delay=0.5  # 500ms between requests
)
```

## SDMX Adapter

SDMX 2.1 is the exchange standard shared by most national and international statistical agencies. One adapter covers all of them.

### Quick Start

```python
from api.sfm_service import SFMService
from data.importers import SDMXAdapter, SDMX_AGENCIES

service = SFMService()

# ECB monthly USD/EUR reference rate since 2023
adapter = SDMXAdapter(
    agency="ECB",
    flow="EXR",
    key="M.USD.EUR.SP00.A",
    params={"startPeriod": "2023"},
)
result = service.import_bulk("sdmx:ECB:EXR:M.USD.EUR.SP00.A", adapter=adapter)
print(f"Imported {result.nodes_created} observations")

# Eurostat GDP for Germany, current prices
adapter = SDMXAdapter(agency="EUROSTAT", flow="nama_10_gdp", key="A.CP_MEUR.B1GQ.DE")
service.import_bulk("sdmx:EUROSTAT:nama_10_gdp:A.CP_MEUR.B1GQ.DE", adapter=adapter)

# Any other SDMX 2.1 service, by base URL
adapter = SDMXAdapter(agency="https://stats.example.org/sdmx", flow="MY_FLOW")

# A file downloaded earlier (SDMX-JSON or SDMX-ML)
adapter = SDMXAdapter(agency="IMF", flow="IFS")
service.import_bulk("ifs_extract.xml", adapter=adapter)
```

`SDMX_AGENCIES` lists the built-in base URLs: `ECB`, `EUROSTAT`, `BIS`, `IMF`, `ILO`, `OECD`, `UNSD`, `WB`.

### REST API

```bash
curl -X POST "http://localhost:8000/api/v1/import/sdmx" \
  -F "agency=ECB" -F "flow=EXR" -F "key=M.USD.EUR.SP00.A" -F "start_period=2023"
```

### Data Mapping

Each observation becomes a `SocialFabricIndicator`:

| Node field | Source |
|------------|--------|
| `label` | dataflow id |
| `current_value` | observation value (observations with no value are skipped) |
| `meta.country` | `REF_AREA`, `LOCATION`, `GEO`, `COUNTRY` or `AREA`, whichever the flow uses |
| `meta.period` | `TIME_PERIOD` as given (`2023`, `2023-Q1`, `2023-03`) |
| `meta.year` | first four digits of the period |
| `meta.frequency`, `meta.unit` | `FREQ`, `UNIT_MEASURE` |
| `meta.agency`, `meta.data_source` | agency code, `SDMX:<agency>` |

Every dimension and attribute in the message is available to a custom `MappingConfig` under its SDMX id (and `<id>_name` for the human-readable label when the message carries one).

### Formats Understood

- SDMX-JSON 1.0 and 2.0, series-keyed (`dataSets[].series`) and flat (`dataSets[].observations`), including series and observation attributes
- SDMX-ML 2.1 Generic (`SeriesKey` / `ObsDimension` / `ObsValue`) and StructureSpecific (dimensions as XML attributes), including flat `Obs` under `DataSet`

The adapter asks for SDMX-JSON first and falls back to whatever the service returns, so agencies that only speak SDMX-ML work unchanged.

## RDF / Linked Data Adapter

Institutional data published as Linked Data (Wikidata and DBpedia extracts, organisational ontologies, SKOS vocabularies) can be imported directly. Unlike the statistical adapters, this one produces **relationships as well as nodes**.

### Quick Start

```python
from api.sfm_service import SFMService
from data.importers import RDFAdapter

service = SFMService()
adapter = RDFAdapter(type_map={
    "GovernmentOrganization": "InstitutionalStructure",   # rdf:type local name -> SFM node type
    "https://schema.org/Legislation": "PolicyInstrument",  # or a full IRI
})
result = service.import_bulk("institutions.ttl", adapter=adapter)
print(result.nodes_created, result.relationships_created)
```

Formats: Turtle (`.ttl`), RDF/XML (`.rdf`, `.owl`, `.xml`), N-Triples (`.nt`), N3 (`.n3`), JSON-LD (`.jsonld`, `.json`), TriG (`.trig`). Pass `rdf_format=` to override the extension-based guess.

### REST API

```bash
curl -X POST "http://localhost:8000/api/v1/import/rdf" \
  -F "file=@institutions.ttl" \
  -F 'type_map={"GovernmentOrganization": "InstitutionalStructure"}'
```

### What Becomes What

| RDF | SFM |
|-----|-----|
| Any IRI with a label (`rdfs:label`, `schema:name`, `skos:prefLabel`, `dcterms:title`, `foaf:name`) | A node; `id = uuid5(NAMESPACE_URL, iri)`, so re-imports resolve to the same node |
| `rdfs:comment`, `schema:description`, `dcterms:description`, `skos:definition` | `description` |
| `rdf:type` | `meta.rdf_types`; `type_map` picks the SFM node class |
| Object property between two imported resources | A relationship; `kind` is the predicate's local name in snake_case (`reportsTo` → `reports_to`), IRI kept in `meta.predicate` |
| Resources without a label, literal-valued properties, blank nodes | Skipped |

Language-tagged labels prefer `preferred_language` (default `en`), then untagged, then whatever is first.

## Performance Considerations

### OECD Adapter

- **Rate Limit**: Default 0.5s between requests (2 req/sec)
- **Caching**: Responses cached in memory per session
- **Typical Dataset Size**: 10-1000 observations
- **Average Import Time**: 2-10 seconds

### World Bank Adapter

- **Rate Limit**: Default 0.3s between requests (~3 req/sec)
- **Pagination**: Automatic (1000 records/page)
- **Caching**: Responses cached per page
- **Typical Dataset Size**: 10-100 data points (per country/indicator)
- **Average Import Time**: 1-5 seconds

### Optimization Tips

1. **Use Filters** - Narrow dataset with filters to reduce API calls
2. **Batch Imports** - Import multiple indicators in one session to leverage cache
3. **Dry-Run First** - Validate before full import to catch errors early
4. **Adjust Rate Limits** - Increase delay if hitting API limits

## Error Handling

### Common Errors

#### OECD Dataset Not Found

```
Error: OECD dataset 'INVALID_DATASET' not found
```

**Solution**: Check available datasets at https://stats.oecd.org/

#### World Bank Invalid Country

```
Error: World Bank country 'XYZ' or indicator 'INVALID' not found
```

**Solution**: Use valid ISO 3-letter country codes

#### API Rate Limit

```
Error: Too many requests (429)
```

**Solution**: Increase `rate_limit_delay` parameter

#### Network Timeout

```
Error: Request timeout after 30s
```

**Solution**: Check network connection, try again later

### Retry Logic

Both adapters include automatic retry with exponential backoff:

```python
# Default: 3 retries with 1s, 2s, 4s delays
# Configured internally, no user action needed
```

## Comparison

| Feature | OECD Adapter | World Bank Adapter |
|---------|--------------|-------------------|
| **Data Format** | SDMX-JSON | JSON |
| **Pagination** | Single response | Multi-page |
| **Filters** | Dimension-based | Country + Indicator + Year range |
| **Rate Limit** | 2 req/sec | 3 req/sec |
| **Caching** | Per dataset+filters | Per page |
| **Typical Use** | Environmental, economic statistics | Development indicators, time series |
| **Node Type** | SocialFabricIndicator | SocialFabricIndicator |

## Best Practices

1. **Start Small** - Test with single country/indicator before bulk imports
2. **Use Dry-Run** - Validate data structure before committing
3. **Monitor API Usage** - Be mindful of rate limits
4. **Cache Results** - Re-use imported data instead of re-fetching
5. **Handle Nulls** - World Bank returns `null` for missing data
6. **Check Metadata** - Verify `meta.data_source` to track origin

## Examples

### Environmental Analysis

```python
# Import CO2 emissions for major economies
countries = ["USA", "CHN", "DEU", "GBR", "FRA"]
adapter = OECDAdapter(
    dataset_id="GREEN_GROWTH",
    filters={"MEASURE": "CO2"}
)

for country in countries:
    adapter.filters["LOCATION"] = country
    adapter._cache.clear()  # Clear cache for new country
    result = service.import_bulk("oecd:GREEN_GROWTH", adapter=adapter)
```

### Economic Comparison

```python
# Compare GDP growth across countries
adapter = WorldBankAdapter(
    country="ALL",  # Warning: large dataset
    indicator="GDP_GROWTH",
    start_year=2015,
    end_year=2020
)

result = service.import_bulk("worldbank:ALL:GDP_GROWTH", adapter=adapter)
```

### Time Series Analysis

```python
# Build 20-year GDP time series for USA
adapter = WorldBankAdapter(
    country="USA",
    indicator="GDP",
    start_year=2000,
    end_year=2020
)

result = service.import_bulk("worldbank:USA:GDP", adapter=adapter)

# Result: 21 data points (one per year)
```

## API References

- **OECD.Stat API**: https://data.oecd.org/api/sdmx-json-documentation/
- **World Bank API**: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392

## See Also

- [Bulk Import Guide](bulk_import_guide.md)
- [CSV Import Guide](bulk_import_guide.md#csv-format-examples)
- [Field Mapping](bulk_import_guide.md#field-mapping)
- [REST API Reference](rest_api.md)
