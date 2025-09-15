Constraints Schema (for artists)

- File: `frontend/src/lib/rig/constraints.json`
- Purpose: Clamp per-bone pitch (rotation) globally and with per-action overrides.

Schema:

- pitch: default clamp per bone id
  - Example: "BeakLower": [0, 45]

- actions.pitch: optional per-action clamp overrides
  - Example: under "caw": set narrower ranges for head/beaks/neck

Notes:

- Ranges are degrees inclusive: [min, max]
- Only listed bones are clamped; others fall back to skeleton spec ranges
- Action clamp takes precedence over default clamp when that action runs
- Add new bones here when adding to `corvid_v1.json` (e.g., Shoulder, Elbow, Wrist, Primaries; Hip/Knee/Ankle/Toes)

