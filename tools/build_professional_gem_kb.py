from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "GEM_KB_PROFESSIONAL"

SUBJECTS = {
    "ARABIC": {
        "source": "GEM_KB_ARABIC_GRADES_1-4.md",
        "title": "الكفايات المرجعية للغة العربية — الصفوف ١–٤",
        "scope": "الاستماع، المحادثة والتعبير الشفوي، القراءة، الكتابة، الأنماط اللغوية، والتدرج في الأداء وفق المادة المصدرية.",
    },
    "MATH": {
        "source": "GEM_KB_MATH_GRADES_1-4.md",
        "title": "الكفايات المرجعية للرياضيات — الصفوف ١–٤",
        "scope": "المجالات الرياضية، كفايات الممارسة، الكفايات الفرعية، المعايير، نتاجات التعلم، مستويات الأداء، والقيم كما وردت في المادة المصدرية.",
    },
    "ISLAMIC": {
        "source": "GEM_KB_ISLAMIC_GRADES_1-4.md",
        "title": "الكفايات المرجعية للتربية الإسلامية — الصفوف ١–٤",
        "scope": "الكفايات والممارسات والقيم والمؤشرات ومستويات الأداء في التربية الإسلامية، مع تطبيق بوابة الأصالة الإسلامية الموجودة في المستودع.",
    },
    "NURTURING": {
        "source": "GEM_KB_NURTURING_GRADES_1-4.md",
        "title": "الكفايات المرجعية للتربية الوطنية والحياتية/التنشئة — الصفوف ١–٤",
        "scope": "الكفايات الوطنية والحياتية للصفين ١–٢، والتنشئة للصفين ٣–٤، مع الحفاظ على تسمية المصدر لكل صف وعدم اختلاق تكافؤ رسمي غير موثق.",
    },
}


def arabic_grade(n):
    return str(n).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def split_grades(text):
    parts = re.split(r"(?m)^## الصف ([1-4])\s*$", text)
    grades = {}
    for i in range(1, len(parts), 2):
        grades[int(parts[i])] = parts[i + 1].strip()
    return grades


def source_header():
    return [
        "# قاعدة معرفة GEM Ω — الكفايات التعليمية",
        "",
        "> **حالة المصدر:** مادة مرجعية مقدمة/مجمعة في مستودع KEFAYAT وليست موسومة كمصدر رسمي متحقق منه استقلاليًا.",
        "> **قاعدة الأمانة:** لا تُحوّل الصياغة المنسقة أو المستخلصة إلى ادعاء رسمي. عند وجود تعارض، يُرجع إلى المادة المصدرية المحفوظة في المستودع.",
        "> **قاعدة الاستخدام:** هذه الملفات طبقة معرفة بالمخرجات التعليمية المطلوبة، وليست بديلًا عن الحكم المهني للمعلم أو عن التحقق الرسمي عند الحاجة.",
        "",
    ]


def build(subject, meta):
    src = ROOT / meta["source"]
    text = src.read_text(encoding="utf-8")
    grades = split_grades(text)
    out = source_header()
    out += [
        f"## {meta['title']}",
        "",
        f"**المجال:** {meta['scope']}",
        "**المصدر الأساسي:** `" + meta["source"] + "`",
        "**نطاق التغطية:** الصفوف ١–٤.",
        "**الغرض:** تمكين Gem من استرجاع الكفايات بحسب الصف والمجال، وربطها بنتائج التعلم والأداء المتوقع والتقويم عند بناء درس أو نشاط أو ورقة عمل.",
        "",
        "## قواعد القراءة والاسترجاع",
        "1. ابدأ دائمًا بالصف المطلوب ثم المجال ثم الكفاية ثم المعيار/نتاج التعلم ثم مستوى الأداء.",
        "2. اعتبر «يتقن» مستوى الإتقان المستهدف، و«يطور» مستوى الأداء النامي، و«يحاول» مستوى الأداء الذي يحتاج إلى دعم، وفق المصدر.",
        "3. لا تدمج كفايات من صف مختلف إلا إذا كان المطلوب مقارنة التدرج.",
        "4. لا تحذف أو تستبدل تفاصيل المصدر عند استخدامها لاتخاذ قرار تعليمي.",
        "5. لا تستنتج معيارًا رسميًا غير موجود في المصدر.",
        "6. في التربية الإسلامية، لا تُنشئ حكمًا شرعيًا أو نصًا منسوبًا إلى القرآن أو السنة اعتمادًا على الاستنتاج؛ استخدم المصدر الموثوق عند الحاجة.",
        "",
        "## خريطة التغطية",
    ]
    for g in range(1, 5):
        if g in grades:
            out.append(f"- الصف {arabic_grade(g)}: **موجود في المصدر**")
        else:
            out.append(f"- الصف {arabic_grade(g)}: **غير موجود في الملف المصدر**")
    out += ["", "---", ""]

    for g in range(1, 5):
        if g not in grades:
            continue
        body = grades[g]
        # Remove duplicated wrapper metadata from the source grade block.
        body = re.sub(r"^SOURCE:.*\nEXTRACTION ORIGIN:.*\n\n### ORIGINAL EXTRACTED TEXT\n\n", "", body, flags=re.S)
        out += [
            f"# الصف {arabic_grade(g)}",
            "",
            f"## بطاقة الصف {arabic_grade(g)}",
            f"**المصدر:** `{meta['source']}` — قسم الصف {g}",
            "**حالة البيانات:** محفوظة من المادة المصدرية مع إعادة تنظيم العرض فقط.",
            "",
            "## الكفايات والمعايير والمؤشرات — النص المصدر المنظم",
            "",
            body,
            "",
            "## بوابة الاستخدام لهذا الصف",
            f"عند طلب مخرج للصف {arabic_grade(g)}: استخدم كفايات هذا القسم فقط ما لم يطلب المستخدم صراحة المقارنة أو التدرج بين الصفوف.",
            "تحقق من الصف والمجال والمهارة والقيمة ومستوى الأداء قبل بناء أي نشاط أو سؤال أو تقويم.",
            "",
            "---",
            "",
        ]
    return "\n".join(out).strip() + "\n"


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    generated = []
    for subject, meta in SUBJECTS.items():
        content = build(subject, meta)
        path = DIST / f"KEFAYAT_GEM_KB_{subject}_GRADES_1-4.md"
        path.write_text(content, encoding="utf-8")
        generated.append(path)

    readme = DIST / "README.txt"
    readme.write_text(
        "KEFAYAT Ω — Professional GEM Knowledge Base\n"
        "Four subject knowledge files for grades 1–4.\n\n"
        "Files:\n"
        "1) Arabic\n2) Mathematics\n3) Islamic Education\n4) National/Life Education and Nurturing\n\n"
        "Source status: user-provided/reference material in the KEFAYAT repository; not independently certified as official.\n"
        "The files preserve the source competency content while adding a professional retrieval-oriented wrapper.\n",
        encoding="utf-8",
    )
    zip_path = ROOT / "dist" / "KEFAYAT_GEM_KNOWLEDGE_BASE_4_SUBJECTS_GRADES_1-4.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in [*generated, readme]:
            z.write(p, arcname=p.name)
    print(f"Generated {len(generated)} subject files and {zip_path}")


if __name__ == "__main__":
    main()
