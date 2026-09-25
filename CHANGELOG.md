# CHANGELOG

<!-- version list -->

## v2.0.0 (2026-09-25)

### Breaking changes

- `load_dataset`, `list_datasets` and `get_columns` now raise
  (`DatasetNotFoundError`, `DownloadError`, `ValueError`) instead of returning `None`.
- The package no longer installs top-level `utils` and `configs` modules; the
  dataset registry lives at `aircheckdata/configs/datasets.yaml`.
- `list_datasets()` takes only `partner_name`.
- CLI `load` now takes `PARTNER DATASET` like `columns`; `partners` and `cache`
  commands added.
- Requires Python 3.10+ (the code already used 3.10 syntax).

### Features

- Datasets are cached on disk (`~/.cache/aircheckdata` or `$AIRCHECKDATA_CACHE_DIR`)
  and downloaded once; `clear_cache()` and `use_cache=False` added.
- Downloads stream to disk atomically with request timeouts.

### Fixes

- Library no longer calls `logging.basicConfig` on import; debug prints removed.
- Single-sourced version (`aircheckdata.__version__`); `gcsfs` dependency dropped.
- Test suite no longer hits the network.

## v1.0.1 (2025-06-05)

### Bug Fixes

- Test file modified
  ([`66b599c`](https://github.com/StructuralGenomicsConsortium/AIRCHECK-data-package/commit/66b599ccafd9cbfb0f099e3ce790967f21983f95))


## v1.0.0 (2025-06-05)

- Initial Release

## v1.2.0 (2025-06-05)


## v1.1.0 (2025-06-05)

### Features

- Pyproject file fixed
  ([`a99f218`](https://github.com/nabinelnino/new-package/commit/a99f21822e73552f5798ed4870430a9f364e2b6c))


## v1.0.0 (2025-06-04)

- Initial Release
