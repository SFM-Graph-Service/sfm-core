# Pylance/Pyright Configuration Guide

This document describes the Pylance type checking configuration for the SFM Core project.

## Configuration Files

### 1. `pyrightconfig.json`
The main configuration file for Pylance/Pyright type checking. This file is used by:
- VS Code Pylance extension
- Pyright CLI tool
- CI/CD pipelines

**Key Settings:**
- **Type Checking Mode**: `standard` (balanced strictness)
- **Python Version**: 3.14
- **Included Directories**: `models/`, `graph/`, `data/`, `api/`
- **Excluded Directories**: Tests, build artifacts, virtual environments

### 2. `.vscode/settings.json`
VS Code workspace settings that configure the Python extension and Pylance.

**Key Settings:**
- Python interpreter path points to `.venv/bin/python`
- Type checking mode set to `standard`
- Custom diagnostic severity overrides for common false positives
- Integration with pytest and pylint

## Type Checking Configuration

### Strictness Level: Standard

The project uses `"typeCheckingMode": "standard"` which provides:
- ✅ Error detection for common type issues
- ✅ Optional type checking (None checks)
- ✅ Type compatibility verification
- ❌ Doesn't require type annotations everywhere (unlike strict mode)

### Disabled Checks

The following checks are disabled because they produce false positives or are too strict for this project:

| Check | Reason |
|-------|--------|
| `reportMissingTypeStubs` | Many third-party libraries lack stubs |
| `reportUnknownMemberType` | Dataclasses generate members dynamically |
| `reportUnknownVariableType` | Inference is sufficient in many cases |
| `reportUntypedFunctionDecorator` | Pydantic/dataclass decorators are safe |
| `reportInvalidTypeForm` | False positives with TYPE_CHECKING guards |
| `reportArgumentType` | False positives with Neo4j LiteralString |
| `reportUnusedClass/Function` | Many utilities are legitimately unused in current phase |

### Enabled Checks (Errors)

The following checks remain as errors:

| Check | Purpose |
|-------|---------|
| `reportMissingImports` | Catch import errors early |
| `reportDuplicateImport` | Code quality |
| `reportOptionalSubscript` | Prevent None access errors |
| `reportOptionalMemberAccess` | Prevent None attribute errors |
| `reportOptionalCall` | Prevent calling None |
| `reportIncompatibleMethodOverride` | Ensure proper inheritance |
| `reportUndefinedVariable` | Catch typos and undefined names |
| `reportUnboundVariable` | Prevent use-before-assignment |
| `reportUnusedCoroutine` | Catch async/await mistakes |

## Running Type Checks

### In VS Code
Type checking runs automatically as you edit. Look for:
- **Red squiggles**: Errors that must be fixed
- **Yellow squiggles**: Warnings (can be suppressed if false positive)
- **Blue squiggles**: Informational hints

### From Command Line

```bash
# Activate virtual environment
source .venv/bin/activate

# Run pyright
pyright

# Run pyright on specific files
pyright models/ graph/

# Output JSON for CI
pyright --outputjson
```

### With Mypy (Alternative)

The project also supports mypy:

```bash
source .venv/bin/activate
mypy models/ graph/ data/ api/ --check-untyped-defs
```

## Common Type Issues and Fixes

### Issue: Optional Type Errors

```python
# ❌ Error: Object of type "None" is not subscriptable
result = tx.run(query)
return result.single()[0]

# ✅ Fix: Check for None first
result = tx.run(query)
record = result.single()
return record[0] if record else None
```

### Issue: TYPE_CHECKING Imports

```python
# ❌ Error: Variable not allowed in type expression
from neo4j import ManagedTransaction

def my_func(tx: ManagedTransaction):
    pass

# ✅ Fix: Use TYPE_CHECKING guard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neo4j import ManagedTransaction

def my_func(tx: "ManagedTransaction"):  # String literal or just use TYPE_CHECKING
    pass
```

### Issue: Enum Value Access

```python
# ❌ Error: Cannot access attribute "value" for class "str"
value = rel.kind.value

# ✅ Fix: Type guard
from enum import Enum

if isinstance(rel.kind, Enum):
    value = rel.kind.value
else:
    value = rel.kind
```

## Suppressing False Positives

### Inline Suppressions

```python
# Suppress on specific line
result = dangerous_call()  # type: ignore[reportOptionalCall]

# Suppress entire function
# pyright: reportOptionalMemberAccess=false
def my_function():
    pass
```

### Configuration Suppressions

Add to `pyrightconfig.json`:

```json
{
  "reportSpecificCheck": "none"
}
```

## Integration with Other Tools

### Pylint

Pylint runs separately and checks for code quality issues. Configure via `.pylintrc`.

```bash
pylint models/ graph/ data/ api/ --rcfile=.pylintrc
```

### Mypy

Mypy is an alternative type checker. Configure via `mypy.ini`.

```bash
mypy models/ graph/ data/ api/ --check-untyped-defs
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/RobertCraigie/pyright-python
  rev: v1.1.409
  hooks:
    - id: pyright
```

## Troubleshooting

### Still seeing `reportUnknownVariableType` errors

If you see this error even though it's disabled in the config:

1. **Restart Pylance Language Server:**
   - `Ctrl+Shift+P` → "Python: Restart Language Server"
   
2. **Reload VS Code Window:**
   - `Ctrl+Shift+P` → "Developer: Reload Window"
   
3. **Check for user settings override:**
   - Open Command Palette: `Ctrl+Shift+P`
   - Select "Preferences: Open User Settings (JSON)"
   - Look for `python.analysis.diagnosticSeverityOverrides`
   - If present, ensure it doesn't override workspace settings
   
4. **Verify workspace settings are active:**
   - Bottom right of VS Code should show the Python interpreter from `.venv`
   - Click on it to ensure the correct interpreter is selected
   
5. **Clear Pylance cache:**
   ```bash
   rm -rf ~/.cache/pylance
   ```
   Then reload VS Code

6. **Add explicit type annotation:**
   If the error persists on a specific line, add an explicit type annotation:
   ```python
   # Instead of:
   oldest_key = next(iter(self._relationship_cache))
   
   # Use:
   oldest_key: uuid.UUID = next(iter(self._relationship_cache))
   ```

### Pylance shows errors but pyright doesn't

1. Reload VS Code window: `Ctrl+Shift+P` → "Reload Window"
2. Check Python interpreter: Should be `.venv/bin/python`
3. Verify pyrightconfig.json is being loaded
4. Restart the Pylance language server

### Type stubs not found

Some libraries don't have type stubs. Install them:

```bash
pip install types-networkx types-requests
```

Or suppress the warning in pyrightconfig.json:

```json
{
  "reportMissingTypeStubs": "none"
}
```

### Performance issues

If Pylance is slow:

1. Exclude more directories in pyrightconfig.json
2. Reduce `typeCheckingMode` from `standard` to `basic`
3. Disable indexing: `"indexing": false`

## CI/CD Integration

Add to GitHub Actions workflow:

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install pyright
    pip install -r requirements.txt

- name: Run Pyright
  run: pyright
```

## Version Information

- **Pyright**: 1.1.409
- **Python**: 3.14.4
- **Pylance**: Latest (bundled with VS Code Python extension)

## References

- [Pyright Documentation](https://github.com/microsoft/pyright)
- [Pylance Documentation](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [Type Checking Best Practices](https://github.com/microsoft/pyright/blob/main/docs/type-concepts.md)
