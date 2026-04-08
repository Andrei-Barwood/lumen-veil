# Native Physics Engine

The C engine advances a 2D abstract field model for motion, exposure, attenuation, and subsystem pressure within the ward lattice.

## Inputs

Per vessel:

- position
- velocity
- acceleration
- susceptibility
- shielding
- subsystem health
- current exposure

Per ward node:

- position
- reach
- intensity
- falloff
- doctrinal bias

## Outputs

- updated position and velocity
- subsystem degradation bounded to `[0, 1]`
- cumulative exposure
- instantaneous field pressure

## Integration Strategy

- The compiled extension exports `propagate`.
- [`src/lumen_veil/physics.py`](/Volumes/macOS - Beck/SnoGuard/src/lumen_veil/physics.py) packs domain objects into stable tuples.
- If the extension is unavailable, the wrapper uses a mathematically equivalent Python implementation.
