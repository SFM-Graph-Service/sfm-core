# Neo4j Repository Usage Guide

## Overview

The `Neo4jSFMRepository` provides persistent graph storage for SFM data using Neo4j graph database. It implements all methods defined in the `SFMRepository` abstract base class.

## Installation

Ensure neo4j driver is installed:
```bash
pip install neo4j
```

## Basic Usage

### Connecting to Neo4j

```python
from data import Neo4jSFMRepository

# Initialize repository with connection details
repo = Neo4jSFMRepository(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="your_password"
)

# Use as context manager (recommended)
with Neo4jSFMRepository("bolt://localhost:7687", "neo4j", "password") as repo:
    # Work with repository
    node = repo.create_node(my_node)
```

### Creating Nodes

```python
from models import Node
from uuid import uuid4

# Create a node
node = Node(
    id=uuid4(),
    label="Example Node",
    description="A sample node"
)

created_node = repo.create_node(node)
```

### Reading Nodes

```python
# Read by ID
node = repo.read_node(node_id)

# List all nodes
all_nodes = repo.list_nodes()

# List nodes of specific type
from models import MatrixCell
cells = repo.list_nodes(MatrixCell)
```

### Updating Nodes

```python
# Modify and update
node.label = "Updated Label"
updated_node = repo.update_node(node)
```

### Deleting Nodes

```python
# Delete a node
success = repo.delete_node(node_id)
```

### Creating Relationships

```python
from graph.sfm_graph import Relationship

rel = Relationship(
    source_id=node1.id,
    target_id=node2.id,
    kind="INFLUENCES",
    weight=0.8
)

created_rel = repo.create_relationship(rel)
```

### Finding Relationships

```python
# Find by source
rels = repo.find_relationships(source_id=node1.id)

# Find by target
rels = repo.find_relationships(target_id=node2.id)

# Find by kind
from models.sfm_enums import RelationshipKind
rels = repo.list_relationships(kind=RelationshipKind.INFLUENCES)
```

### Working with Graphs

```python
from graph.sfm_graph import SFMGraph

# Load entire graph
graph = repo.load_graph()

# Save entire graph
repo.save_graph(graph)

# Clear all data
repo.clear()
```

## Node Label Mapping

Node labels in Neo4j are derived directly from Python class names:
- `Node` → `:Node`
- `MatrixCell` → `:MatrixCell`
- `SystemProperty` → `:SystemProperty`

## Type Serialization

The repository automatically handles serialization of complex types:

- **UUID**: Converted to/from string
- **datetime**: Converted to/from ISO 8601 format
- **Enum**: Converted to/from value
- **dict/list**: Recursively serialized

## Error Handling

```python
from data import Neo4jConnectionError, Neo4jSerializationError
from models.exceptions import (
    NodeCreationError,
    SFMNotFoundError,
    RelationshipValidationError
)

try:
    repo = Neo4jSFMRepository("bolt://localhost:7687", "neo4j", "password")
except Neo4jConnectionError as e:
    print(f"Connection failed: {e}")

try:
    node = repo.create_node(my_node)
except NodeCreationError as e:
    print(f"Node creation failed: {e}")

try:
    node = repo.read_node(node_id)
    if node is None:
        print("Node not found")
except Exception as e:
    print(f"Error reading node: {e}")
```

## Performance Considerations

1. **Batch Operations**: Use `save_graph()` for bulk inserts
2. **Transactions**: All operations use transactions for data consistency
3. **Connection Management**: Use context manager to ensure proper cleanup
4. **Indexes**: Consider creating indexes in Neo4j for frequently queried properties:
   ```cypher
   CREATE INDEX FOR (n:Node) ON (n.id)
   CREATE INDEX FOR (n:MatrixCell) ON (n.institution_id, n.criteria_id)
   ```

## Testing

Tests use `unittest.mock` to mock the Neo4j driver, requiring no live database:

```bash
pytest tests/test_persistence/test_neo4j.py -v
```

## Connection Configuration

Set up Neo4j connection via environment variables:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_password"
```

```python
import os
from data import Neo4jSFMRepository

repo = Neo4jSFMRepository(
    uri=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)
```
