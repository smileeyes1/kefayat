# KEFAYAT Ω — GEM Knowledge Base

## Purpose

This package is the curated knowledge layer for a Gemini Gem. It is intentionally separated from runtime code and project implementation details.

## Authority model

- `USER-PROVIDED REFERENCE`: material supplied by the user and preserved as reference.
- `STRUCTURED KNOWLEDGE`: normalized competency/domain knowledge derived from repository sources.
- `ASSURANCE RULES`: deterministic rules governing interpretation, generation, verification, visual correctness, and release.
- `OFFICIAL VERIFIED SOURCE`: must never be claimed unless independently verified against an authoritative source.

## Included domains

- Mathematics — Grades 1–4
- Arabic — Grades 1–4
- Islamic Education — Grades 1–4
- Nurturing / civic-life competencies — Grades 1–4
- Core competency reasoning and educational knowledge model
- Arabic/localization safeguards
- Mathematical visual-order safeguards
- Worksheet artifact specification
- Quality assurance and release rules

## Critical operating rule

Knowledge describes what the learner should know/do; assurance rules describe how the Gem must reason, generate, verify, and release outputs. Do not collapse these layers.

## Mathematical visual truth

When a user specifies a visual mathematical order, the final visible arrangement is authoritative. RTL, BiDi, CSS, HTML, DOM, renderers, PDF engines, SVG, Canvas, frameworks, libraries, or mathematical equivalence must never silently change it.

## Numerical graphics truth

Every visual quantity must be derived from one authoritative value. `VALUE = REQUIRED_COUNT = ACTUAL_VISIBLE_COUNT`, and the visual group must be explicitly bound to the corresponding number.

## Release rule

`GENERATED ≠ VERIFIED`. A product is not ready merely because the source or code is correct. The final artifact visible to the user must be checked, including relationships, counts, ordering, rendering, usability, and delivery.
