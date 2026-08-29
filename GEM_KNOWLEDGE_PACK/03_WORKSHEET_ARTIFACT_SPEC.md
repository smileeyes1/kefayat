# KEFAYAT Ω — WORKSHEET ARTIFACT SPECIFICATION

## Purpose
A worksheet is a **finished learner-facing artifact**, not a question list. The expected result is printable, readable, age-appropriate, mathematically correct, visually correct, and immediately usable by the teacher.

## 1. Artifact contract
Before production, define:
`PURPOSE → GRADE → LEARNING_GOAL → ITEM_TYPES → ITEM_COUNT → DATA_MODEL → VISUAL_MODEL → ANSWER_MODEL → PAGE_MODEL → ACCEPTANCE_TESTS → DELIVERY_FORMAT`

If a critical relationship is undefined, do not begin final generation.

## 2. Per-item canonical record
Every item containing a number, visual group, operation, or answer location should have a logical record containing at least:

`QUESTION_ID`
`LEARNING_GOAL`
`QUESTION_TYPE`
`CORRECT_VALUE`
`DISPLAYED_NUMBER`
`VISUAL_GROUP_ID`
`EXPECTED_COUNT`
`ACTUAL_COUNT`
`BINDING_TARGET`
`VISUAL_ORDER`
`ANSWER_LOCATION`
`EXPECTED_RENDERING`

The record is an internal validation model; it does not need to be exposed to the child.

## 3. Number-to-visual binding
For every item:
`CORRECT_VALUE = DISPLAYED_NUMBER = EXPECTED_COUNT = ACTUAL_COUNT`
when the task explicitly represents that value by a one-to-one visual group.

Also:
`VISUAL_GROUP_ID ↔ DISPLAYED_NUMBER`

Never allow independently generated numeral and graphics to drift apart.

## 4. Item acceptance checklist
Every item must pass:
- content correctness;
- intended answer correctness;
- numeral identity;
- visual count correctness;
- visual-to-number binding;
- group separation/ownership;
- absence of extra or missing objects;
- clear learner instruction;
- clear answer location;
- age appropriateness;
- visual readability;
- no unintended mathematical reordering.

## 5. Repeated-item rule
If an error can occur repeatedly, validate **every occurrence**, not only a representative sample.

Example: if a worksheet has ten number-to-object items, run the count/binding checks for all ten.

## 6. Page-level requirements
For printable worksheets, inspect:
- page size and margins;
- clipping and overflow;
- consistent hierarchy;
- readable font size;
- sufficient writing space;
- clear separation between questions;
- no accidental object overlap;
- no orphaned labels;
- correct page breaks;
- correct header/footer if required;
- print-safe contrast and line weight.

## 7. Human-use test
Ask whether a child can answer the item without guessing what belongs to what. If a teacher must explain a visual relationship that should have been obvious, the item fails usability.

## 8. Final rendered artifact is authoritative
A source document, HTML, SVG, code, or generated data structure is not the acceptance target. The rendered/printed worksheet is.

`SOURCE ≠ RENDERED PRODUCT`

A defect visible only after conversion to PDF or printing is still a product defect.

## 9. Release gate
Release only when:
`CONTENT PASS + MATH PASS + VISUAL PASS + USABILITY PASS + PAGE PASS + FILE PASS + DELIVERY PASS`

Any material failure means `NO-GO` until repaired and re-tested.