# SFM Graph Persistence Guide

**Version**: Beta  
**Status**: Production Ready  
**Last Updated**: June 2026

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Save/Load Operations](#saveload-operations)
4. [Storage Formats](#storage-formats)
5. [Management Operations](#management-operations)
6. [Export/Import Operations](#exportimport-operations)
7. [Security Considerations](#security-considerations)
8. [Common Workflows](#common-workflows)
9. [API Reference](#api-reference)

---

## Overview

The SFM persistence layer provides comprehensive capabilities for saving, loading, and managing Social Fabric Matrix graphs. All persistence operations are available through the `SFMService` API.

### Available Features

- **Save/Load Operations** - Persist graphs to disk and restore them
- **Storage Formats** - JSON (human-readable) and Pickle (Python objects), with optional compression
- **Management** - Clear all data, reload previous states
- **Export/Import** - Share graphs in standard formats (GraphML, GEXF, JSON)
- **Version Control** - Track graph metadata and checksums

### Key Benefits

- **Data Preservation** - Retain complex graph structures across sessions
- **Collaboration** - Share graphs in standard formats
- **Workflow Flexibility** - Save checkpoints, test changes, rollback easily
- **Format Choice** - Human-readable JSON or efficient Pickle storage

---

## Quick Start

```python
from api.sfm_service import SFMService
from models import Node

# Create service and build a graph
service = SFMService()

node1 = Node(label="Institution A", description="Primary institution")
node2 = Node(label="Institution B", description="Secondary institution")
service.create_node(node1)
service.create_node(node2)

# Save to disk
result = service.save("my_graph.json")
print(f"Saved {result['node_count']} nodes to {result['filepath']}")

# Load in a new session
new_service = SFMService()
new_service.load("my_graph.json")
print(f"Loaded {len(new_service.list_nodes())} nodes")
```

---

## Save/Load Operations

### `save(filename, format_type, base_path)`

Persist the current graph to disk.

**Parameters**:
- `filename` (str): Name of the file to create
- `format_type` (str, optional): Storage format - `"json"`, `"json.gz"`, `"pickle"`, or `"pickle.gz"`. Default: `"json"`
- `base_path` (str, optional): Directory path for storage. Default: `"./sfm_data"`

**Returns**: Dictionary with metadata:
```python
{
    "filepath": "/path/to/file",
    "node_count": 42,
    "relationship_count": 15,
    "format": "json",
    "size_bytes": 12345,
    "checksum": "abc123..."
}
```

**Example**:
```python
from api.sfm_service import SFMService
from models import Node

service = SFMService()
service.create_node(Node(label="Test Node"))

# Save as JSON (recommended)
result = service.save("my_graph.json")

# Save as compressed JSON (better for large graphs)
result = service.save("my_graph.json.gz", format_type="json.gz")

# Save to custom directory
result = service.save("backup.json", base_path="/home/user/backups")

# Save as pickle (requires allow_pickle=True on load)
result = service.save("my_graph.pickle", format_type="pickle")
```

---

### `load(filename, format_type, base_path, replace, allow_pickle)`

Load a graph from disk.

**Parameters**:
- `filename` (str): Name of the file to load
- `format_type` (str, optional): Storage format used when saving. Default: `"json"`
- `base_path` (str, optional): Directory path where file is stored. Default: `"./sfm_data"`
- `replace` (bool, optional): If `True`, replace current graph. If `False`, merge loaded data. Default: `True`
- `allow_pickle` (bool, optional): **Security-sensitive** - Set to `True` only for trusted pickle files. Default: `False`

**Returns**: Dictionary with load results:
```python
{
    "filepath": "/path/to/file",
    "total_nodes": 42,
    "total_relationships": 15,
    "nodes_loaded": 42,
    "relationships_loaded": 15,
    "replaced": True
}
```

**Example**:
```python
# Load and replace current graph (default)
service = SFMService()
result = service.load("my_graph.json")

# Merge with existing graph
service.load("additional_data.json", replace=False)

# Load compressed format
service.load("my_graph.json.gz", format_type="json.gz")

# Load from custom directory
service.load("backup.json", base_path="/home/user/backups")

# Load pickle (ONLY for trusted sources)
service.load("my_graph.pickle", format_type="pickle", allow_pickle=True)
```

**Replace vs Merge**:
```python
# Replace mode (replace=True) - Discards current data
service1 = SFMService()
service1.create_node(Node(label="Node A"))
service1.load("graph.json", replace=True)
# Result: Only nodes from graph.json

# Merge mode (replace=False) - Combines data
service2 = SFMService()
service2.create_node(Node(label="Node A"))
service2.load("graph.json", replace=False)
# Result: Node A + all nodes from graph.json
```

---

### `reload(filename, format_type, base_path)`

Convenience method to discard unsaved changes and reload from disk. Equivalent to `load(..., replace=True)`.

**Parameters**: Same as `load()`

**Returns**: Same as `load()`

**Example**:
```python
service = SFMService()

# Save initial state
service.create_node(Node(label="Saved Node"))
service.save("checkpoint.json")

# Make changes
service.create_node(Node(label="Unsaved Node"))
print(f"Before reload: {len(service.list_nodes())} nodes")  # 2 nodes

# Discard changes and reload
service.reload("checkpoint.json")
print(f"After reload: {len(service.list_nodes())} nodes")  # 1 node
```

---

## Storage Formats

The persistence layer supports four storage formats:

| Format | Extension | Description | Use Case |
|--------|-----------|-------------|----------|
| `JSON` | `.json` | Human-readable text | **Recommended** - Easy to inspect, version control friendly |
| `COMPRESSED_JSON` | `.json.gz` | Gzipped JSON | Large graphs, reduced disk space |
| `PICKLE` | `.pickle` | Python binary | Fast serialization, complex Python objects |
| `COMPRESSED_PICKLE` | `.pickle.gz` | Gzipped pickle | Maximum compression, fastest load times |

### Format Comparison

```python
from api.sfm_service import SFMService
from models import Node

service = SFMService()

# Create a test graph
for i in range(100):
    service.create_node(Node(label=f"Node {i}", description=f"Description {i}"))

# Compare formats
formats = [
    ("data.json", "json"),
    ("data.json.gz", "json.gz"),
    ("data.pickle", "pickle"),
    ("data.pickle.gz", "pickle.gz")
]

for filename, format_type in formats:
    result = service.save(filename, format_type=format_type)
    print(f"{format_type:20} - {result['size_bytes']:8} bytes")

# Output example:
# json                 -    45678 bytes
# json.gz              -    12345 bytes
# pickle               -    38901 bytes
# pickle.gz            -     9876 bytes
```

### Format Recommendations

- **JSON** - Default choice for most use cases
  - Human-readable
  - Git-friendly
  - Language-agnostic
  - Safe to share

- **COMPRESSED_JSON** - Large graphs (>1000 nodes)
  - 60-80% size reduction
  - Still inspectable (gunzip first)
  - Safe to share

- **PICKLE** - Advanced use only
  - Fastest save/load
  - Preserves Python object state exactly
  - **Security risk** - See [Security Considerations](#security-considerations)

- **COMPRESSED_PICKLE** - Maximum efficiency
  - Smallest file size
  - Fastest for very large graphs
  - **Security risk** - See [Security Considerations](#security-considerations)

---

## Management Operations

### `unload()`

Clear all nodes and relationships from the current graph. Useful for starting fresh or discarding work.

**Parameters**: None

**Returns**: Dictionary with removal counts:
```python
{
    "nodes_removed": 42,
    "relationships_removed": 15,
    "timestamp": "2026-06-22T10:30:00"
}
```

**Example**:
```python
service = SFMService()

# Build a graph
for i in range(5):
    service.create_node(Node(label=f"Node {i}"))

print(f"Before unload: {len(service.list_nodes())} nodes")  # 5 nodes

# Clear everything
result = service.unload()
print(f"Removed {result['nodes_removed']} nodes")

print(f"After unload: {len(service.list_nodes())} nodes")  # 0 nodes
```

**Common Patterns**:

```python
# Save → Experiment → Discard → Reload
service.save("checkpoint.json")
# ... try experimental changes ...
service.unload()
service.load("checkpoint.json")

# Clear and start fresh
service.unload()
# ... build new graph ...
service.save("new_graph.json")

# Load without merge artifacts
service.unload()  # Ensure clean slate
service.load("imported_data.json")
```

---

## Export/Import Operations

### `export_snapshot(filepath, export_format)`

Export graph to external formats for use with other tools.

**Parameters**:
- `filepath` (str): Full path for the exported file
- `export_format` (str): Export format - `"json"`, `"graphml"`, or `"gexf"`

**Returns**: Dictionary with export metadata:
```python
{
    "filepath": "/path/to/export.graphml",
    "format": "graphml",
    "node_count": 42,
    "relationship_count": 15
}
```

**Supported Formats**:

| Format | Extension | Description | Compatible Tools |
|--------|-----------|-------------|------------------|
| `json` | `.json` | Custom snapshot format | Python, JavaScript, any JSON parser |
| `graphml` | `.graphml` | GraphML XML | Gephi, Cytoscape, yEd, NetworkX |
| `gexf` | `.gexf` | Graph Exchange XML | Gephi, Sigma.js, NetworkX |

**Example**:
```python
from api.sfm_service import SFMService
from models import Node

service = SFMService()
service.create_node(Node(label="Node A"))
service.create_node(Node(label="Node B"))

# Export to JSON snapshot
result = service.export_snapshot(
    "/home/user/exports/snapshot.json",
    export_format="json"
)

# Export to GraphML for Gephi
result = service.export_snapshot(
    "/home/user/exports/visualization.graphml",
    export_format="graphml"
)

# Export to GEXF for web visualization
result = service.export_snapshot(
    "/home/user/exports/web_viz.gexf",
    export_format="gexf"
)
```

**JSON Snapshot Format**:
```json
{
  "metadata": {
    "graph_id": "uuid-here",
    "name": "SFM Graph",
    "description": "",
    "version": 1,
    "created_at": "2026-06-22T10:00:00",
    "exported_at": "2026-06-22T10:30:00",
    "node_count": 2,
    "relationship_count": 1
  },
  "nodes": [
    {
      "type": "Node",
      "id": "uuid-1",
      "label": "Node A",
      "description": "",
      "meta": {}
    }
  ],
  "relationships": [
    {
      "id": "uuid-rel",
      "source_id": "uuid-1",
      "target_id": "uuid-2",
      "kind": "connects_to",
      "weight": null,
      "meta": {}
    }
  ]
}
```

---

### `import_snapshot(filepath)`

Import a JSON snapshot back into the graph.

**Parameters**:
- `filepath` (str): Full path to the JSON snapshot file

**Returns**: Dictionary with import results:
```python
{
    "filepath": "/path/to/snapshot.json",
    "node_count": 42,
    "relationship_count": 15,
    "total_nodes": 42,
    "total_relationships": 15
}
```

**Example**:
```python
from api.sfm_service import SFMService

service = SFMService()

# Import JSON snapshot
result = service.import_snapshot("/home/user/exports/snapshot.json")

print(f"Imported {result['node_count']} nodes")
print(f"Imported {result['relationship_count']} relationships")

# Verify data
nodes = service.list_nodes()
print(f"Total nodes now: {len(nodes)}")
```

**Export/Import Roundtrip**:
```python
# Export from service1
service1 = SFMService()
service1.create_node(Node(label="Original Node"))
service1.export_snapshot("/tmp/export.json", export_format="json")

# Import into service2
service2 = SFMService()
service2.import_snapshot("/tmp/export.json")

# Verify preservation
assert len(service2.list_nodes()) == 1
assert service2.list_nodes()[0].label == "Original Node"
```

---

## Security Considerations

### Pickle Deserialization Risk

**WARNING**: The `PICKLE` and `COMPRESSED_PICKLE` formats use Python's `pickle` module.

**Security Issue**: Deserializing pickle data from an **untrusted source** allows **arbitrary code execution** on the host system (CWE-502).

**Mitigation**: Pickle deserialization is **disabled by default**. You must explicitly opt-in:

```python
# UNSAFE - Only use for files you created yourself
service.load("my_graph.pickle", format_type="pickle", allow_pickle=True)

# SAFE - JSON formats have no code execution risk
service.load("my_graph.json", format_type="json")  # No allow_pickle needed
```

### Safe Practices

✅ **DO**:
- Use JSON formats by default
- Only use pickle for files you created yourself
- Verify file sources before using `allow_pickle=True`
- Store pickle files in restricted directories

❌ **DON'T**:
- Load pickle files from email attachments
- Load pickle files from untrusted users
- Load pickle files from public repositories
- Enable `allow_pickle` for external data sources

### Example: Safe Pickle Workflow

```python
# Safe: Save your own work
service1 = SFMService()
service1.create_node(Node(label="My Work"))
service1.save("my_work.pickle", format_type="pickle")

# Safe: Load your own file
service2 = SFMService()
service2.load("my_work.pickle", format_type="pickle", allow_pickle=True)

# UNSAFE: Don't do this
# service.load("downloaded_graph.pickle", format_type="pickle", allow_pickle=True)
```

### Converting Pickle to JSON

If you receive a pickle file from a trusted source, convert it to JSON:

```python
# One-time conversion (in a sandboxed environment)
trusted_service = SFMService()
trusted_service.load("trusted.pickle", format_type="pickle", allow_pickle=True)
trusted_service.save("trusted.json", format_type="json")

# Future use: Load the JSON version
service = SFMService()
service.load("trusted.json")  # Safe, no pickle risk
```

---

## Common Workflows

### 1. Save and Restore Session

Preserve your work between sessions.

```python
from api.sfm_service import SFMService
from models import Node

# Session 1: Build and save
service = SFMService()

node1 = Node(label="Institution A", description="Primary")
node2 = Node(label="Institution B", description="Secondary")
service.create_node(node1)
service.create_node(node2)

# Save work
result = service.save("session_2026_06_22.json")
print(f"Saved to {result['filepath']}")

# Session 2: Restore and continue
new_service = SFMService()
new_service.load("session_2026_06_22.json")

# Continue working
node3 = Node(label="Institution C", description="Tertiary")
new_service.create_node(node3)

# Save updated state
new_service.save("session_2026_06_22_updated.json")
```

---

### 2. Experiment with Changes

Try modifications without losing original work.

```python
from api.sfm_service import SFMService
from models import Node

service = SFMService()

# Build initial graph
service.create_node(Node(label="Original Node 1"))
service.create_node(Node(label="Original Node 2"))

# Save checkpoint
service.save("before_experiment.json")

# Try experimental changes
service.create_node(Node(label="Experimental Node"))
# ... test the changes ...

# If changes work: save new version
service.save("after_experiment.json")

# If changes don't work: rollback
service.reload("before_experiment.json")  # Discards experimental changes
```

---

### 3. Merge Multiple Graphs

Combine data from different sources.

```python
from api.sfm_service import SFMService
from models import Node

# Service 1: Economic data
econ_service = SFMService()
econ_service.create_node(Node(label="Market A", meta={"type": "economic"}))
econ_service.create_node(Node(label="Market B", meta={"type": "economic"}))
econ_service.save("economic_data.json")

# Service 2: Social data
social_service = SFMService()
social_service.create_node(Node(label="Community A", meta={"type": "social"}))
social_service.create_node(Node(label="Community B", meta={"type": "social"}))
social_service.save("social_data.json")

# Service 3: Merge both
merged_service = SFMService()

# Load first dataset (replace=True is default)
merged_service.load("economic_data.json")
print(f"After economic: {len(merged_service.list_nodes())} nodes")

# Load second dataset (replace=False to merge)
merged_service.load("social_data.json", replace=False)
print(f"After social: {len(merged_service.list_nodes())} nodes")

# Save combined graph
merged_service.save("combined_data.json")

# Verify merge
nodes = merged_service.list_nodes()
economic_nodes = [n for n in nodes if n.meta.get("type") == "economic"]
social_nodes = [n for n in nodes if n.meta.get("type") == "social"]

print(f"Economic nodes: {len(economic_nodes)}")
print(f"Social nodes: {len(social_nodes)}")
```

---

### 4. Export for External Tools

Visualize or analyze in Gephi, Cytoscape, or web tools.

```python
from api.sfm_service import SFMService
from models import Node
from graph.sfm_graph import Relationship

service = SFMService()

# Build a network
node1 = Node(label="Institution A")
node2 = Node(label="Institution B")
node3 = Node(label="Institution C")

service.create_node(node1)
service.create_node(node2)
service.create_node(node3)

rel1 = Relationship(source_id=node1.id, target_id=node2.id, kind="influences")
rel2 = Relationship(source_id=node2.id, target_id=node3.id, kind="influences")
service.create_relationship(rel1)
service.create_relationship(rel2)

# Export for Gephi visualization
service.export_snapshot(
    "/home/user/visualizations/network.graphml",
    export_format="graphml"
)

# Export for web-based visualization
service.export_snapshot(
    "/home/user/visualizations/network.gexf",
    export_format="gexf"
)

# Export to JSON for custom processing
service.export_snapshot(
    "/home/user/data/network_snapshot.json",
    export_format="json"
)

print("Exported to 3 formats for external analysis")
```

---

### 5. Backup and Version Control

Maintain historical versions of your analysis.

```python
from api.sfm_service import SFMService
from models import Node
from datetime import datetime

service = SFMService()

# Build initial version
service.create_node(Node(label="v1 Node"))
service.save("analysis_v1.json")

# Make updates
service.create_node(Node(label="v2 Node"))

# Save with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
service.save(f"analysis_v2_{timestamp}.json")

# Later: Review different versions
service_v1 = SFMService()
service_v1.load("analysis_v1.json")

service_v2 = SFMService()
service_v2.load(f"analysis_v2_{timestamp}.json")

print(f"v1 nodes: {len(service_v1.list_nodes())}")
print(f"v2 nodes: {len(service_v2.list_nodes())}")
```

---

### 6. Data Migration

Transfer graphs between environments or update storage formats.

```python
from api.sfm_service import SFMService

# Development environment: Save as compressed
dev_service = SFMService()
# ... build graph ...
dev_service.save("dev_graph.json.gz", format_type="json.gz")

# Production environment: Load and convert
prod_service = SFMService()
prod_service.load("dev_graph.json.gz", format_type="json.gz")

# Save in production format
prod_service.save("prod_graph.json", format_type="json")

print("Migrated from compressed to standard JSON")
```

---

## Versioned Persistence (Time Travel + Branching)

Versioned persistence stores graph snapshots in `./.sfm_versions/` with:

- SQLite metadata index (`versions.db`)
- Content-addressed snapshot objects (`objects/<sha256>`)
- Branch, tag, and `HEAD` refs (`refs/`)

```python
from api.sfm_service import SFMService
from models import Node

service = SFMService()
service.create_node(Node(label="Baseline"))
service.commit("Initial baseline", tags=["baseline"])

service.create_branch("hypothesis-1")
service.create_node(Node(label="Alternative institution"))
service.commit("Test alternative structure")

service.checkout("baseline")   # tag checkout
service.checkout("HEAD~1")     # time-travel checkout

history = service.list_versions(branch="main", limit=10)
diff = service.diff_versions("baseline", "hypothesis-1")
print(diff["nodes_added"])

service.merge_branch("hypothesis-1", strategy="manual")
print(service.show_history(format="text"))
```

### Versioned API Methods

- `commit(message, tags=None)`
- `checkout(version_ref)`
- `list_versions(branch="main", limit=20)`
- `diff_versions(version1, version2)`
- `create_branch(branch_name, from_version=None)`
- `merge_branch(branch_name, strategy="manual")`
- `show_history(format="text")`

---

## API Reference

### SFMService Persistence Methods

All persistence operations are available through the `SFMService` class.

#### save()
```python
def save(
    filename: str,
    format_type: str = "json",
    base_path: str = "./sfm_data"
) -> Dict[str, Any]
```

#### load()
```python
def load(
    filename: str,
    format_type: str = "json",
    base_path: str = "./sfm_data",
    replace: bool = True,
    allow_pickle: bool = False
) -> Dict[str, Any]
```

#### reload()
```python
def reload(
    filename: str,
    format_type: str = "json",
    base_path: str = "./sfm_data"
) -> Dict[str, Any]
```

#### unload()
```python
def unload() -> Dict[str, Any]
```

#### export_snapshot()
```python
def export_snapshot(
    filepath: str,
    export_format: str = "json"
) -> Dict[str, Any]
```

#### import_snapshot()
```python
def import_snapshot(
    filepath: str
) -> Dict[str, Any]
```

---

### Storage Format Constants

Available through `graph.sfm_persistence.StorageFormat`:

```python
from graph.sfm_persistence import StorageFormat

StorageFormat.JSON              # "json"
StorageFormat.COMPRESSED_JSON   # "json.gz"
StorageFormat.PICKLE            # "pickle"
StorageFormat.COMPRESSED_PICKLE # "pickle.gz"
```

---

### Error Handling

```python
from api.sfm_service import SFMService
from graph.sfm_persistence import SFMPersistenceError, SFMSerializationError

service = SFMService()

try:
    service.load("nonexistent.json")
except SFMPersistenceError as e:
    print(f"File not found: {e}")

try:
    service.load("corrupt.json")
except SFMSerializationError as e:
    print(f"Invalid file format: {e}")

try:
    service.load("untrusted.pickle", format_type="pickle", allow_pickle=False)
except SFMSerializationError as e:
    print(f"Pickle security error: {e}")
```

---

## Implementation Details

### File Storage Location

Default storage directory: `./sfm_data/` (relative to current working directory)

```python
# Default location
service.save("graph.json")  # Saves to ./sfm_data/graph.json

# Custom location
service.save("graph.json", base_path="/home/user/sfm_graphs")
# Saves to /home/user/sfm_graphs/graph.json
```

### Supported Node Types

All 33 Beta unified model node types plus delivery matrix and temporal types:

- Base: `Node`
- Cultural: `InformalNorm`, `CeremonialInstrumentalClassification`, `ValueSystem`, `SocialBelief`, `CulturalAttitude`
- System: `SystemProperty`, `SystemLevelAnalysis`, `InstitutionalHolarchy`, `InstitutionalStructure`
- Matrix: `MatrixCell`, `SFMCriteria`, `SFMMatrix`
- Policy: `PolicyInstrument`, `ValueJudgment`, `ProblemSolvingSequence`
- Coordination: `TransactionCost`, `CoordinationMechanism`, `CommonsGovernance`
- Analysis: `PathDependencyAnalysis`, `CrossImpactAnalysis`, `DigraphAnalysis`, `ConflictDetection`
- Delivery: `Delivery`, `SFMDeliveryCell`, `SFMDeliveryMatrix`, `DeliveryRelationship`, `MatrixDeliveryNetwork`
- Assessment: `SocialValueAssessment`, `SocialFabricIndicator`, `SocialCost`, `SocialIndicatorSystem`
- Integration: `InstrumentalistInquiryFramework`, `NormativeSystemsAnalysis`, `PolicyRelevanceIntegration`, `DatabaseIntegrationCapability`
- Evolution: `EvolutionaryPathway`, `CircularCausationProcess`
- Provisioning: `SocialProvisioningMatrix`, `ToolSkillTechnologyComplex`, `EcologicalSystem`
- Scenario: `Scenario`, `ScenarioPath`, `ScenarioSet`, `Event`
- Temporal: `TemporalClock`, `TemporalPhase`

### Metadata Tracking

Saved graphs include comprehensive metadata:

```python
{
    "graph_id": "unique-uuid",
    "name": "SFM Graph",
    "description": "",
    "version": 1,
    "created_at": "2026-06-22T10:00:00",
    "modified_at": "2026-06-22T10:30:00",
    "node_count": 42,
    "relationship_count": 15,
    "checksum": "sha256-hash",
    "format": "json"
}
```

---

## See Also

- **[SFM Graph API](API_REFERENCE.md)** - Complete API documentation
- **[Beta Unified Model](BETA_MODEL.md)** - Node types and relationships
- **[Delivery Matrix Guide](DELIVERY_MATRIX.md)** - Hayden-compliant delivery matrices
- **[Test Examples](../tests/test_api/test_persistence.py)** - Comprehensive test suite

---

## Questions or Issues?

For bug reports or feature requests, please file an issue in the repository issue tracker.
