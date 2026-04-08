# Scenario Guide

Each scenario is a small rite of judgment. Together they show how Sorox and Vossk witness approach, weigh ambiguity, and impose order without losing doctrinal character.

Bundled scenarios:

- `sorox_unsealed_arrival`: an unsealed hull enters the gold path and meets immediate Sorox measure.
- `vossk_minor_intrusion`: a drifting contact tests Vossk's patience for partial accord.
- `authorized_convoy_anomaly`: a blessed convoy proceeds while one escort falls into shadow.
- `low_mass_swarm`: scattered low-mass contacts force Vossk to answer with pattern rather than haste.
- `false_flag_crossing`: a borrowed halo crosses ceremonial watch under a weak seal.
- `storm_degraded_sensor`: sparse witness in a storm tests Vossk restraint.
- `sorox_vossk_sovereignty_conflict`: foreign grace enters a border that reserves its own judgment.
- `neutral_liturgical_corridor`: a neutral rite-lane stays open only while geometry and bearing remain in concord.

## Rite of Release

```bash
PYTHONPATH=src python3 -m lumen_veil conduct \
  --scenario scenarios/authorized_convoy_anomaly.json \
  --steps 4 \
  --pretty
```

This yields a full trace from first witness to final release, while the escort vessel departs from harmony and settles into `shadowed`.
