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

For development and testing (optional):

```bash
pip install -e ".[dev]"
```

Installation verification (optional)

Verify that the installation was successful by running unit tests

```bash
pytest tests/
```

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

df = load_dataset('HitGen','WDR91', columns=['ECFP6','ECFP4','LABEL'])  # Download specified data columns with progressbar or
df = load_dataset('HitGen','WDR91', columns=['ECFP6','ECFP4','LABEL'],show_progress=False) # Download specified data columns with without progressbar, this is more memory efficient and faster
df = load_dataset()  # Download once, then cache locally (by default it loads HitGen WDR91 Target)
print(df.head())
```

### Advanced Usage

```python
# Load only selected columns
df = load_dataset('WDR91', columns=['ECFP6', 'ECFP4', 'LABEL'])

# Show progress while loading
df = load_dataset('WDR91', show_progress=True)


```

---

## 💻 CLI Usage

The `aircheckdata` CLI enables quick access to datasets via command-line:

```bash
aircheckdata --help
```

### Options and Examples

| Option                                | Description                                         |
| ------------------------------------- | --------------------------------------------------- |
| `list`                                | List all available datasets                         |
| `columns Provider Name "Target Name"` | Select columns to load or list columns of a dataset |

#### Examples

```bash
# List datasets
aircheckdata list


# View available columns for Distinct Target (defaults to HitGen WDR91 if no provider and Target name is given)
# aircheckdata columns
airctest columns <Provider Name> <Target Name>
airctest columns HitGen "WDR12"
```

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

---

## 🛠 Requirements

- Python 3.7+

---
