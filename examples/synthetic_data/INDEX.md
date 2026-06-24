# Synthetic Data Directory - File Index

Complete guide to all files in the synthetic_data directory.

## Data Files (Generated)

### climate_network.json (3.5 MB)
**Main dataset in SFM-Core format**
- 1,056 institutional nodes
- 6,363 relationships
- Complete metadata and statistics
- Ready to load in Python/JavaScript

**Usage:**
```python
import json
with open('climate_network.json', 'r') as f:
    data = json.load(f)
```

### climate_network.gexf (1.2 MB)
**GEXF format for Gephi visualization**
- Same network structure
- Optimized for graph visualization tools
- Node attributes included
- Edge weights preserved

**Usage:**
- Open in Gephi (File → Open)
- Import into Cytoscape
- Use with NetworkX GEXF parser

## Source Code

### generate_large_network.py (95 KB)
**Main generator script**
- Creates 1000+ node network
- Configurable seed for reproducibility
- Well-documented class structure
- Extensible for custom scenarios

**Key Features:**
- 25 institutional categories
- 20+ relationship types
- Realistic metadata generation
- Ceremonial/instrumental modeling
- Geographic distribution
- Temporal validity periods

**Run:**
```bash
python generate_large_network.py
```

**Customize:**
- Edit seed: `ClimateNetworkGenerator(seed=123)`
- Reduce scale: Slice institution lists
- Change scenario: Modify institution names
- Add categories: Define new generator methods

### validate_network.py (6.3 KB)
**Data validation script**
- Checks node/relationship uniqueness
- Validates required fields
- Verifies score ranges (0-1)
- Tests reference integrity
- Reports statistics

**Run:**
```bash
python validate_network.py
```

**Exit codes:**
- 0: All checks passed
- 1: Validation failed

### example_analysis.py (8.1 KB)
**Demonstration queries**
- 8 complete analysis examples
- Shows common query patterns
- Demonstrates network analysis
- Illustrates data access methods

**Run:**
```bash
python example_analysis.py
```

**Examples included:**
1. Funding flow analysis
2. Regulatory chain tracing
3. Geographic distribution
4. Ceremonial/instrumental patterns
5. Network centrality
6. Technology deployment
7. Policy implementation
8. Collaboration patterns

## Documentation

### README.md (14 KB)
**Comprehensive documentation**
- Dataset composition tables
- Generation instructions
- Loading examples
- Query cookbook (7+ examples)
- Gephi visualization guide
- Customization instructions
- Use case descriptions

**Topics covered:**
- Node categories and counts
- Relationship types
- Metadata structure
- Example queries
- Extension guide
- FAQ section

### DATASET_SUMMARY.md (7.9 KB)
**High-level dataset overview**
- Quick statistics
- Node composition breakdown
- Relationship distribution
- Network characteristics
- Validation results
- Realism features
- Use cases
- Limitations

**Best for:**
- Quick reference
- Dataset citation
- Understanding scope
- Assessing fitness for purpose

### QUICKSTART.md (4.4 KB)
**5-minute getting started guide**
- Step-by-step instructions
- Copy-paste code examples
- Common queries
- Troubleshooting tips
- Next steps

**Best for:**
- First-time users
- Quick demos
- Teaching/training
- Testing integration

### INDEX.md (This file)
**File directory and usage guide**
- What each file does
- When to use which file
- Quick reference
- Workflow suggestions

## Workflows

### First Time Setup
1. Read `QUICKSTART.md`
2. Run `generate_large_network.py`
3. Run `validate_network.py`
4. Run `example_analysis.py`

### Development Workflow
1. Modify `generate_large_network.py`
2. Regenerate data
3. Validate changes
4. Test with example queries
5. Update documentation

### Research Workflow
1. Read `DATASET_SUMMARY.md` for overview
2. Read `README.md` for details
3. Load data in analysis environment
4. Adapt examples from `example_analysis.py`
5. Build custom queries

### Visualization Workflow
1. Generate or use existing `climate_network.gexf`
2. Open in Gephi
3. Apply layouts (Force Atlas 2)
4. Calculate statistics (Modularity, Degree)
5. Style by attributes (category, scores)
6. Export visualizations

### Teaching Workflow
1. Use `QUICKSTART.md` as handout
2. Demo `example_analysis.py`
3. Load data in Gephi for visualization
4. Reference `README.md` for query examples
5. Assign custom analysis tasks

## File Dependencies

```
generate_large_network.py  (no dependencies - standalone)
    ↓ generates
climate_network.json
climate_network.gexf
    ↓ used by
validate_network.py  (requires climate_network.json)
example_analysis.py  (requires climate_network.json)
    ↓ documented in
README.md
DATASET_SUMMARY.md
QUICKSTART.md
INDEX.md (this file)
```

## Quick Commands

```bash
# Generate dataset
python generate_large_network.py

# Validate
python validate_network.py

# Analyze
python example_analysis.py

# Make scripts executable
chmod +x *.py

# Clean generated files
rm -f climate_network.json climate_network.gexf

# Regenerate everything
python generate_large_network.py && python validate_network.py

# File sizes
ls -lh

# Checksums
sha256sum *.json *.gexf

# Count lines of code
wc -l *.py
```

## Support Resources

**Getting started:**
→ `QUICKSTART.md`

**Understanding the data:**
→ `DATASET_SUMMARY.md`

**Detailed usage:**
→ `README.md`

**Code examples:**
→ `example_analysis.py`

**Customization:**
→ `generate_large_network.py` (well-commented)

**Troubleshooting:**
→ `QUICKSTART.md` (troubleshooting section)
→ `README.md` (FAQ)

**Data validation:**
→ `validate_network.py`

**This index:**
→ `INDEX.md`

## Version Information

**Dataset Version:** 1.0  
**Generator Version:** 1.0  
**Generated:** 2026-06-24  
**Python:** 3.8+ (no external dependencies)  
**Format:** JSON (primary), GEXF (secondary)  
**Encoding:** UTF-8  
**Random Seed:** 42 (for reproducibility)

## License & Citation

**Usage:** Free for research, education, and development  
**Type:** Synthetic/demonstration data  
**Not for:** Production policy analysis (fictional relationships)

**Cite as:**
```
Synthetic National Climate Policy Network (2025-2035)
SFM-Core Framework Demonstration Dataset
1,056 nodes, 6,363 relationships
Generated: 2026-06-24
```

## Updates & Maintenance

**Regenerate dataset:**
```bash
python generate_large_network.py
```
(Same output with seed=42)

**Change scenario:**
1. Edit institution lists in generator
2. Modify relationship logic
3. Regenerate and validate

**Add categories:**
1. Create `generate_X` method
2. Call in `generate_network()`
3. Add relationships in `_add_complex_relationships()`
4. Update documentation

**Report issues:**
- Data problems: Check validation first
- Generator bugs: Include reproducible example
- Documentation gaps: Specify which file needs update

---

**Status:** ✓ Complete | ✓ Validated | ✓ Ready for use  
**Last updated:** 2026-06-24
