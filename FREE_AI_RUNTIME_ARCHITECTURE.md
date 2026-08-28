# FREE AI Runtime — Kefayat

## الهدف
تشغيل ذكاء اصطناعي حقيقي مع أقل تكلفة ممكنة على مالك المشروع، مع احترام حصص المزودين وعدم التحايل عليها.

## الترتيب التشغيلي

1. Knowledge Base / deterministic rules — صفر استهلاك AI.
2. Cache — إعادة استخدام الإجابات السابقة عند تطابق المهمة والسياق.
3. Local model — عند توفر نموذج محلي على الجهاز/البيئة.
4. User-owned free-tier Gemini API — الطلب يذهب مباشرة إلى Google باستخدام مفتاح المستخدم، ولا يمر عبر خادم Kefayat.
5. Fallback / degraded mode — عند فشل المزود أو انتهاء حد الأمان المحلي، يستمر التطبيق دون ادعاء أن الناتج AI.

## قاعدة التكلفة

لا توجد طريقة مشروعة لضمان توكنات سحابية مجانية وغير محدودة إلى الأبد. الحصص المجانية تخضع لحدود المزود وتغييراته.

الهدف الهندسي الصحيح هو:

`ZERO OWNER AI BILLING` whenever the user uses their own free-tier access or local inference.

وليس:

`UNLIMITED FREE CLOUD TOKENS`.

## الأمان

- لا توضع مفاتيح API في GitHub.
- لا يستخدم Kefayat مفتاحًا سريًا مشتركًا داخل الواجهة العامة.
- مفتاح المستخدم يبقى على جهازه في الوضع الحالي.
- لا توجد محاولة لتجاوز rate limits أو إنشاء حسابات متعددة أو تدوير مفاتيح للتحايل على الحصص.

## الحالة الحالية

`Gemini 2.5 Flash-Lite` هو مزود السحابة الافتراضي في واجهة GEM، مع Free-First routing وقاطع استخدام محلي وفallback محلي. راجع `ai.html`.

## حدود الادعاء

Free Tier != Unlimited.

Real AI != Always Available.

Local fallback != Generative AI unless a local model is actually installed and invoked.

Production readiness requires real-device testing and provider failure testing.
