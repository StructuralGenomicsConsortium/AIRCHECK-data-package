# `aircheckdata`: AIRCHECK Parquet Dataset Loader

A lightweight Python package and CLI tool for listing and loading **AIRCHECK** datasets, with built-in support for column selection, progress tracking, and automatic local caching. This is the Pythonic way to programmatically access datasets that are also available for download via the [AIRCHECK website](https://www.aircheck.ai/datasets). Before using any dataset, please ensure you have read and agreed to the dataset agreement **[HitGen End User License Agreement (EULA)](https://www.aircheck.ai/docs/HitGen.pdf)**

---

## ✅ Best Practices

- **Use virtual environments** to avoid dependency conflicts:

  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows use .venv\Scripts\activate
  ```

- Always validate that your code respects **data privacy and licensing terms**.
- Avoid storing large datasets in version control. Let `aircheckdata` handle caching.

---

## 📦 Installation

You can install the package from PyPI:

```bash
pip install aircheckdata
```

For development see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 🔧 Usage in a Python Project (Virtual Environment)

`aircheckdata` can be used directly from your Python environment to:

- List pre-configured datasets
- View available columns and metadata
- Load datasets with optional filtering and progress indicators

## Quick Start

### List Datasets

```python
from aircheckdata import list_datasets

datasets = list_datasets()
for name, desc in datasets.items():
    print(f"{name}: {desc}")
```

### View Available Columns

```python
from aircheckdata import get_columns

columns = get_columns('HitGen','WDR91')
names = [item["name"] for item in columns]
print("Column Names: \n", names)

```

### Load dataset

```python
from aircheckdata import load_dataset

# Argument order is (partner, dataset). Both default to HitGen / WDR91.
df = load_dataset("HitGen", "WDR91", columns=["ECFP6", "ECFP4", "LABEL"])
df = load_dataset()  # every column of HitGen WDR91
print(df.head())
```

The first call downloads the Parquet file into a local cache; later calls, with any column selection, read from the cached file and need no network.

### Advanced Usage

```python
from aircheckdata import load_dataset, clear_cache, DatasetNotFoundError, DownloadError

# Hide the progress bar
df = load_dataset("HitGen", "WDR91", columns=["LABEL"], show_progress=False)

# Use a custom cache location (or set AIRCHECKDATA_CACHE_DIR)
df = load_dataset("HitGen", "WDR91", cache_dir="/data/aircheck-cache")

# Do not keep the file on disk after reading
df = load_dataset("HitGen", "WDR91", use_cache=False)

# Errors are raised, not swallowed
try:
    load_dataset("HitGen", "NoSuchTarget")
except DatasetNotFoundError as e:
    print(e)

# Free disk space
clear_cache()                    # everything
clear_cache("HitGen", "WDR91")   # one dataset
```

### Caching

Datasets are stored under `~/.cache/aircheckdata` (or `$XDG_CACHE_HOME/aircheckdata`). Set the `AIRCHECKDATA_CACHE_DIR` environment variable or pass `cache_dir=` to change this. Downloads are written to a temporary `.part` file and renamed only on completion, so an interrupted download never leaves a corrupt cache entry.

---

## 💻 CLI Usage

```bash
aircheckdata --help
```

| Command                                          | Description                                             |
| ------------------------------------------------ | ------------------------------------------------------- |
| `partners`                                       | List dataset providers                                  |
| `list [PARTNER]`                                 | List datasets and descriptions (default: HitGen)        |
| `columns [PARTNER] [DATASET]`                    | List columns of a dataset (default: HitGen WDR91)       |
| `load [PARTNER] [DATASET] [-c COLS] [--no-cache]` | Download a dataset into the cache and print its shape   |
| `cache [--clear]`                                | Show the cache directory, or delete all cached datasets |

Add `-v` before the command to see download and read log messages.

#### Examples

```bash
aircheckdata list
aircheckdata columns HitGen WDR12
aircheckdata columns HitGen "Chicken PLCZ1"          # quote names with spaces
aircheckdata load HitGen WDR91 -c ECFP4,LABEL
aircheckdata -v load HitGen SETDB1 --no-progress
aircheckdata cache --clear
```

---

## 🧑‍💻 Development and Releasing

```bash
uv sync --all-groups      # install with dev tools
uv run ruff format .      # format
uv run ruff check .       # lint
uv run pytest             # tests (no network needed)
```

Work on a feature branch, commit with a [Conventional Commits](https://www.conventionalcommits.org/) prefix (`feat:`, `fix:`, `docs:`, ...), open a PR with a `feature`/`fix`/`documentation` label, and merge into `main`. Bumping `__version__` in `src/aircheckdata/__init__.py` and merging is what publishes a new version to PyPI. Full details, including local package checks and what the release workflow does, are in **[CONTRIBUTING.md](CONTRIBUTING.md)**.

---

## 📜 License and Terms of Use

This package is distributed under the **MIT License**. However, the datasets it provides access to are subject to the **[HitGen End User License Agreement (EULA)](https://www.aircheck.ai/docs/HitGen.pdf)**.

> ⚠️ **By using any dataset accessed via `aircheckdata`, you agree to abide by the HitGen EULA.**
>
> Please refer to the full license terms and conditions here:
> 👉 https://www.aircheck.ai/docs/HitGen.pdf

---

## 📚 Pre-configured Datasets

Currently available datasets include:

- `WDR91`: A curated Parquet dataset provided by **HitGen**
- `WDR12`: A curated Parquet dataset provided by **HitGen**
- `SETDB1`: A curated Parquet dataset provided by **HitGen**
- `LRRK2`: A curated Parquet dataset provided by **HitGen**
- `DCAF7`: A curated Parquet dataset provided by **HitGen**
- `Chicken PLCZ1`: A curated Parquet dataset provided by **HitGen**
- `Chicken PLCZ1 known inhibitor`: A curated Parquet dataset provided by **HitGen**
- `Human PLCZ1 (D202R OR H170A&H215A)`: A curated Parquet dataset provided by **HitGen**
- `Human PLCZ1 (D202R OR H170A&H215A) known inhibitor`: A curated Parquet dataset provided by **HitGen**
- `PLCZ1 (Chicken or Human mutants)`: A curated Parquet dataset provided by **HitGen**
- `PLCZ1 off target His-PLCD1;2:756`: A curated Parquet dataset provided by **HitGen**

---

## 🛠 Requirements

- Python 3.10+

---

## 💬 Feedback, Issues, and Support

We welcome feedback and contributions to help improve `aircheckdata`.

If you encounter a bug, experience unexpected behavior, have a question, or would like to suggest a new feature, please submit an issue through our GitHub Issues page.

- **🐛 Bug Reports:** Report bugs, errors, or unexpected behavior.
- **💡 Feature Requests:** Suggest new features, datasets, or improvements.
- **❓ Questions and Support:** Ask questions about package usage, dataset access, or functionality.

👉 **[Report an Issue or Submit Feedback](https://github.com/StructuralGenomicsConsortium/AIRCHECK-data-package/issues)**

When submitting an issue, please include a clear description of the problem or suggestion, the steps to reproduce the issue (if applicable), and relevant error messages or code snippets.


