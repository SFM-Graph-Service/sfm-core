"""
Graph module for SFM Core - Network representation and query capabilities.
"""

# Phase 2 Step 1-2: Graph structures and query engine
from graph.sfm_graph import (
    NetworkMetrics,
    SFMGraph,
    Relationship,
)
from graph.sfm_query import (
    AnalysisType,
    QueryResult,
    NodeMetrics,
    FlowAnalysis,
    SFMQueryEngine,
    NetworkXSFMQueryEngine,
    SFMQueryFactory,
)

__all__ = [
    # Graph
    "NetworkMetrics",
    "SFMGraph",
    "Relationship",
    # Query
    "AnalysisType",
    "QueryResult",
    "NodeMetrics",
    "FlowAnalysis",
    "SFMQueryEngine",
    "NetworkXSFMQueryEngine",
    "SFMQueryFactory",
]
