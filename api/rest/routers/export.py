"""
Export router: download the graph or a delivery matrix in interchange formats.

Graph exports (whole repository):
- json     : flat snapshot (nodes + relationships + metadata)
- graphml  : GraphML for yEd, Cytoscape, NetworkX
- gexf     : GEXF for Gephi, Sigma.js

Delivery matrix exports (one SFMDeliveryMatrix by id):
- xlsx     : Hayden three-sheet workbook (matrix view, cell descriptions, delivery details)
- xmile    : OASIS XMILE system-dynamics model for Stella / Vensim / ithink

Files are written to a temporary path and streamed back; the temp file is
removed after the response is sent.
"""

import os
import tempfile
import uuid
from enum import Enum
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from api.rest.dependencies import get_sfm_service
from api.sfm_service import SFMService
from graph.exporters import export_delivery_matrix_to_xlsx
from graph.exporters.system_dynamics_exporter import export_to_xmile
from models.delivery_matrix import SFMDeliveryMatrix

router = APIRouter()


class GraphExportFormat(str, Enum):
    json = "json"
    graphml = "graphml"
    gexf = "gexf"


class MatrixExportFormat(str, Enum):
    xlsx = "xlsx"
    xmile = "xmile"


_MEDIA_TYPES = {
    "json": "application/json",
    "graphml": "application/graphml+xml",
    "gexf": "application/gexf+xml",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xmile": "application/xml",
}


class ExportFormatInfo(BaseModel):
    format_name: str
    display_name: str
    file_extension: str
    scope: str = Field(..., description="'graph' for whole-repository exports, 'matrix' for one delivery matrix")
    description: str
    endpoint: str


class ExportFormatsResponse(BaseModel):
    formats: List[ExportFormatInfo]


class MatrixSummary(BaseModel):
    id: uuid.UUID
    label: str
    description: Optional[str] = None
    component_count: int
    cell_count: int
    matrix_scope: Optional[str] = None


class MatrixListResponse(BaseModel):
    matrices: List[MatrixSummary]


def _temp_path(suffix: str) -> Path:
    fd, name = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return Path(name)


def _file_response(path: Path, fmt: str, download_name: str) -> FileResponse:
    return FileResponse(
        path=str(path),
        media_type=_MEDIA_TYPES[fmt],
        filename=download_name,
        background=BackgroundTask(_unlink_quietly, path),
    )


def _unlink_quietly(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _load_matrix(service: SFMService, matrix_id: uuid.UUID) -> SFMDeliveryMatrix:
    node = service.get_node(matrix_id)
    if node is None or not isinstance(node, SFMDeliveryMatrix):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery matrix {matrix_id} not found",
        )
    return node


def _safe_filename(label: str, fallback: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "-_" else "_" for c in label).strip("_")
    return cleaned or fallback


@router.get("/formats", response_model=ExportFormatsResponse, summary="List export formats")
async def list_export_formats() -> ExportFormatsResponse:
    return ExportFormatsResponse(formats=[
        ExportFormatInfo(
            format_name="json", display_name="JSON snapshot", file_extension=".json", scope="graph",
            description="Flat nodes + relationships snapshot with metadata.",
            endpoint="/export/graph?format=json",
        ),
        ExportFormatInfo(
            format_name="graphml", display_name="GraphML", file_extension=".graphml", scope="graph",
            description="GraphML XML for yEd, Cytoscape, NetworkX.",
            endpoint="/export/graph?format=graphml",
        ),
        ExportFormatInfo(
            format_name="gexf", display_name="GEXF", file_extension=".gexf", scope="graph",
            description="Graph Exchange XML for Gephi and Sigma.js.",
            endpoint="/export/graph?format=gexf",
        ),
        ExportFormatInfo(
            format_name="xlsx", display_name="Excel (Hayden format)", file_extension=".xlsx", scope="matrix",
            description="Three-sheet workbook: matrix view, cell descriptions, delivery details.",
            endpoint="/export/matrix/{matrix_id}?format=xlsx",
        ),
        ExportFormatInfo(
            format_name="xmile", display_name="XMILE (System Dynamics)", file_extension=".xmile", scope="matrix",
            description="OASIS XMILE 1.0 model for Stella, Vensim, ithink.",
            endpoint="/export/matrix/{matrix_id}?format=xmile",
        ),
    ])


@router.get(
    "/graph",
    summary="Export whole graph",
    response_class=FileResponse,
    responses={400: {"description": "Graph is empty (graphml/gexf only)"}},
)
async def export_graph(
    format: GraphExportFormat = Query(GraphExportFormat.json, description="Export format"),
    service: SFMService = Depends(get_sfm_service),
) -> FileResponse:
    fmt = format.value
    path = _temp_path(f".{fmt}")
    try:
        service.export_snapshot(str(path), export_format=fmt)
    except ValueError as e:
        _unlink_quietly(path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception:
        _unlink_quietly(path)
        raise
    return _file_response(path, fmt, f"sfm_graph.{fmt}")


@router.get("/matrices", response_model=MatrixListResponse, summary="List delivery matrices available for export")
async def list_matrices(service: SFMService = Depends(get_sfm_service)) -> MatrixListResponse:
    matrices = service.list_nodes(SFMDeliveryMatrix)
    return MatrixListResponse(matrices=[
        MatrixSummary(
            id=m.id,
            label=m.label,
            description=m.description,
            component_count=len(m.components),
            cell_count=len(m.cells),
            matrix_scope=m.matrix_scope,
        )
        for m in matrices
    ])


@router.get(
    "/matrix/{matrix_id}",
    summary="Export one delivery matrix",
    response_class=FileResponse,
    responses={404: {"description": "No delivery matrix with that id"}},
)
async def export_matrix(
    matrix_id: uuid.UUID,
    format: MatrixExportFormat = Query(MatrixExportFormat.xlsx, description="Export format"),
    include_cell_descriptions: bool = Query(True, description="xlsx only: include Cell Descriptions sheet"),
    include_delivery_details: bool = Query(True, description="xlsx only: include Delivery Details sheet"),
    service: SFMService = Depends(get_sfm_service),
) -> FileResponse:
    matrix = _load_matrix(service, matrix_id)
    fmt = format.value
    path = _temp_path(f".{fmt}")
    try:
        if fmt == "xlsx":
            export_delivery_matrix_to_xlsx(
                matrix, path, service,
                include_cell_descriptions=include_cell_descriptions,
                include_delivery_details=include_delivery_details,
            )
        else:
            export_to_xmile(matrix, path, service)
    except Exception:
        _unlink_quietly(path)
        raise
    name = _safe_filename(matrix.label, f"matrix_{matrix_id}")
    return _file_response(path, fmt, f"{name}.{fmt}")
