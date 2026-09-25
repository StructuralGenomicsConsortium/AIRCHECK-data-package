# Contributing and Releasing

This guide covers the full loop: set up, test locally, commit, open a PR, and ship a new version to PyPI.

## 1. Set up

Requirements: Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:StructuralGenomicsConsortium/AIRCHECK-data-package.git
cd AIRCHECK-data-package
uv sync --all-groups          # creates .venv, installs the package (editable) + dev tools
uv run aircheckdata --help    # sanity check
```

## 2. Test everything locally

Run these before every commit. CI runs exactly the same commands and fails if any of them do.

```bash
uv run ruff format .          # auto-format (CI fails if this would change a file)
uv run ruff check .           # lint: docstrings, imports, pandas/pytest rules
uv run pytest                 # unit tests, ~0.2 s, no network needed
```

Useful variations:

```bash
uv run pytest -v                                        # verbose
uv run pytest tests/test_loader.py                      # one file
uv run pytest tests/test_cli.py::test_load              # one test
uv run pytest --cov=aircheckdata --cov-report=term      # coverage
```

### Live end-to-end check (optional, needs network)

Unit tests fake the network. To hit the real signed-URL service and confirm caching works, point the cache at a disposable directory so you do not fill `~/.cache`:

```bash
export AIRCHECKDATA_CACHE_DIR=/tmp/aircheck-cache
uv run aircheckdata -v load HitGen WDR91 -c LABEL,ECFP4 --no-progress   # downloads (~900 MB)
uv run aircheckdata -v load HitGen WDR91 -c LABEL                       # instant, from cache
uv run aircheckdata cache --clear
```

### Check the built package

```bash
rm -rf build dist
uv build                                  # wheel + sdist into dist/
unzip -l dist/*.whl | grep -v dist-info   # must list ONLY aircheckdata/... entries, incl. configs/datasets.yaml
```

Install the wheel into a throwaway environment to make sure it works outside the repo:

```bash
uv venv /tmp/aircheck-test --python 3.12
uv pip install --python /tmp/aircheck-test/bin/python dist/*.whl
/tmp/aircheck-test/bin/aircheckdata columns HitGen WDR12
```

## 3. Branch, commit, and open a PR

Never commit directly to `main`; every push to `main` triggers the release workflow.

```bash
git checkout main && git pull
git checkout -b feat/short-description      # or fix/..., docs/..., chore/...
# ... make changes, run the checks in section 2 ...
git add -A
git commit -m "feat: add SETDB1 column descriptions"
git push -u origin feat/short-description
```

Then open a pull request against `main` on GitHub.

### Commit message prefixes

Use [Conventional Commits](https://www.conventionalcommits.org/). The prefix tells reviewers what kind of change it is and what version bump it needs:

| Prefix       | Use for                                   | Version bump |
| ------------ | ----------------------------------------- | ------------ |
| `feat:`      | New functionality, new dataset            | minor        |
| `fix:`       | Bug fix                                   | patch        |
| `perf:`      | Performance improvement                   | patch        |
| `docs:`      | README, docstrings, this file             | none         |
| `test:`      | Tests only                                | none         |
| `refactor:`  | Code change with no behaviour change      | none         |
| `ci:`        | GitHub workflows                          | none         |
| `chore:`     | Tooling, dependencies, housekeeping       | none         |
| `feat!:` / `fix!:` | Breaking change (also describe it in the body) | major |

### PR labels

The GitHub release notes are generated from PR **labels** (see `.github/changelog_config.json`), not from commit messages. Put one of these labels on every PR: `feature`, `fix`, `test`, `documentation`, `chore`. Unlabelled PRs land under "Other".

## 4. Release a new version

A release happens automatically when a PR that bumps the version is merged into `main`. Nothing is published if the version is unchanged, so ordinary PRs are safe.

1. **Pick the version** using semantic versioning (`MAJOR.MINOR.PATCH`):
   - patch (`2.0.0` → `2.0.1`): bug fixes only
   - minor (`2.0.0` → `2.1.0`): new features / datasets, backwards compatible
   - major (`2.0.0` → `3.0.0`): breaking API or CLI changes
2. **Bump `__version__`** in `src/aircheckdata/__init__.py`. This is the only place the version lives; `pyproject.toml` reads it at build time.
3. **Add a `CHANGELOG.md` entry** at the top of the version list.
4. Commit on your feature branch, e.g. `git commit -m "chore: release v2.1.0"`, push, open the PR, get it reviewed, merge.

### What happens on merge (`.github/workflows/release.yaml`)

1. `test.yaml` runs: ruff + pytest on Python 3.10–3.12, and `aircheckdata --help` on Linux, macOS, and Windows.
2. The workflow reads `__version__`. If tag `v<version>` already exists, it stops (no release).
3. Otherwise it builds release notes from the merged PRs since the last tag, creates and pushes tag `v<version>`, runs `uv build`, uploads to PyPI, and creates a GitHub Release.

Do **not** create version tags by hand; the workflow owns them. The one secret the workflow needs is `PYPI_API_TOKEN` in the repository settings.

### Verify

```bash
pip install --upgrade aircheckdata
python -c "import aircheckdata; print(aircheckdata.__version__)"
```

Also check the Releases page on GitHub for the new tag and notes.

### If the release fails

- Tests failed: fix on a branch, merge again; the version is still untagged so the release will retry.
- PyPI upload failed after the tag was pushed: fix the cause, delete the tag (`git push --delete origin v<version>` and `git tag -d v<version>`), and re-run the workflow from the Actions tab or merge another commit.

## 5. Adding a dataset

1. Add a block under the partner in `src/aircheckdata/configs/datasets.yaml` with a `description` and the full `columns` list. `tests/test_config.py::test_registry_is_well_formed` catches missing descriptions and duplicate column names.
2. Add the dataset to the "Pre-configured Datasets" list in both `README.md` and `README package.md`.
3. The backend signed-URL service must already know the partner/target pair; this repo cannot add datasets to the server.
4. Bump the minor version and release as above.
