#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python3 -m lumen_veil.cli run --scenario scenarios/sorox_unsealed_arrival.json --steps 6 --pretty
