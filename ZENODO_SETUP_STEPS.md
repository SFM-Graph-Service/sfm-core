# Zenodo DOI Setup for sfm-core

## Step 1: Create Zenodo Account
1. Go to https://zenodo.org/
2. Click "Sign up" (top right)
3. **Use GitHub login** (recommended - enables auto-sync)
4. Authorize Zenodo to access your GitHub repos

## Step 2: Enable GitHub Integration
1. After login, go to https://zenodo.org/account/settings/github/
2. Find `SFM-Graph-Service/sfm-core` in the repository list
3. Toggle the switch to **ON** to enable archiving
4. This creates automatic DOI assignment on each GitHub release

## Step 3: Create First Release on GitHub
1. Go to https://github.com/SFM-Graph-Service/sfm-core/releases
2. Click "Create a new release"
3. Tag version: `v0.1.0`
4. Release title: `SFM Core v0.1.0 - Initial Release`
5. Description: Copy from CHANGELOG.md highlights
6. Attach built packages (optional):
   - `sfm_core-0.1.0-py3-none-any.whl`
   - `sfm_core-0.1.0.tar.gz`
7. Click "Publish release"

## Step 4: Zenodo Auto-Archives Release
Within 5-10 minutes after GitHub release:
- Zenodo automatically creates archive snapshot
- Assigns DOI (format: `10.5281/zenodo.XXXXXXX`)
- Creates permanent landing page

## Step 5: Update Citation Files with DOI
Once DOI is assigned, update:

### CITATION.cff
Add after line 8 (after `type: software`):
```yaml
doi: 10.5281/zenodo.XXXXXXX
```

### README.md
Update citation section (around line 705):
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

### CONTRIBUTORS.md
Update line 125:
```markdown
**Zenodo DOI:** [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

## Step 6: Verify DOI Landing Page
1. Visit `https://doi.org/10.5281/zenodo.XXXXXXX`
2. Verify metadata is correct:
   - Title, authors, keywords
   - Description from GitHub release
   - License (GPL-3.0)
   - Links to GitHub repo
3. Download archived snapshot to confirm completeness

## Why This Matters for Academic Software
- **Permanent citation**: DOI never changes, even if GitHub repo moves/deletes
- **Versioned snapshots**: Each release gets unique DOI (e.g., `.../zenodo.123` concept DOI, `.../zenodo.124` version DOI)
- **Academic credibility**: Researchers can cite software in papers using DOI
- **Reproducibility**: Archived snapshots preserve exact code state
- **Discovery**: Zenodo indexed by Google Scholar, academic search engines

## Alternative: Manual Upload (if GitHub integration fails)
1. Go to https://zenodo.org/deposit/new
2. Upload: `sfm_core-0.1.0.tar.gz`
3. Fill metadata form:
   - Title: "SFM Core: Social Fabric Matrix Graph Service"
   - Creators: Dabbs, Garrick
   - Description: Copy from CITATION.cff abstract
   - Keywords: Copy from pyproject.toml
   - License: GPL-3.0
   - Version: 0.1.0
   - Related identifiers: GitHub repo URL
4. Click "Publish"
5. Copy assigned DOI

## Expected Timeline
- Account creation: 2 minutes
- GitHub integration setup: 3 minutes
- GitHub release creation: 5 minutes
- Zenodo auto-archive: 5-10 minutes (automatic)
- Citation file updates: 5 minutes
- **Total: ~20-30 minutes**

## Next Step After DOI Assignment
Update PUBLICATION_STRATEGY.md Phase 2 checklist:
- [x] Zenodo DOI obtained
- [ ] Update all citation files with DOI
- [ ] Add DOI badge to README
- [ ] Proceed to academic outreach
