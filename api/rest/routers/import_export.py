"""
Import router for bulk data operations.

Provides endpoints for:
- Uploading and importing CSV/Excel files
- Importing from external APIs (OECD, World Bank)
- Listing supported import formats

Export endpoints live in api.rest.routers.export.
"""

from typing import Dict, Optional, List
from pathlib import Path
import logging
import tempfile

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel, Field

from api.rest.dependencies import get_sfm_service
from api.sfm_service import SFMService
from data.importers import (
    CSVImportAdapter,
    OECDAdapter,
    WorldBankAdapter,
    SDMXAdapter,
    SDMX_AGENCIES,
    MappingTemplates,
    ImportConfig,
)
from models.exceptions import SFMError


logger = logging.getLogger(__name__)
router = APIRouter()

MAPPING_TEMPLATES = {
    "basic_node": MappingTemplates.basic_node,
    "csv_institution": MappingTemplates.csv_institution,
    "oecd_indicator": MappingTemplates.oecd_indicator,
    "worldbank_indicator": MappingTemplates.worldbank_indicator,
    "sdmx_indicator": MappingTemplates.sdmx_indicator,
}


def _to_response(result) -> "ImportResultResponse":
    return ImportResultResponse(
        nodes_created=result.nodes_created,
        nodes_failed=result.nodes_failed,
        relationships_created=result.relationships_created,
        relationships_failed=result.relationships_failed,
        errors=[
            ImportErrorResponse(row=e.row, field=e.field, message=e.message, suggestion=e.suggested_fix)
            for e in result.errors
        ],
        warnings=result.warnings,
        elapsed_time=result.elapsed_time,
    )


# ==================== Response Schemas ====================

class ImportErrorResponse(BaseModel):
    """Single import error."""
    row: Optional[int] = Field(None, description="Row number where error occurred")
    field: Optional[str] = Field(None, description="Field name that caused error")
    message: str = Field(..., description="Error message")
    suggestion: Optional[str] = Field(None, description="Suggested fix")

    model_config = {"from_attributes": True}


class ImportResultResponse(BaseModel):
    """Result of bulk import operation."""
    nodes_created: int = Field(..., description="Number of nodes successfully created")
    nodes_failed: int = Field(..., description="Number of nodes that failed validation")
    relationships_created: int = Field(0, description="Number of relationships created")
    relationships_failed: int = Field(0, description="Number of relationships that failed")
    errors: List[ImportErrorResponse] = Field(default_factory=list, description="List of errors encountered")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")
    elapsed_time: float = Field(..., description="Total import time in seconds")

    model_config = {
        "json_schema_extra": {
            "example": {
                "nodes_created": 147,
                "nodes_failed": 3,
                "relationships_created": 0,
                "relationships_failed": 0,
                "errors": [
                    {
                        "row": 15,
                        "field": "type",
                        "message": "Invalid enum value 'foo'",
                        "suggestion": "Did you mean 'REGULATORY'?"
                    }
                ],
                "warnings": [],
                "elapsed_time": 0.52
            }
        }
    }


class SupportedFormat(BaseModel):
    """Supported import format description."""
    format_name: str = Field(..., description="Format identifier")
    display_name: str = Field(..., description="Human-readable format name")
    file_extensions: List[str] = Field(..., description="Supported file extensions")
    description: str = Field(..., description="Format description")
    adapter_available: bool = Field(..., description="Whether adapter is implemented")


class FormatsListResponse(BaseModel):
    """List of supported import formats."""
    formats: List[SupportedFormat]

    model_config = {
        "json_schema_extra": {
            "example": {
                "formats": [
                    {
                        "format_name": "csv",
                        "display_name": "CSV/Excel",
                        "file_extensions": [".csv", ".xlsx", ".xls", ".tsv"],
                        "description": "Comma-separated values or Excel spreadsheet",
                        "adapter_available": True
                    },
                    {
                        "format_name": "oecd",
                        "display_name": "OECD.Stat API",
                        "file_extensions": [],
                        "description": "OECD statistical indicators via API",
                        "adapter_available": False
                    }
                ]
            }
        }
    }


# ==================== Endpoints ====================

@router.get("/formats", response_model=FormatsListResponse)
async def list_supported_formats():
    """
    List all supported import formats.

    Returns information about available adapters, file extensions,
    and format descriptions.
    """
    formats = [
        SupportedFormat(
            format_name="csv",
            display_name="CSV/Excel",
            file_extensions=[".csv", ".xlsx", ".xls", ".tsv"],
            description="Comma-separated values or Excel spreadsheet files. Supports custom field mapping.",
            adapter_available=True
        ),
        SupportedFormat(
            format_name="oecd",
            display_name="OECD.Stat API",
            file_extensions=[],
            description="OECD statistical indicators (GREEN_GROWTH, QNA datasets). Requires API access.",
            adapter_available=True
        ),
        SupportedFormat(
            format_name="worldbank",
            display_name="World Bank API",
            file_extensions=[],
            description="World Bank development indicators (GDP, population, emissions). Requires API access.",
            adapter_available=True
        ),
        SupportedFormat(
            format_name="sdmx",
            display_name="SDMX 2.1",
            file_extensions=[".xml", ".json"],
            description=(
                "SDMX 2.1 REST services (" + ", ".join(sorted(SDMX_AGENCIES)) + " or any base URL) "
                "and local SDMX-JSON / SDMX-ML files."
            ),
            adapter_available=True
        ),
        SupportedFormat(
            format_name="rdf",
            display_name="RDF/Turtle",
            file_extensions=[".rdf", ".ttl", ".n3"],
            description="RDF/Linked Data from Wikidata, DBpedia institutional entities.",
            adapter_available=False
        )
    ]

    return FormatsListResponse(formats=formats)


@router.post("/csv", response_model=ImportResultResponse)
async def import_csv(
    file: UploadFile = File(..., description="CSV or Excel file to import"),
    node_type: str = Form(default="Node", description="Default node type for imported data"),
    mapping_template: Optional[str] = Form(
        default=None,
        description="Pre-built mapping template (basic_node, csv_institution, oecd_indicator, worldbank_indicator, sdmx_indicator)"
    ),
    dry_run: bool = Form(default=False, description="Validate without persisting data"),
    continue_on_error: bool = Form(default=True, description="Continue processing after errors"),
    batch_size: int = Form(default=1000, description="Number of nodes per batch"),
    service: SFMService = Depends(get_sfm_service),
):
    """
    Import nodes from CSV or Excel file.

    Supports:
    - CSV files (.csv, .tsv)
    - Excel files (.xlsx, .xls)
    - Custom field mapping via templates
    - Dry-run validation
    - Error handling modes

    The file will be streamed for large datasets to avoid memory issues.
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename required"
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.csv', '.xlsx', '.xls', '.tsv', '.txt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Supported: .csv, .xlsx, .xls, .tsv"
        )

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='wb', suffix=file_ext, delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        template_name = mapping_template or "basic_node"
        template_factory = MAPPING_TEMPLATES.get(template_name)
        if template_factory is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown mapping_template '{template_name}'. "
                       f"Valid options: {', '.join(sorted(MAPPING_TEMPLATES))}"
            )
        mapping = template_factory()

        # Override node type if specified
        if node_type != "Node":
            mapping.node_type = node_type

        # Create import config
        config = ImportConfig(
            dry_run=dry_run,
            continue_on_error=continue_on_error,
            batch_size=batch_size
        )

        # Create adapter and import
        adapter = CSVImportAdapter(mapping, config)
        result = service.import_bulk(temp_path, adapter=adapter, config=config)
        return _to_response(result)

    except (HTTPException, SFMError):
        raise
    except Exception as e:
        logger.exception("CSV import failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Import failed due to an internal error"
        ) from e

    finally:
        # Clean up temporary file
        Path(temp_path).unlink(missing_ok=True)


@router.post("/oecd", response_model=ImportResultResponse)
async def import_oecd(
    dataset_id: str = Form(..., description="OECD dataset ID (e.g., GREEN_GROWTH, QNA)"),
    filters: Optional[str] = Form(None, description="JSON string of filters (e.g., {\"LOCATION\": \"USA\"})"),
    dry_run: bool = Form(default=False, description="Validate without persisting data"),
    batch_size: int = Form(default=1000, description="Number of nodes per batch"),
    service: SFMService = Depends(get_sfm_service),
):
    """
    Import data from OECD.Stat API.

    Supports importing statistical indicators from OECD datasets:
    - GREEN_GROWTH (environmental indicators)
    - QNA (quarterly national accounts)
    - Custom datasets with dimension filters

    **Examples**:
    - dataset_id="GREEN_GROWTH", filters='{"LOCATION": "USA"}'
    - dataset_id="QNA", filters='{"LOCATION": "FRA", "MEASURE": "CUR"}'

    Data is automatically paginated and mapped to SocialFabricIndicator nodes.
    """
    import json

    # Parse filters
    filter_dict = {}
    if filters:
        try:
            filter_dict = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON in filters parameter"
            )

    try:
        # Create import config
        config = ImportConfig(
            dry_run=dry_run,
            continue_on_error=True,
            batch_size=batch_size
        )

        # Create OECD adapter
        adapter = OECDAdapter(
            dataset_id=dataset_id,
            filters=filter_dict,
            config=config
        )

        # Import via service
        source = f"oecd:{dataset_id}"
        result = service.import_bulk(source, adapter=adapter, config=config)
        return _to_response(result)

    except (HTTPException, SFMError):
        raise
    except Exception as e:
        logger.exception("OECD import failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OECD import failed due to an internal error"
        ) from e


@router.post("/worldbank", response_model=ImportResultResponse)
async def import_worldbank(
    country: str = Form(..., description="Country code (e.g., USA, GBR, CHN)"),
    indicator: str = Form(..., description="Indicator code or name (e.g., NY.GDP.MKTP.CD or GDP)"),
    start_year: Optional[int] = Form(None, description="Start year for data range"),
    end_year: Optional[int] = Form(None, description="End year for data range"),
    dry_run: bool = Form(default=False, description="Validate without persisting data"),
    batch_size: int = Form(default=1000, description="Number of nodes per batch"),
    service: SFMService = Depends(get_sfm_service),
):
    """
    Import data from World Bank API.

    Supports importing development indicators:
    - GDP (NY.GDP.MKTP.CD or "GDP")
    - Population (SP.POP.TOTL or "POPULATION")
    - CO2 emissions (EN.ATM.CO2E.KT or "CO2_EMISSIONS")
    - And 100+ other indicators

    **Examples**:
    - country="USA", indicator="GDP", start_year=2010, end_year=2020
    - country="GBR", indicator="NY.GDP.MKTP.CD"
    - country="CHN", indicator="POPULATION", start_year=2015

    Data is automatically paginated and mapped to SocialFabricIndicator nodes.
    """
    try:
        # Create import config
        config = ImportConfig(
            dry_run=dry_run,
            continue_on_error=True,
            batch_size=batch_size
        )

        # Create World Bank adapter
        adapter = WorldBankAdapter(
            country=country,
            indicator=indicator,
            start_year=start_year,
            end_year=end_year,
            config=config
        )

        # Import via service
        source = f"worldbank:{country}:{indicator}"
        result = service.import_bulk(source, adapter=adapter, config=config)
        return _to_response(result)

    except (HTTPException, SFMError):
        raise
    except Exception as e:
        logger.exception("World Bank import failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="World Bank import failed due to an internal error"
        ) from e


@router.post("/sdmx", response_model=ImportResultResponse)
async def import_sdmx(
    agency: str = Form(..., description="Agency code (" + ", ".join(sorted(SDMX_AGENCIES)) + ") or SDMX REST base URL"),
    flow: str = Form(..., description="Dataflow id, e.g. EXR (ECB) or nama_10_gdp (Eurostat)"),
    key: str = Form(default="all", description="Dot-separated dimension key, e.g. M.USD.EUR.SP00.A; 'all' for no filter"),
    start_period: Optional[str] = Form(None, description="Earliest period to include, e.g. 2020 or 2020-Q1"),
    end_period: Optional[str] = Form(None, description="Latest period to include"),
    dry_run: bool = Form(default=False, description="Validate without persisting data"),
    batch_size: int = Form(default=1000, description="Number of nodes per batch"),
    service: SFMService = Depends(get_sfm_service),
):
    """
    Import observations from any SDMX 2.1 REST service.

    Understands SDMX-JSON (series-keyed and flat) and SDMX-ML (Generic and
    StructureSpecific) responses, so it works with ECB, Eurostat, BIS, IMF,
    ILO, OECD, UN and World Bank endpoints. Observations are mapped to
    SocialFabricIndicator nodes labelled by dataflow, with country, period,
    year, frequency, unit and provenance in meta.

    **Examples**:
    - agency="ECB", flow="EXR", key="M.USD.EUR.SP00.A", start_period="2023"
    - agency="EUROSTAT", flow="nama_10_gdp", key="A.CP_MEUR.B1GQ.DE"
    """
    params: Dict[str, str] = {}
    if start_period:
        params["startPeriod"] = start_period
    if end_period:
        params["endPeriod"] = end_period

    config = ImportConfig(dry_run=dry_run, continue_on_error=True, batch_size=batch_size)
    try:
        adapter = SDMXAdapter(agency=agency, flow=flow, key=key, params=params, config=config)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    try:
        source = f"sdmx:{adapter.agency}:{adapter.flow}:{adapter.key}"
        result = service.import_bulk(source, adapter=adapter, config=config)
        return _to_response(result)

    except (HTTPException, SFMError):
        raise
    except Exception as e:
        logger.exception("SDMX import failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SDMX import failed due to an internal error"
        ) from e
