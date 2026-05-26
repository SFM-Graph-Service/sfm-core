"""
Demonstration of using the SFM Core REST API.

This script shows how to:
1. Create nodes via REST API
2. Query nodes and statistics
3. Perform ceremonial analysis
4. Detect conflicts
5. Evaluate digraph relationships

Prerequisites:
    pip install requests

Usage:
    # Start the API server first
    uvicorn api.rest.app:app --reload

    # Then run this script
    python examples/rest_api_demo.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print('=' * 60)


def print_response(response: requests.Response):
    """Print formatted response data."""
    if response.status_code in (200, 201):
        print(f"✓ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


def demo_health_check():
    """Check API health and get statistics."""
    print_section("1. Health Check & Statistics")

    print("\nGetting health status...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)

    print("\nGetting graph statistics...")
    response = requests.get(f"{BASE_URL}/statistics")
    print_response(response)


def demo_node_crud() -> str:
    """Demonstrate node CRUD operations."""
    print_section("2. Node CRUD Operations")

    # Create
    print("\nCreating a new institution node...")
    response = requests.post(
        f"{BASE_URL}/nodes/",
        json={
            "label": "Federal Reserve System",
            "description": "Central banking system of the United States",
            "node_type": "Institution",
            "meta": {
                "established": "1913",
                "type": "central_bank",
                "source": "API Demo"
            }
        }
    )
    print_response(response)
    node_id = response.json()["id"]

    # Read
    print(f"\nRetrieving node {node_id}...")
    response = requests.get(f"{BASE_URL}/nodes/{node_id}")
    print_response(response)

    # Update
    print(f"\nUpdating node {node_id}...")
    response = requests.put(
        f"{BASE_URL}/nodes/{node_id}",
        json={
            "label": "Federal Reserve System (Updated)",
            "description": "Central banking system - updated description",
            "node_type": "Institution",
            "meta": {
                "established": "1913",
                "type": "central_bank",
                "source": "API Demo",
                "status": "active"
            }
        }
    )
    print_response(response)

    # List
    print("\nListing all nodes...")
    response = requests.get(f"{BASE_URL}/nodes/")
    data = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"Total nodes: {data['total']}")
    print(f"Nodes returned: {len(data['nodes'])}")

    return node_id


def demo_ceremonial_analysis():
    """Demonstrate ceremonial analysis query."""
    print_section("3. Ceremonial Analysis")

    print("\nRunning ceremonial analysis (threshold=0.5)...")
    response = requests.post(
        f"{BASE_URL}/query/ceremonial",
        json={"threshold": 0.5}
    )
    print_response(response)


def demo_conflicts():
    """Demonstrate conflict detection."""
    print_section("4. Conflict Detection")

    print("\nDetecting system conflicts...")
    response = requests.get(f"{BASE_URL}/query/conflicts")
    print_response(response)


def demo_digraph_evaluation(node_id: str):
    """Demonstrate digraph evaluation."""
    print_section("5. Digraph Evaluation")

    print(f"\nEvaluating institutional dependencies for node {node_id}...")
    response = requests.post(
        f"{BASE_URL}/evaluate/digraph",
        json={
            "institutions": [node_id],
            "analyze_sequences": True
        }
    )
    print_response(response)


def demo_cleanup(node_id: str):
    """Clean up created nodes."""
    print_section("6. Cleanup")

    print(f"\nDeleting node {node_id}...")
    response = requests.delete(f"{BASE_URL}/nodes/{node_id}")
    if response.status_code == 204:
        print("✓ Node deleted successfully (204 No Content)")
    else:
        print(f"✗ Status: {response.status_code}")

    print("\nVerifying deletion...")
    response = requests.get(f"{BASE_URL}/nodes/{node_id}")
    if response.status_code == 404:
        print("✓ Confirmed: Node not found (404)")
    else:
        print(f"Unexpected status: {response.status_code}")


def main():
    """Run all API demonstrations."""
    print("\n" + "=" * 60)
    print(" SFM Core REST API Demonstration")
    print("=" * 60)
    print("\nThis script demonstrates the REST API capabilities.")
    print(f"API Base URL: {BASE_URL}")

    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n✗ Error: API is not responding correctly")
            print("Make sure the API server is running:")
            print("  uvicorn api.rest.app:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to API server")
        print("Make sure the API server is running:")
        print("  uvicorn api.rest.app:app --reload")
        return

    # Run demonstrations
    demo_health_check()

    node_id = demo_node_crud()

    demo_ceremonial_analysis()

    demo_conflicts()

    demo_digraph_evaluation(node_id)

    demo_cleanup(node_id)

    print("\n" + "=" * 60)
    print(" Demo Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("- Explore the interactive docs: http://localhost:8000/api/v1/docs")
    print("- Read API_DOCUMENTATION.md for detailed examples")
    print("- Check out the Phase 2 query and Phase 3 evaluation endpoints")


if __name__ == "__main__":
    main()
