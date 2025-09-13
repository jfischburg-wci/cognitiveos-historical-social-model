# Actions → Correct Mapping, Smooth Motion, Reset to Neutral

This PR is a record of the work ensuring each UI action triggers the correct behavior, motion is smooth/connected, and each action returns to the neutral state.

- Adds cancel/reset hooks to both Svelte and CSS rigs
- Uses WAAPI `fill: none` so transforms do not persist
- App buttons run through a single runner that cancels/resets before and after
- Preserves underlays and refined masks for seam reduction

