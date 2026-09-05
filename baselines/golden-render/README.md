# Golden Render Baseline

This directory is the machine-readable P0 contract for Arabic student-facing linear addition.

Canonical mapping:

`SEMANTIC / USER-EYE: A + B = R`

`ENGINE REQUEST: R = B + A`

Reference:

`٤ + ٣ = □` ⇐ `□ = ٣ + ٤`

Do not infer mathematical display from RTL/BiDi. Do not swap operand identities. All visuals bound to an operand move with that operand. The exact final rendered artifact is the release oracle.

The imported qualification evidence under `evidence/imported/` is evidence-scoped: source artifacts passed their documented user-eye checks, while platform-specific Gemini Gem runtime acceptance remains unproven until an actual platform run is observed.
