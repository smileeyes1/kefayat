# KEFAYAT Ω — MATHEMATICAL VISUAL CONSTITUTION

## Status
This document defines **mandatory knowledge constraints for human-visible mathematical artifacts**. It is specifically designed to prevent RTL/BiDi/rendering errors and number-to-quantity mismatches.

## 1. Three orders are independent
Never infer one from another:

`UI DIRECTION ≠ LANGUAGE DIRECTION ≠ EDUCATIONAL ORDER ≠ MATHEMATICAL ORDER ≠ VISUAL ORDER`

Arabic may be RTL while a mathematical expression has an explicitly prescribed visual order. The prescribed visual order wins for the artifact.

## 2. Explicit visual sequence
Any critical mathematical expression must first be represented as ordered semantic elements:

`ELEMENT_ID → VALUE/ROLE → VISUAL_POSITION`

Example required visual order:
`[ANSWER_BOX] → [EQUALS] → [٤] → [+] → [٣]`

Therefore the human-visible result must be exactly:
`□ = ٤ + ٣`

It must **not** become:
`٣ + ٤ = □`
or
`□ = ٣ + ٤`

Mathematical equivalence is irrelevant to visual-order compliance.

## 3. Technology must not define meaning
Do not rely on RTL, BiDi, CSS direction, flex order, HTML DOM order, renderer behavior, PDF layout, SVG order, Canvas order, framework behavior, or library defaults to establish the intended mathematical sequence.

The intended sequence must be explicitly encoded/controlled independently of those mechanisms.

## 4. Human-visible acceptance rule
The final rendered artifact is the authority:
`VISIBLE OUTPUT > SOURCE DATA > CODE > INTENTION`

Inspect what a human actually sees. Internal correctness does not prove visual correctness.

## 5. Mathematical visual tests
For every critical expression test:
- `POSITION_TEST` — each element is in its intended position.
- `ORDER_TEST` — sequence matches the prescribed visual sequence exactly.
- `NUMBER_IDENTITY_TEST` — every numeral is the intended numeral.
- `OPERATOR_TEST` — operator is correct and correctly positioned.
- `EQUALS_TEST` — equality sign is correct and correctly positioned.
- `ANSWER_BOX_TEST` — answer box is in the intended location.
- `SPACING_TEST` — spacing does not create a false grouping or separation.
- `VISUAL_RELATION_TEST` — a learner can immediately understand which elements belong together.

## 6. Critical failure protocol
Any unintended visual reversal, movement, substitution, omission, duplication, or ambiguity is:
`CRITICAL FAILURE → NO-GO → REPAIR → VISUAL RECHECK → RETEST → REGRESSION`

Do not release a known critical visual defect.

## 7. Quantity/number binding
For any number represented by visible objects:
`VALUE → REQUIRED_COUNT → BOUND_GROUP → VISUAL_ELEMENTS`

The invariant is:
`VISIBLE_COUNT = INTENDED_VALUE`

and:
`BOUND_GROUP ↔ CORRECT_NUMBER`

A correct numeral with the wrong number of objects is a failure. Correct objects with the wrong numeral are a failure. Correct counts with unclear ownership are a failure.

## 8. Per-group tests
For every numeric visual group:
- `VALUE_TEST`
- `COUNT_TEST`
- `BINDING_TEST`
- `GROUP_BOUNDARY_TEST`
- `VISUAL_COUNTABILITY_TEST`
- `DUPLICATION_TEST`
- `OMISSION_TEST`

The test must be applied to **every repeated group**, not only one sample.

## 9. Single source of truth
Never independently type the numeral and independently draw its objects and assume they match.

Create one authoritative value, then derive:
`VALUE → NUMERAL → VISUAL_GROUP → COUNT → LABEL/QUESTION → ANSWER`

The same value must drive all representations.

## 10. Example
If the intended value is `٥`:
- displayed numeral = `٥`;
- required visible count = `٥`;
- bound group contains exactly `٥` countable objects;
- group is visually identifiable as belonging to `٥`;
- no extra object may appear inside the group;
- no required object may be missing.

`٥ + ٦ objects = FAIL` even if the page otherwise looks attractive.

## 11. Regression principle
When a mismatch is discovered, fix both the artifact and the generation method. Add or strengthen a rule/test so the same failure is prevented in future artifacts.