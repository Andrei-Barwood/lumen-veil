# Event Contracts

Primary event names:

- `VesselWitnessed`
- `ThresholdCrossed`
- `GraceDenied`
- `SilenceInvoked`
- `ContainmentRaised`
- `TransitPurified`
- `AegisShifted`

## Payload Shape

All events include:

- `trace_id`
- `timestamp`
- `payload`

The payload typically includes:

- `tick`
- `vessel_id`
- `reason_code`
- `rule_name`

## Replay

The event bus appends every event to an in-memory stream. The replay vault captures that stream so scenario runs can be inspected deterministically after execution.
