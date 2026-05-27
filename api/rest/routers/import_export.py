"""
Import/Export router for bulk data operations.

Provides endpoints for:
- Uploading and importing CSV/Excel files
- Importing from external APIs (OECD, World Bank)
- Listing supported import formats
- Export endpoints (future)
"""

from typing import Optional, List
from pathlib import Path
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel, Field

from api.rest.dependencies import get_sfm_service
from data.importers import (
    CSVImportAdapter,
    MappingTemplates,
    ImportConfig,
    ImportResult,
    ImportError as ImportErrorModel
)


router = APIRouter()


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
            adapter_available=False
        ),
        SupportedFormat(
            format_name="worldbank",
            display_name="World Bank API",
            file_extensions=[],
            description="World Bank development indicators (GDP, population, emissions). Requires API access.",
            adapter_available=False
        ),
        SupportedFormat(
            format_name="sdmx",
            display_name="SDMX",
            file_extensions=[".xml"],
            description="Statistical Data and Metadata eXchange standard (ECB, Eurostat, IMF, BIS).",
            adapter_available=False
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
        description="Pre-built mapping template (basic_node, csv_institution, oecd_indicator, worldbank_indicator)"
    ),
    dry_run: bool = Form(default=False, description="Validate without persisting data"),
    continue_on_error: bool = Form(default=True, description="Continue processing after errors"),
    batch_size: int = Form(default=1000, description="Number of nodes per batch")
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
        # Select mapping template
        if mapping_template == "csv_institution":
            mapping = MappingTemplates.csv_institution()
        elif mapping_template == "basic_node":
            mapping = MappingTemplates.basic_node()
        else:
            # Default: basic node mapping
            mapping = MappingTemplates.basic_node()

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
        service = get_sfm_service()
        result = service.import_bulk(temp_path, adapter=adapter, config=config)

        # Convert result to response model
        errors_response = [
            ImportErrorResponse(
                row=err.row,
                field=err.field,
                message=err.message,
                suggestion=err.suggested_fix
            )
            for err in result.errors
        ]

        return ImportResultResponse(
            nodes_created=result.nodes_created,
            nodes_failed=result.nodes_failed,
            relationships_created=result.relationships_created,
            relationships_failed=result.relationships_failed,
            errors=errors_response,
            warnings=result.warnings,
            elapsed_time=result.elapsed_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        ) from e

    finally:
        # Clean up temporary file
        Path(temp_path).unlink(missing_ok=True)


@router.post("/oecd", response_model=ImportResultResponse)
async def import_oecd(
    dataset_id: str = Form(..., description="OECD dataset ID (e.g., GREEN_GROWTH)"),
    filters: Optional[str] = Form(None, description="JSON string of filters (e.g., {\"LOCATION\": \"USA\"})"),
    dry_run: bool = Form(default=False, description="Validate without persisting data")
):
    """
    Import data from OECD.Stat API.

    **NOT YET IMPLEMENTED** - Placeholder for Priority 2 feature.

    Will support importing statistical indicators from OECD datasets:
    - GREEN_GROWTH (environmental indicators)
    - QNA (quarterly national accounts)
    - Custom filters by country, measure, time period
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OECD adapter not yet implemented. Coming in Priority 2 release."
    )


@router.post("/worldbank", response_model=ImportResultResponse)
async def import_worldbank(
    country: str = Form(..., description="Country code (e.g., USA, GBR)"),
    indicator: str = Form(..., description="Indicator code (e.g., NY.GDP.MKTP.CD)"),
    start_year: Optional[int] = Form(None, description="Start year for data range"),
    end_year: Optional[int] = Form(None, description="End year for data range"),
    dry_run: bool = Form(default=False, description="Validate without persisting data")
):
    """
    Import data from World Bank API.

    **NOT YET IMPLEMENTED** - Placeholder for Priority 2 feature.

    Will support importing development indicators:
    - GDP, population, emissions
    - Custom country and indicator filters
    - Time range selection
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="World Bank adapter not yet implemented. Coming in Priority 2 release."
    )
