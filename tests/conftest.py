"""
Shared fixtures.

`backend_service` yields an SFMService for each storage backend so the same
contract test runs against NetworkX and, when NEO4J_URI is set, a live Neo4j.
Neo4j-backed parametrisations carry the `neo4j` marker so they can be run
serially (`-m neo4j`) against a shared database while everything else runs
in parallel (`-m "not neo4j"`).
"""

import os

import pytest

from api.sfm_service import SFMService, SFMServiceConfig


BACKENDS = [
    "networkx",
    pytest.param("neo4j", marks=pytest.mark.neo4j),
]


@pytest.fixture(params=BACKENDS)
def backend(request):
    if request.param == "neo4j" and not os.getenv("NEO4J_URI"):
        pytest.skip("NEO4J_URI not set; live Neo4j backend unavailable")
    return request.param


@pytest.fixture
def backend_service(backend):
    if backend == "neo4j":
        config = SFMServiceConfig(
            storage_type="neo4j",
            neo4j_uri=os.environ["NEO4J_URI"],
            neo4j_username=os.getenv("NEO4J_USERNAME", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "password"),
        )
    else:
        config = SFMServiceConfig(storage_type="networkx")

    service = SFMService(config)
    service.repository.clear()
    try:
        yield service
    finally:
        service.repository.clear()
        close = getattr(service.repository, "close", None)
        if callable(close):
            close()
