# raw-to-sdtm-python

Derivation of CDISC SDTM domains from raw EDC-style data, written in Python (pandas), with automated QC against a reference implementation.

## What it does

Starting from the raw datasets of the CDISC Pilot study published in the R package `pharmaverseraw`, the code builds two SDTM domains:

| Domain | Function | Variables | Match with reference |
|---|---|---|---|
| DM (Demographics) | `src/derive_dm.py` | 28 | 25 of 28 |
| AE (Adverse Events) | `src/derive_ae.py` | 35 | 29 of 35 |

The reference datasets come from the R package `pharmaversesdtm`. Every variable is compared subject by subject (DM) or row by row (AE) with `pytest`. The variables that do not match are documented, with the reason and the decision taken, in `spec/discrepanze_dm.md` and `spec/discrepanze_ae.md` (in Italian).

## Workflow

1. **Mapping specification** (`spec/sdtm_spec.xlsx`): for each SDTM variable, its raw source and derivation rule.
2. **Derivation** (`src/`): one function per domain, following the specification.
3. **QC** (`tests/`): an independent comparison with the reference domain, in the spirit of double programming.
4. **Discrepancy log** (`spec/`): what differs, why, and what was decided.

Points handled in the code: ISO 8601 dates (including partial dates such as `2003`), controlled-terminology recoding, reference dates taken from other domains (DS, EC), study days without day 0, MedDRA hierarchy, sequence numbers.

## How to run

```
conda env create -f environment.yml
conda activate sdtm
Rscript scripts/export_data.R     # writes the CSV files in data/ (needs R with pharmaverseraw and pharmaversesdtm)
python -m pytest -q
```

## Data

The data are not stored in this repository: `scripts/export_data.R` exports them from the `pharmaverseraw` and `pharmaversesdtm` packages (pharmaverse, CDISC Pilot study, synthetic data).
