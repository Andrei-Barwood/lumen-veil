# CLI Invocations

List the bundled rites:

```bash
PYTHONPATH=src python3 -m lumen_veil rites --pretty
```

Run the Sorox threshold watch:

```bash
PYTHONPATH=src python3 -m lumen_veil conduct \
  --scenario scenarios/sorox_unsealed_arrival.json \
  --steps 3 \
  --pretty
```

Inspect the Vossk canon:

```bash
PYTHONPATH=src python3 -m lumen_veil canon \
  --jurisdiction vossk \
  --pretty
```

Open the HTTP gate:

```bash
PYTHONPATH=src python3 -m lumen_veil gate --host 127.0.0.1 --port 8787
```
