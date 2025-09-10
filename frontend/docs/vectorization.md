Corvid Logo → Animated SVG Workflow

Goal
- Create a clean, single‑color (or few‑color) crow silhouette SVG that matches `frontend/public/corvid_logo.png` in outline and proportions, with separate paths for head, eye, beak, wing (3 feather layers), tail, and legs. This enables blink, head bob, hop, and feather shakes directly in code.

Option A — Illustrator (recommended for brand assets)
1) File → New from your PNG or Place the PNG on a locked layer.
2) Window → Image Trace. Preset: Black and White Logo.
   - Threshold: adjust until the silhouette is clean.
   - Paths/Noise: increase Paths, reduce Noise to keep edges crisp.
   - Click Expand to convert to vectors.
3) Use the Pen tool to separate parts into editable shapes:
   - Wing group: draw 3 overlapping shapes following feather contours.
   - Head, eye (circle), beak, tail, legs as separate paths.
4) Pathfinder → Unite/Minus Front to clean overlaps. Smooth anchors where needed.
5) Set fills to near‑black (e.g., #0b0f14) with slight variation per feather.
6) Save As → SVG. SVG Options: Styling = Presentation Attributes, Decimal = 2, Responsive = true.
7) Replace the group in `frontend/src/lib/ParallaxCrow.svelte` or export to `frontend/src/assets/crow.svg` and inline its paths.

Option B — Inkscape (open source)
1) Path → Trace Bitmap → Single scan (Brightness cutoff), adjust Threshold until silhouette is clean.
2) Path → Simplify (optional) while preserving shape fidelity.
3) Use Node tool to separate wing into 3 feather paths; draw eye as separate circle.
4) Save as Plain SVG and integrate as above.

Option C — CLI (repeatable, fast)
Requirements: ImageMagick + Potrace.

  # 1) Convert PNG to high‑contrast PNM (bitmap)
  magick frontend/public/corvid_logo.png -colorspace Gray -threshold 55% /tmp/corvid.pnm

  # 2) Trace to SVG with Potrace
  potrace /tmp/corvid.pnm -s -o frontend/src/assets/crow_trace.svg --flat --turdsize 5 --longcurve 1 --opttolerance 0.2

Then open the SVG in an editor, split into parts (wing feathers, head, beak, legs, tail), and paste the resulting <path> elements into the wing/head/body areas of `ParallaxCrow.svelte`.

Integration Notes
- Keep consistent coordinate space. If your exported SVG uses a different viewBox, either:
  - Replace the internal <g> in `ParallaxCrow.svelte` and adjust the `viewBox`, or
  - Copy just the paths into the existing group and nudge transforms to align.
- For animation, ensure classes/ids:
  - `.wing .feather` (f1/f2/f3), `.head`, `.eye`, `polygon` for beak, tail path, legs.
- Aim for smooth anchor curves and minimal point count — it animates better.

Testing
- Run `cd frontend && npm install && npm run dev` and open http://localhost:5173
- Verify proportions align with the header logo. Tweak `viewBox` or group `transform` as needed.

