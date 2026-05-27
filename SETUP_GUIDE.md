# SFM Core Setup Guide

Complete setup instructions for different deployment scenarios.

**Note**: This is research software under active development. Claude AI was used to assist with documentation. Verify all steps for your specific environment.

---

## Table of Contents

1. [Quick Start (Local Development)](#quick-start-local-development)
2. [Dev Container Setup (VS Code)](#dev-container-setup-vs-code)
3. [Docker Standalone Deployment](#docker-standalone-deployment)
4. [Running Examples](#running-examples)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.10 or higher
- pip and venv
- graphviz (optional, for visualization)

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/SFM-Graph-Service/sfm-core.git
cd sfm-core

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install package in development mode
pip install -e .

# 5. Verify installation
python -c "from api.sfm_service import SFMService; print('✓ Installation successful')"
```

### Validation

Run the setup validation script:

```bash
./test_setup.sh
```

Expected output:
```
✓ All critical tests passed
```

### Run Examples

```bash
# Nebraska K-12 Education Finance
python examples/hayden_case_studies/nebraska_k12_finance.py

# Low-Level Radioactive Waste Policy
python examples/hayden_case_studies/radioactive_waste.py

# Corporate Director Networks
python examples/hayden_case_studies/director_networks.py

# Clean Air Act 1970
python examples/hayden_case_studies/clean_air_act_1970.py
```

Examples generate `.xlsx` files in the `examples/hayden_case_studies/` directory.

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_delivery_matrix_fidelity.py

# Run with coverage
pytest --cov=. --cov-report=html tests/
```

---

## Dev Container Setup (VS Code)

### Prerequisites

- Docker Desktop
- Visual Studio Code
- Dev Containers extension (ms-vscode-remote.remote-containers)

### Steps

1. **Open in Container**
   ```
   File → Open Folder → sfm-core/
   VS Code will detect .devcontainer/devcontainer.json
   Click "Reopen in Container" when prompted
   ```

2. **Wait for Setup**
   - Container builds automatically
   - Dependencies install via `postCreateCommand`
   - Extensions install automatically

3. **Verify Setup**
   ```bash
   # In VS Code terminal
   python -c "from api.sfm_service import SFMService; print('✓ OK')"
   ```

4. **Run Examples**
   ```bash
   python examples/hayden_case_studies/nebraska_k12_finance.py
   ```

### Dev Container Features

- **Port Forwarding**: 8000 (API), 7474 (Neo4j), 7687 (Bolt), 3000 (frontend)
- **Extensions**: Python, Pylance, Docker, ESLint, Prettier
- **System Tools**: graphviz, curl pre-installed

---

## Docker Standalone Deployment

### Prerequisites

- Docker
- docker-compose (or Docker Compose plugin)

### Option 1: Build and Run (NetworkX Backend)

```bash
# Build image
docker build -t sfm-core .

# Run container
docker run -d \
  --name sfm-core \
  -p 8000:8000 \
  -e STORAGE_TYPE=networkx \
  sfm-core

# Verify API
curl http://localhost:8000/api/v1/health
```

### Option 2: Docker Compose (Development)

```bash
# Start API with NetworkX backend
docker-compose up api-dev

# Access API documentation
open http://localhost:8000/docs
```

### Option 3: Docker Compose (Production with Neo4j)

```bash
# Start Neo4j and API
docker-compose up neo4j api-neo4j

# Access points:
# - API: http://localhost:8001
# - Neo4j Browser: http://localhost:7474 (user: neo4j, pass: neo4j_password)
```

### Validation

Run container deployment tests:

```bash
./test_container_deployment.sh
```

Expected output:
```
✓ All container tests passed
```

---

## Running Examples

### Example Files

All examples are in `examples/hayden_case_studies/`:

1. **nebraska_k12_finance.py** - State education funding (Hoffman & Hayden 2007)
2. **radioactive_waste.py** - Interstate waste compact (Hayden & Bolduc 2000)
3. **director_networks.py** - Corporate interlocks (Hayden, Wood & Kaya 2002)
4. **clean_air_act_1970.py** - Environmental policy (demonstration)

### Running Examples Locally

```bash
# Must run from repository root
python examples/hayden_case_studies/<example_name>.py
```

### Running Examples in Container

```bash
docker run --rm \
  -v $(pwd)/examples:/app/examples \
  sfm-core \
  python examples/hayden_case_studies/nebraska_k12_finance.py
```

### Output Files

Examples generate Excel files (`.xlsx`) with three sheets:

1. **Matrix View** - N×N delivery matrix
2. **Cell Descriptions** - Narrative descriptions (Hayden methodology)
3. **Delivery Details** - Tabular delivery data

Open in Excel, LibreOffice, or Python:

```python
import pandas as pd
df = pd.read_excel('nebraska_k12_finance.xlsx', sheet_name='Delivery Details')
print(df.head())
```

---

## Troubleshooting

### Common Issues

#### 1. Import Error: `No module named 'api'`

**Cause**: Package not installed in editable mode

**Solution**:
```bash
pip install -e .
```

#### 2. Docker Build Fails

**Cause**: Outdated Docker or insufficient memory

**Solution**:
```bash
# Update Docker
# Increase Docker memory to 4GB in Docker Desktop settings

# Clean build
docker build --no-cache -t sfm-core .
```

#### 3. Permission Denied: `test_setup.sh`

**Cause**: Script not executable

**Solution**:
```bash
chmod +x test_setup.sh
chmod +x test_container_deployment.sh
```

#### 4. Port Already in Use (8000, 7474, 7687)

**Cause**: Another service using ports

**Solution**:
```bash
# Check what's using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Stop conflicting service or change ports in docker-compose.yml
```

#### 5. GraphViz Not Found

**Cause**: Optional dependency not installed

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Windows
choco install graphviz
```

#### 6. Tests Fail with Neo4j Connection Error

**Cause**: Neo4j not running or wrong credentials

**Solution**:
```bash
# Start Neo4j
docker-compose up neo4j

# Wait for healthy status
docker-compose ps

# Verify connection
docker exec -it <neo4j_container> cypher-shell -u neo4j -p neo4j_password
```

### Getting Help

1. Check logs:
   ```bash
   # Docker logs
   docker logs <container_id>
   
   # Docker compose logs
   docker-compose logs api-dev
   ```

2. Run validation scripts:
   ```bash
   ./test_setup.sh
   ./test_container_deployment.sh
   ```

3. Check GitHub issues:
   https://github.com/SFM-Graph-Service/sfm-core/issues

---

## Next Steps

After successful setup:

1. **Explore Documentation**
   - [Hayden SFM Guide](docs/hayden_sfm_guide.md)
   - [Analysis Methods](docs/ANALYSIS_METHODS_GUIDE.md)
   - [API Documentation](http://localhost:8000/docs)

2. **Run Examples**
   - Study Nebraska K-12 finance example
   - Modify examples for your research

3. **Build Custom Matrices**
   ```python
   from api.sfm_service import SFMService
   from models.delivery_matrix import Delivery, SFMDeliveryMatrix
   
   service = SFMService()
   # Your code here
   ```

4. **Contribute**
   - Report issues on GitHub
   - Submit pull requests
   - Share use cases

---

*Last updated: 2026-05-27*
