# HTTP API

The gate uses only the Python standard library and mirrors the same order as the CLI: list the rites, read the canon, conduct the passage.

## Endpoints

- `GET /health`
- `GET /scenarios`
- `GET /policy/<jurisdiction>`
- `POST /run`

### `POST /run`

Request body:

```json
{
  "scenario": "scenarios/vossk_minor_intrusion.json",
  "steps": 4,
  "dt": 1.0
}
```

Response fields include:

- `scenario`
- `canon_name`
- `jurisdiction`
- `ticks`
- `rite_summary`
- `final_states`
- `audit`
- `events`
- `metrics`
- `training`
