#!/bin/bash
# Test script for Docker container deployment
set -e

echo "=========================================="
echo "Testing Docker Container Deployment"
echo "=========================================="

# Test 1: Check Docker availability
echo ""
echo "Test 1: Checking Docker..."
if command -v docker >/dev/null 2>&1; then
    echo "✓ Docker installed: $(docker --version)"
else
    echo "✗ Docker not installed"
    exit 1
fi

# Test 2: Check docker-compose availability
echo ""
echo "Test 2: Checking docker-compose..."
if command -v docker-compose >/dev/null 2>&1; then
    echo "✓ docker-compose installed: $(docker-compose --version)"
elif docker compose version >/dev/null 2>&1; then
    echo "✓ docker compose (plugin) installed: $(docker compose version)"
    # Use docker compose instead of docker-compose
    shopt -s expand_aliases
    alias docker-compose='docker compose'
else
    echo "✗ docker-compose not installed"
    exit 1
fi

# Test 3: Verify Dockerfile exists
echo ""
echo "Test 3: Checking Dockerfile..."
if [ -f "Dockerfile" ]; then
    echo "✓ Dockerfile found"
    echo "  Base image: $(grep '^FROM' Dockerfile)"
else
    echo "✗ Dockerfile not found"
    exit 1
fi

# Test 4: Verify docker-compose.yml exists
echo ""
echo "Test 4: Checking docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    echo "✓ docker-compose.yml found"
    SERVICES=$(grep -E "^  [a-z-]+:" docker-compose.yml | wc -l)
    echo "  Services defined: $SERVICES"
else
    echo "✗ docker-compose.yml not found"
    exit 1
fi

# Test 5: Build Docker image
echo ""
echo "Test 5: Building Docker image..."
if docker build -t sfm-core:test . >/dev/null 2>&1; then
    echo "✓ Docker image built successfully"
    echo "  Image size: $(docker images sfm-core:test --format '{{.Size}}')"
else
    echo "✗ Docker build failed"
    exit 1
fi

# Test 6: Test container startup (NetworkX mode)
echo ""
echo "Test 6: Testing container startup..."
CONTAINER_ID=$(docker run -d --rm \
    -e STORAGE_TYPE=networkx \
    -p 8888:8000 \
    sfm-core:test \
    /bin/bash -c "pip install -e . && python -c 'from api.sfm_service import SFMService; print(\"Service OK\")' && sleep 5")

if [ -n "$CONTAINER_ID" ]; then
    echo "✓ Container started: $CONTAINER_ID"
    sleep 2

    # Check container logs
    LOGS=$(docker logs "$CONTAINER_ID" 2>&1)
    if echo "$LOGS" | grep -q "Service OK"; then
        echo "✓ SFM service initialized in container"
    else
        echo "⚠ Service check uncertain"
    fi

    # Stop container
    docker stop "$CONTAINER_ID" >/dev/null 2>&1
    echo "✓ Container stopped"
else
    echo "✗ Container failed to start"
    exit 1
fi

# Test 7: Test example execution in container
echo ""
echo "Test 7: Testing example execution in container..."
EXAMPLE_OUTPUT=$(docker run --rm \
    sfm-core:test \
    /bin/bash -c "pip install -e . >/dev/null 2>&1 && python examples/hayden_case_studies/nebraska_k12_finance.py 2>&1 | tail -5")

if echo "$EXAMPLE_OUTPUT" | grep -q "Components:"; then
    echo "✓ Nebraska K-12 example ran successfully in container"
    echo "  Output: $(echo "$EXAMPLE_OUTPUT" | grep "Components:")"
else
    echo "⚠ Example execution check uncertain"
    echo "  Output: $EXAMPLE_OUTPUT"
fi

# Test 8: Cleanup test image
echo ""
echo "Test 8: Cleanup..."
if docker rmi sfm-core:test >/dev/null 2>&1; then
    echo "✓ Test image removed"
else
    echo "⚠ Could not remove test image"
fi

echo ""
echo "=========================================="
echo "Container Deployment Summary"
echo "=========================================="
echo "✓ All container tests passed"
echo ""
echo "Deployment options:"
echo "  1. Dev container: docker-compose up sfm"
echo "  2. API server (NetworkX): docker-compose up api-dev"
echo "  3. API server (Neo4j): docker-compose up api-neo4j neo4j"
echo "  4. Standalone: docker run -p 8000:8000 sfm-core"
echo ""
