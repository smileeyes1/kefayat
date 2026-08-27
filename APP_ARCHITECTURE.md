# كفايات Ω — App Architecture

## Purpose
تحويل مستودع الكفايات إلى تطبيق تعليمي قابل للتشغيل، مع إبقاء المصدر الأصلي منفصلًا عن طبقة التطبيع والتشغيل والضمان.

## Governing baseline
- MASTER Ω vΩ.7.4 + OAC-01 + OAG-01: governance/assurance baseline.
- CAX-01: Competency Assurance & Curriculum Traceability Extension.
- USER-PROVIDED WORKING BASELINE: الكفايات المحفوظة في هذا المستودع.
- OFFICIAL VERIFIED SOURCE: لا يُعلن إلا بدليل مستقل.

## Data layers
1. `raw_sources/` — النصوص المستخرجة من الملفات الأصلية.
2. `GEM_KB_*.md` — قواعد معرفة قابلة للقراءة والاستخدام.
3. Future structured layer — records with stable competency IDs.
4. `index.html` — واجهة التطبيق، لا تعدّل المصدر.

## Mandatory downstream traceability
`SOURCE → COMPETENCY → LEARNING OUTCOME → OBSERVABLE PERFORMANCE → ACTIVITY → EVIDENCE → ASSESSMENT`

## Required competency record
كل سجل منظم يجب أن يحافظ على:
- الصف
- المجال المعرفي
- كفايات الممارسة الرئيسة
- الكفايات الفرعية المستقلة بنيوياً
- المعايير التفصيلية
- نتاجات التعلم
- يتقن / يطور / يحاول
- القيم
- مصدر السجل وموقعه
- حالة المصدر

## Non-negotiable source rule
لا يجوز للتطبيق استبدال النص الأصلي بنص مُعاد الصياغة. التطبيع طبقة منفصلة وقابلة للتتبع.

## Mathematical visual rule
إذا أنشأ التطبيق لاحقًا محتوى رياضيًا بصريًا، يجب بناء الترتيب من بيانات منظمة وترتيب بصري صريح؛ لا يعتمد على BiDi أو CSS أو DOM أو renderer لتحديد الترتيب التعليمي.

## Islamic integrity
التربية الإسلامية تخضع لـ `ISLAMIC_AUTHENTICITY_GATE.md`. لا تُنسب آية أو حديث أو حكم شرعي إلى المصدر دون تحقق مناسب، ولا يُرفع مستوى المصدر إلى رسمي مثبت دون دليل مستقل.

## Current app phase
Phase 1 = Foundation:
- source-aware browsing
- grade/subject filtering
- original-text viewing
- source-state visibility
- GitHub Pages deployment workflow

Phase 2 يجب أن تضيف structured competency records + traceability + validation.
