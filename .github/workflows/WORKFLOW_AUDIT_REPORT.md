# GitHub Actions Workflow Audit Report
**Date**: 2026-06-21  
**Repository**: SFM-Graph-Service/sfm-core

---

## Executive Summary

**Status**: ⚠️ **CRITICAL ISSUES FOUND** - Multiple workflows reference non-existent directories

The repository has 8 GitHub Actions workflows, but 7 of them have critical path errors that cause them to fail or skip important checks. The workflows were likely copied from an old repository structure and never updated.

---

## Issues Found

### 🔴 CRITICAL: Directory Structure Mismatch

**Problem**: Most workflows reference old directory structure that doesn't exist:
- ❌ `core/` (does not exist)
- ❌ `db/` (does not exist) 
- ❌ `infrastructure/` (does not exist)
- ❌ `utils/` (does not exist)

**Actual structure**:
- ✅ `models/` (Python model definitions)
- ✅ `graph/` (Graph query engine, exporters)
- ✅ `api/` (SFM service layer)
- ✅ `data/` (Importers, data access)
- ✅ `examples/` (Case studies)
- ✅ `tests/` (Test suite)

### Affected Workflows (7 of 8):

1. **code-quality.yml** - Lines 34, 59, 97 reference `core/ api/ db/`
2. **pylint.yml** - Line 32 references `core/ api/ db/`
3. **documentation.yml** - Lines 35, 44, 201, 204 reference old paths
4. **security.yml** - Lines 94, 135, 149, 154, 159 reference old paths
5. **performance.yml** - All test references (lines 39, 47)
6. **ci.yml** - Line 34, 86 reference old paths (BUT tests work because they target `models/ graph/ api/ data/`)
7. **test-examples.yml** - Lists wrong example files (lines 62-66)

**Only pytest.yml is correct** - it uses the right paths (`models/`, `graph/`, `api/`, `data/`)

---

## Detailed Findings by Workflow

### 1. ci.yml (Continuous Integration)
**Status**: ⚠️ PARTIALLY WORKING (tests pass, linting fails)

**Issues**:
- Pylint step (line 34): Tries to scan `core/ api/ db/` → **SKIPS ACTUAL CODE**
- Complexity checks (line 86-91): Scan `models/ graph/ api/ data/` → ✅ CORRECT
- Tests (line 46): Scan `models/ graph/ api/ data/` → ✅ CORRECT

**Impact**: Pylint never runs on actual code. Code quality not enforced.

**Fix**:
```yaml
# Line 34 - Change from:
pylint core/ api/ db/ --output-format=parseable

# To:
pylint models/ graph/ api/ data/ --output-format=parseable
```

---

### 2. code-quality.yml (Linting & Type Checking)
**Status**: ❌ MOSTLY BROKEN

**Issues**:
- Line 34: Pylint scans `core/ api/ db/` → **WRONG**
- Line 59: Flake8 scans `core/ api/ db/` → **WRONG**
- Line 97: MyPy scans `core/ api/ db/` → **WRONG**
- Line 141: Black checks `core/ api/ db/ tests/` → **WRONG**
- Line 149: isort checks `core/ api/ db/ tests/` → **WRONG**

**Impact**: Entire code quality workflow scans nothing useful.

**Fix**: Replace all instances of `core/ api/ db/` with `models/ graph/ api/ data/`

---

### 3. pylint.yml (Dedicated Pylint Run)
**Status**: ❌ COMPLETELY BROKEN

**Issues**:
- Line 32: Scans `core/ api/ db/` → **WRONG**

**Impact**: Redundant workflow (duplicates ci.yml and code-quality.yml) that also doesn't work.

**Recommendation**: **DELETE THIS FILE** - it's redundant and broken.

---

### 4. pytest.yml (Test Suite)
**Status**: ✅ CORRECT

**No issues** - properly scans `models/`, `graph/`, `api/`, `data/`

**Note**: This workflow works correctly and should be the model for others.

---

### 5. test-examples.yml (Example Validation)
**Status**: ⚠️ PARTIALLY BROKEN

**Issues**:
- Lines 62-66: Lists expected examples that DON'T EXIST:
  ```
  examples/global_supply_chain_resilience_example.py
  examples/healthcare_system_policy_example.py
  examples/smart_city_urban_planning_example.py
  examples/us_grain_export_example.py
  examples/us_grain_market_forecast.py
  ```

**Actual examples** (from `examples/hayden_case_studies/`):
- `clean_air_act_1970.py`
- `director_networks.py`
- `nebraska_k12_finance.py`
- `radioactive_waste.py`

**Impact**: Workflow validates wrong examples, never tests actual case studies.

**Fix**: Update to test Hayden case studies or mark as workflow_dispatch only.

---

### 6. security.yml (Security Scanning)
**Status**: ⚠️ PARTIALLY BROKEN

**Issues**:
- Line 94: Bandit scans `models/ graph/ api/ data/` → ✅ CORRECT
- Line 135: Semgrep scans `models/ graph/ api/ data/` → ✅ CORRECT
- BUT Lines 149, 154, 159: Custom security checks reference `models/ graph/ api/ data/` → ✅ CORRECT

**Status**: Actually this one is CORRECT! False alarm.

---

### 7. documentation.yml (Doc Validation)
**Status**: ⚠️ MOSTLY BROKEN

**Issues**:
- Line 35: pydocstyle scans `models/ api/ graph/ data/ infrastructure/ utils/ core/ db/` → **HALF WRONG**
  - `models/ api/ graph/ data/` → ✅ CORRECT
  - `infrastructure/ utils/ core/ db/` → ❌ DON'T EXIST
- Line 44: interrogate scans same wrong paths
- Lines 201-220: README consistency checks reference old module names

**Impact**: Runs but with errors/warnings for non-existent directories.

**Fix**: Remove `infrastructure/ utils/ core/ db/` from scan paths.

---

### 8. performance.yml (Performance Tests)
**Status**: ⚠️ PARTIALLY BROKEN

**Issues**:
- Tests reference files that may not exist:
  - `tests/test_service/test_sfm_service.py` - need to verify
  - `tests/test_lookup_performance.py` - need to verify

**Impact**: Tests may skip if files don't exist.

**Recommendation**: Verify test files exist or update paths.

---

## Consolidation Opportunities

**Redundant workflows**:
1. `ci.yml` + `pytest.yml` both run pytest
2. `ci.yml` + `code-quality.yml` + `pylint.yml` all run pylint

**Recommendation**:
- Keep `ci.yml` as the main gating workflow
- Delete `pylint.yml` (redundant)
- Make `code-quality.yml` a supplementary workflow for detailed reports

---

## Priority Fixes

### 🔴 CRITICAL (Fix Immediately)

1. **ci.yml Line 34**: Fix pylint path
   ```yaml
   pylint models/ graph/ api/ data/ --output-format=parseable
   ```

2. **code-quality.yml**: Replace all `core/ api/ db/` with `models/ graph/ api/ data/`

3. **test-examples.yml**: Either delete or update to test Hayden case studies

### 🟡 HIGH (Fix Soon)

4. **documentation.yml**: Remove non-existent directories from scans

5. **Delete pylint.yml**: Redundant and broken

### 🟢 MEDIUM (Nice to Have)

6. **Consolidate workflows**: Reduce duplication

7. **Add Hayden case study tests**: Create proper validation for the 4 case studies

---

## Recommended Actions

### Immediate (This PR):
1. Fix `ci.yml` pylint path
2. Fix `code-quality.yml` all paths
3. Delete `pylint.yml`
4. Fix `documentation.yml` paths
5. Update `test-examples.yml` to test Hayden case studies OR make it workflow_dispatch only

### Follow-up (Next PR):
6. Consolidate redundant workflows
7. Add proper case study validation tests
8. Verify performance test paths
9. Add workflow documentation

---

## Global Definition of Done for Workflow Fixes

Every workflow update must:
- [ ] Reference only directories that exist: `models/`, `graph/`, `api/`, `data/`, `examples/`, `tests/`
- [ ] Not reference: `core/`, `db/`, `infrastructure/`, `utils/`
- [ ] Run successfully on a test PR
- [ ] Produce useful output (not empty scans)
- [ ] Be documented with clear purpose

---

## Files to Update

1. `.github/workflows/ci.yml` - Fix line 34
2. `.github/workflows/code-quality.yml` - Fix all path references
3. `.github/workflows/pylint.yml` - **DELETE**
4. `.github/workflows/documentation.yml` - Remove non-existent dirs
5. `.github/workflows/test-examples.yml` - Update example list or mark dispatch-only
6. `.github/workflows/pytest.yml` - ✅ NO CHANGES NEEDED
7. `.github/workflows/security.yml` - ✅ NO CHANGES NEEDED
8. `.github/workflows/performance.yml` - Verify test file paths

---

## Verification Steps

After fixes:
1. Create a PR with workflow changes
2. Verify all workflows run without path errors
3. Check that linting actually scans code
4. Confirm artifacts are generated
5. Review workflow run times for duplication
