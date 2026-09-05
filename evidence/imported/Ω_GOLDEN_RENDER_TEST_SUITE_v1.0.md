# Ω GOLDEN RENDER QUALIFICATION SUITE v1.0

## Golden fixtures
1. ENGINE `□ = ٣ + ٤` → USER-EYE `٤ + ٣ = □`
2. ENGINE `□ = ٢ + ٥` → USER-EYE `٥ + ٢ = □`
3. ENGINE `□ = ١ + ٨` → USER-EYE `٨ + ١ = □`

## Mandatory environments
Plain line / table / narrow table / card / Arabic paragraph / page edge / page-break proximity / multiple equations / actual PDF / print / all pages.

## Pass conditions
- Physical L→R: `□ | = | B | + | A`
- Exactly one `=`
- `=` immediately after `□` physically and between B and □ in USER-EYE
- Answer box intact
- A/B identities preserved
- Eastern Arabic digits only in student-visible math
- No clipping, overlap, wrapping, ENGINE leakage, or answer leakage
- Counting groups match operands

## Mutation suite — MUST FAIL
`= ٤ + ٣ □`
`٤ + = ٣ □`
`٤ + ٣ □ =`
`٣ + ٤ = □`
`□ = ٣ + ٤` visible to student
`٤ + ٣ ==`
`٤ + ٣`
`4 + 3 = □`
equals sign on another line
clipped equals/answer box
swapped visual groups
wrong counting group

Any mutation accepted => VERIFIER INVALID.
Any P0 => NO-GO.