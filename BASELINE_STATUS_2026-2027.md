# Competency Working Baseline — الصفوف ١–٤ — ٢٠٢٦–٢٠٢٧

## 1. Source status
This repository is the working source repository supplied by the user. Repository: `smileeyes1/kefayat`, default branch: `main`.

This file records structural coverage only. The DOCX files remain the primary user-provided reference texts. They are **not** labeled as officially verified solely because they are stored here.

## 2. Coverage inventory

| الصف | اللغة العربية | الرياضيات | التربية الإسلامية | التنشئة/الوطنية والحياتية |
|---|---|---|---|---|
| ١ | موجود | موجود | موجود | موجود: التربية الوطنية والحياتية |
| ٢ | موجود | موجود | موجود | موجود: التربية الوطنية والحياتية |
| ٣ | موجود | موجود | موجود | موجود: التنشئة |
| ٤ | موجود | موجود | موجود | موجود: التنشئة |

## 3. Repository evidence
The current `main` tree contains 18 DOCX files: 4 Arabic, 4 mathematics, 4 Islamic education, 2 national/life education for grades 1–2, 2 nurturing files for grades 3–4, and 2 science files for grades 3–4.

The four-subject matrix for grades 1–4 is therefore structurally covered when the curriculum's subject naming transition is respected: grades 1–2 use التربية الوطنية والحياتية; grades 3–4 use التنشئة الوطنية والاجتماعية/التنشئة as represented by the supplied files.

## 4. Required canonical schema
Every extracted competency record must preserve, without rewriting at first extraction:
- الصف
- المجال المعرفي
- كفايات الممارسة الرئيسة
- الكفايات الفرعية المستقلة بنيوياً
- المعايير التفصيلية
- نتاجات التعلم
- يتقن
- يطور
- يحاول
- القيم

A separate normalization layer may be added later; it must never replace the source text.

## 5. Traceability rule
For every downstream lesson, plan, matrix, or assessment:
`SOURCE → COMPETENCY → LEARNING OUTCOME → OBSERVABLE PERFORMANCE → ACTIVITY → EVIDENCE → ASSESSMENT`

No downstream artifact may claim an official source status unless independently verified.

## 6. Completeness gate
Structural file coverage is currently established. Content-level completeness, exact-text extraction, cross-grade progression, duplication, gaps, misplaced competencies, and contradictions require extraction and comparison of the DOCX contents. They must not be inferred from filenames alone.

## 7. Islamic education integrity gate
Islamic education is governed by the companion protocol `ISLAMIC_AUTHENTICITY_GATE.md`. The goal is authentic Islamic formation: sound creed, worship, character, mercy, justice, responsibility, truthful conduct, and practical application, grounded in the Qur'an and reliably authenticated Sunnah, while preserving the supplied curriculum wording as the reference layer.
