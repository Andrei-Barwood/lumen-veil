# Passage to Release

The convoy scenario offers the clearest procession from witness to grace:

1. `WitnessService` emits `VesselWitnessed`.
2. `SealService` classifies `Concord Hymn` as `ally`.
3. Sorox canon moves the vessel through `measured`, `known`, and `blessed`.
4. `MercyService` applies only restorative effects.
5. The final state becomes `released` and the event stream includes `TransitPurified`.

Invocation:

```bash
PYTHONPATH=src python3 -m lumen_veil conduct \
  --scenario scenarios/authorized_convoy_anomaly.json \
  --steps 4 \
  --pretty
```
