# KEFAYAT Ω — MATHEMATICAL VISUAL CONSTITUTION

## Status — P0 PROTECTED GOLDEN RENDER LOCK
This document defines mandatory constraints for human-visible mathematical artifacts. The empirical Arabic rendering rule below is a protected invariant. It is not a style preference, a fallback, or permission to swap operands.

## 1. Separate the layers
Never infer one layer from another:

`SEMANTIC ORDER ≠ ENGINE REQUEST ORDER ≠ LANGUAGE DIRECTION ≠ UI DIRECTION ≠ FINAL STUDENT-EYE ORDER`

For an addition expression with semantic roles `operand₁=A`, `operator=+`, `operand₂=B`, `relation==`, `result=R`:

- semantic/student-eye contract: `A + B = R`;
- canonical engine request: `R = B + A`;
- final rendered authority: the student must see `A + B = R`.

For a blank result:

`TARGET/USER-EYE: ٤ + ٣ = □`

`ENGINE REQUEST: □ = ٣ + ٤`

This mapping is the proven Golden Render Rule and is P0-protected.

## 2. Operand identity is immutable
`operand₁` and `operand₂` are semantic identities, not interchangeable values. Commutativity is never permission to swap them in a generated artifact.

If `A=٤` and `B=٣`, the required student-eye expression is `٤ + ٣ = □`. A rendered `٣ + ٤ = □` is a regression even though the arithmetic sum is equal.

Any image, counting group, label, badge, caption, manipulative set, or other visual attached to an operand is part of the same atomic block and moves only with that operand.

## 3. Engine request serialization — protected
For every five-role linear addition expression use:

`ENGINE = [RESULT] [EQUALS] [OPERAND₂] [OPERATOR] [OPERAND₁]`

For the blank-result fixture:

`□ | = | B | + | A`

The implementation may use explicit geometry/token slots internally, but it must preserve this canonical request record and must not replace the Golden Render Rule with generic RTL/BiDi heuristics. A future renderer migration cannot supersede this rule unless the protected contract is explicitly re-qualified against all golden fixtures and final user-eye evidence.

## 4. Final user-eye acceptance
The final rendered artifact is the authority:

`STUDENT-EYE OUTPUT > ENGINE INTENT > SOURCE TEXT > CODE ASSUMPTION`

PASS for the reference fixture requires the learner to see exactly:

`٤ + ٣ = □`

with one equals sign, on one line, between `٣` and `□`, with the answer box intact.

The following are P0 failures for that fixture:
- `٣ + ٤ = □`;
- `□ = ٣ + ٤` visible to the student;
- `= ٤ + ٣ □`;
- `٤ + = ٣ □`;
- `٤ + ٣ □ =`;
- duplicated or missing `=`;
- equals sign or answer box on another line;
- clipping, overlap, wrapping, hidden tokens, or answer leakage;
- Western digits in student-visible math.

## 5. Technology must not define meaning
Do not delegate mathematical meaning to RTL, BiDi, CSS direction, flex order, DOM order, table direction, PDF layout, SVG defaults, Canvas defaults, or renderer behavior. These are implementation mechanisms only.

The semantic model, engine request, and expected student-eye result must be explicit before rendering.

## 6. Mandatory golden fixtures
At minimum, preserve these mappings:

1. `ENGINE □ = ٣ + ٤` → `USER-EYE ٤ + ٣ = □`
2. `ENGINE □ = ٢ + ٥` → `USER-EYE ٥ + ٢ = □`
3. `ENGINE □ = ١ + ٨` → `USER-EYE ٨ + ١ = □`

Verify them in every applicable environment: plain line, table, narrow table, card, Arabic paragraph, page edge, near page break, repeated equations, final PDF, print, and all pages.

Any accepted negative mutation invalidates the verifier.

## 7. Quantity/number/operand binding
For a visible counting representation:

`SEMANTIC OPERAND → NUMERAL → REQUIRED COUNT → VISUAL GROUP → ACTUAL COUNT → POSITION → EVIDENCE`

Required invariants:
- `VISIBLE_COUNT = INTENDED_VALUE`;
- each group belongs to the correct operand;
- group boundaries are obvious;
- decorative objects are not countable as part of the task;
- no extra/missing objects;
- operand order remains the semantic order seen by the learner.

Validate every repeated group, not a sample.

## 8. Number line binding
A number-line model must preserve operand roles. If the instruction means “ابدأ من ٤ واقفز ٣”، then the student-eye equation is `٤ + ٣ = □`; do not swap it to `٣ + ٤ = □`.

A demonstrated number line must show its required ticks/labels/start/jumps/end. A decorative plain line is not evidence of the journey.

## 9. Eastern Arabic numerals
Student-visible numerals use:

`٠ ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩`

Appearance of Western `0-9` in student-facing mathematical content is a release failure unless a specific machine/technical payload is intentionally exempt and not learner-facing.

## 10. Critical failure and regression protocol
Any unintended reversal, operand swap, equals displacement, answer-box displacement, quantity mismatch, omission, duplication, clipping, overlap, or engine-request leakage is:

`P0 → NO-GO → ROOT CAUSE → REPAIR → RE-RENDER → USER-EYE RECHECK → MUTATION TEST → REGRESSION`

Do not patch only the observed instance. Strengthen the generation method and test so the same class of failure cannot silently return.
