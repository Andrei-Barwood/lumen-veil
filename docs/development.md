# Development Guide

Development in Lumen Veil follows the same order as the runtime itself: build the lattice, read the canon, conduct a rite, then examine the ledger.

## Local Setup

```bash
python3 setup.py build_ext --inplace
```

This builds the optional native extension in-place. If compilation is unavailable, the package still runs from `PYTHONPATH=src` using the Python fallback.

Optional editable install when your Python environment allows it:

```bash
python3 -m pip install --user -e .
```

## Common Commands

```bash
make test
make run-sorox
make run-vossk
make serve
```

CLI forms in the archive:

- `python3 -m lumen_veil rites`
- `python3 -m lumen_veil conduct --scenario <path>`
- `python3 -m lumen_veil measure --scenario <path> --steps 1`
- `python3 -m lumen_veil canon --jurisdiction sorox`
- `python3 -m lumen_veil gate --host 127.0.0.1 --port 8787`

## Native Layer

- Source: [`physics/src/lumen_native.c`](/Volumes/macOS - Beck/SnoGuard/physics/src/lumen_native.c)
- Python wrapper: [`src/lumen_veil/physics.py`](/Volumes/macOS - Beck/SnoGuard/src/lumen_veil/physics.py)

## Adding Doctrine

1. Create a new JSON file in `configs/jurisdictions/`.
2. Define `name`, `doctrine`, `ambiguity_tolerance`, `release_bias`, and `rules`.
3. Keep the canon terse, ordered, and legible under audit.
4. Reference that jurisdiction from a scenario fixture.

## Test Strategy

- Unit tests for geometry, events, and policy selection.
- Integration tests for end-to-end scenario runs.
- Property-style randomized tests for field monotonicity and bounded subsystem health.
