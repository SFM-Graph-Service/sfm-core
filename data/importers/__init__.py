"""
SFM Core bulk import system.

Provides adapters for importing institutional economics data from various formats:
- CSV/Excel files (academic datasets, spreadsheets)
- OECD API (statistical indicators)
- World Bank API (development indicators)
- SDMX (cross-agency statistical standard)
- RDF/Linked Data (Wikidata, DBpedia)

Basic usage:
    from api.sfm_service import SFMService
    from data.importers import CSVImportAdapter, MappingTemplates

    service = SFMService()
    mapping = MappingTemplates.csv_institution()
    adapter = CSVImportAdapter(mapping)

    result = service.import_bulk('institutions.csv', adapter=adapter)
    print(f"Created {result.nodes_created} nodes")
"""

from .base_adapter import (
    BaseImportAdapter,
    ImportResult,
    ImportConfig,
    ImportError
)

from .mapping_config import (
    MappingConfig,
    FieldMapping,
    MappingTemplates,
    parse_datetime,
    parse_uuid,
    parse_enum,
    to_float,
    to_int
)

from .validators import (
    ValidationError,
    FormatValidationError,
    FieldValidationError,
    NodeValidationError,
    validate_csv_headers,
    validate_enum_value,
    validate_range,
    validate_required_fields,
    validate_uuid,
    validate_node_type,
    validate_duplicate_ids,
    suggest_enum_fix
)

from .csv_adapter import CSVImportAdapter
from .oecd_adapter import OECDAdapter
from .worldbank_adapter import WorldBankAdapter


__all__ = [
    # Base classes
    "BaseImportAdapter",
    "ImportResult",
    "ImportConfig",
    "ImportError",

    # Adapters
    "CSVImportAdapter",
    "OECDAdapter",
    "WorldBankAdapter",

    # Mapping
    "MappingConfig",
    "FieldMapping",
    "MappingTemplates",
    "parse_datetime",
    "parse_uuid",
    "parse_enum",
    "to_float",
    "to_int",

    # Validation
    "ValidationError",
    "FormatValidationError",
    "FieldValidationError",
    "NodeValidationError",
    "validate_csv_headers",
    "validate_enum_value",
    "validate_range",
    "validate_required_fields",
    "validate_uuid",
    "validate_node_type",
    "validate_duplicate_ids",
    "suggest_enum_fix",
]
