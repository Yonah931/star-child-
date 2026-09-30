"""
Content Writer Agent
وكيل كتابة المحتوى: مقالات، وصف منتجات، سوشيال ميديا، إيميلات، إعلانات
"""
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class ContentWriterAgent:
    """وكيل كتابة المحتوى متعدد اللغات"""

    CONTENT_TYPES = {
        "article": {"ar": "مقال مدونة", "fr": "Article de blog", "en": "Blog Article", "icon": "📝"},
        "product": {"ar": "وصف منتج", "fr": "Description produit", "en": "Product Description", "icon": "🛍️"},
        "social": {"ar": "منشور سوشيال", "fr": "Post réseaux sociaux", "en": "Social Post", "icon": "📱"},
        "email": {"ar": "بريد إلكتروني", "fr": "Email", "en": "Email", "icon": "✉️"},
        "ad": {"ar": "إعلان", "fr": "Publicité", "en": "Ad Copy", "icon": "📢"},
        "video": {"ar": "سكريبت فيديو", "fr": "Script vidéo", "en": "Video Script", "icon": "🎬"},
    }

    TONES = {
        "professional": {"ar": "احترافي", "fr": "Professionnel", "en": "Professional"},
        "friendly": {"ar": "ودي", "fr": "Amical", "en": "Friendly"},
        "marketing": {"ar": "تسويقي", "fr": "Marketing", "en": "Marketing"},
        "formal": {"ar": "رسمي", "fr": "Formel", "en": "Formal"},
        "creative": {"ar": "إبداعي", "fr": "Créatif", "en": "Creative"},
    }

    LENGTHS = {
        "short": {"ar": "قصير", "fr": "Court", "en": "Short", "tokens": 400},
        "medium": {"ar": "متوسط", "fr": "Moyen", "en": "Medium", "tokens": 1000},
        "long": {"ar": "طويل", "fr": "Long", "en": "Long", "tokens": 2000},
    }

    def __init__(self, groq_api_key=None, model="openai/gpt-oss-20b"):
        self.model = model
        self.client = None
        if GROQ_AVAILABLE:
            key = groq_api_key or os.environ.get("GROQ_API_KEY")
            if key:
                try:
                    self.client = Groq(api_key=key)
                except Exception:
                    self.client = None

    def _build_prompt(self, content_type, topic, tone, length, lang, audience, keywords):
        lang_names = {"ar": "العربية", "fr": "Français", "en": "English"}
        tone_desc = self.TONES[tone][lang]
        length_desc = self.LENGTHS[length][lang]
        type_desc = self.CONTENT_TYPES[content_type][lang]

        instructions = {
            "ar": {
                "article": f"اكتب مقال مدونة {length_desc} حول: {topic}. ابدأ بعنوان جذاب، ثم مقدمة، 3-4 أقسام، خاتمة، دعوة لاتخاذ إجراء.",
                "product": f"اكتب وصف منتج {length_desc} لـ: {topic}. ركّز على الفوائد، الميزات، والمشاعر.",
                "social": f"اكتب منشور سوشيال ميديا {length_desc} حول: {topic}. أضف emojis مناسبة و hashtags.",
                "email": f"اكتب بريداً إلكترونياً {length_desc} حول: {topic}. مع سطر موضوع، تحية، جسم، خاتمة.",
                "ad": f"اكتب نص إعلان {length_desc} لـ: {topic}. ركّز على الفائدة، أضف CTA قوي.",
                "video": f"اكتب سكريبت فيديو {length_desc} حول: {topic}. قسمه إلى مشاهد مع timings.",
            },
            "fr": {
                "article": f"Rédigez un article de blog {length_desc} sur: {topic}. Titre accrocheur, intro, 3-4 sections, conclusion, CTA.",
                "product": f"Rédigez une description produit {length_desc} pour: {topic}. Focus sur les bénéfices et les émotions.",
                "social": f"Rédigez un post réseaux sociaux {length_desc} sur: {topic}. Emojis et hashtags.",
                "email": f"Rédigez un email {length_desc} sur: {topic}. Objet, salutation, corps, signature.",
                "ad": f"Rédigez une publicité {length_desc} pour: {topic}. Bénéfice + CTA fort.",
                "video": f"Rédigez un script vidéo {length_desc} sur: {topic}. Scènes avec timings.",
            },
            "en": {
                "article": f"Write a {length_desc} blog article about: {topic}. Engaging title, intro, 3-4 sections, conclusion, CTA.",
                "product": f"Write a {length_desc} product description for: {topic}. Focus on benefits and emotions.",
                "social": f"Write a {length_desc} social media post about: {topic}. Include emojis and hashtags.",
                "email": f"Write a {length_desc} email about: {topic}. Subject, greeting, body, closing.",
                "ad": f"Write a {length_desc} ad copy for: {topic}. Benefit + strong CTA.",
                "video": f"Write a {length_desc} video script about: {topic}. Scenes with timings.",
            },
        }

        prompt = instructions[lang][content_type]
        if audience:
            prompt += f"\nالجمهور المستهدف / Audience: {audience}"
        if keywords:
            prompt += f"\nالكلمات المفتاحية / Keywords: {keywords}"

        system = f"""أنت كاتب محتوى محترف متعدد اللغات.
اكتب باللغة: {lang_names[lang]}
النبرة: {tone_desc}
النوع: {type_desc}
اكتب محتوى جاهزاً للنشر مباشرة — بدون مقدمات أو شرح."""

        return system, prompt

    def _fallback_content(self, content_type, topic, tone, length, lang):
        """قوالب احتياطية إن فشل AI"""
        templates = {
            "ar": {
                "article": f"# {topic}\n\n## مقدمة\nنتناول في هذا المقال موضوع {topic} بالتفصيل، مع التركيز على الجوانب العملية.\n\n## الأهمية\nيمثل {topic} أهمية كبيرة للشركات والمهنيين.\n\n## الخطوات\n1. التحضير\n2. التنفيذ\n3. المتابعة\n\n## الخاتمة\nتواصل معنا للمزيد.",
                "product": f"**{topic}**\n\nمنتج عالي الجودة يجمع بين الأداء والأناقة. مثالي لمن يبحث عن التميز.\n\n✅ جودة عالية\n✅ سعر مناسب\n✅ ضمان\n\nاطلبه الآن!",
                "social": f"✨ {topic} ✨\n\nاكتشف الجديد اليوم!\n\n#Maroc #Business #Innovation",
                "email": f"الموضوع: {topic}\n\nمرحباً،\n\nنود إخبارك عن {topic}.\n\nمع التحية",
                "ad": f"🎯 {topic}\n\nاحصل على أفضل النتائج!\n\n👉 اطلب الآن",
                "video": f"[0-3s] مشهد افتتاحي جذاب\n[3-10s] المشكلة\n[10-20s] الحل: {topic}\n[20-30s] CTA",
            },
            "fr": {
                "article": f"# {topic}\n\n## Introduction\nCet article aborde {topic} en détail.\n\n## Importance\n{topic} est essentiel pour les entreprises.\n\n## Conclusion\nContactez-nous.",
                "product": f"**{topic}**\n\nUn produit de qualité supérieure.\n\n✅ Qualité\n✅ Prix\n✅ Garantie",
                "social": f"✨ {topic} ✨\n\nDécouvrez la nouveauté!\n\n#Maroc #Business",
                "email": f"Objet: {topic}\n\nBonjour,\n\nNous voulons vous informer sur {topic}.\n\nCordialement",
                "ad": f"🎯 {topic}\n\nObtenez les meilleurs résultats!\n\n👉 Commandez",
                "video": f"[0-3s] Scène d'ouverture\n[3-10s] Problème\n[10-20s] Solution: {topic}\n[20-30s] CTA",
            },
            "en": {
                "article": f"# {topic}\n\n## Introduction\nThis article covers {topic} in detail.\n\n## Importance\n{topic} is essential for businesses.\n\n## Conclusion\nContact us.",
                "product": f"**{topic}**\n\nA premium quality product.\n\n✅ Quality\n✅ Price\n✅ Warranty",
                "social": f"✨ {topic} ✨\n\nDiscover what's new!\n\n#Morocco #Business",
                "email": f"Subject: {topic}\n\nHello,\n\nWe want to inform you about {topic}.\n\nBest regards",
                "ad": f"🎯 {topic}\n\nGet the best results!\n\n👉 Order now",
                "video": f"[0-3s] Opening scene\n[3-10s] Problem\n[10-20s] Solution: {topic}\n[20-30s] CTA",
            },
        }
        return templates[lang][content_type]

    def generate(self, content_type, topic, tone="professional", length="medium",
                 lang="ar", audience="", keywords=""):
        """توليد محتوى"""
        result = {
            "type": content_type,
            "type_label": self.CONTENT_TYPES[content_type][lang],
            "topic": topic,
            "tone": self.TONES[tone][lang],
            "length": self.LENGTHS[length][lang],
            "lang": lang,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        if self.client is not None:
            try:
                system, prompt = self._build_prompt(content_type, topic, tone, length, lang, audience, keywords)
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.8,
                    max_tokens=self.LENGTHS[length]["tokens"],
                )
                content = resp.choices[0].message.content
                if content and content.strip():
                    result["content"] = content.strip()
                    result["source"] = "AI"
                    return result
                result["content"] = self._fallback_content(content_type, topic, tone, length, lang)
                result["source"] = "قوالب (AI أرجع نصاً فارغاً)"
                return result
            except Exception as e:
                result["content"] = self._fallback_content(content_type, topic, tone, length, lang)
                result["source"] = f"قوالب (خطأ AI: {str(e)[:60]})"
                return result
        else:
            result["content"] = self._fallback_content(content_type, topic, tone, length, lang)
            result["source"] = "قوالب (AI غير متوفر)"
            return result

    def suggest_hashtags(self, topic, lang="ar", count=10):
        """اقتراح hashtags"""
        base = topic.replace(" ", "").replace("-", "")
        common = ["Maroc", "Morocco", "Business", "Marketing", "Innovation", "Digital"]
        specific = [
            f"{base}", f"{base}Maroc", f"{base}2026",
            "Entrepreneur", "Startup", "PME",
            "Success", "Growth",
        ]
        return [f"#{h}" for h in (common + specific)[:count]]

    def suggest_titles(self, topic, lang="ar", count=5):
        """اقتراح عناوين"""
        if lang == "ar":
            base = [
                f"دليل شامل: {topic} في 2026",
                f"5 أسرار لـ {topic} لم يخبرك بها أحد",
                f"كيف تنجح في {topic}؟ خطوة بخطوة",
                f"{topic}: من الصفر إلى الاحتراف",
                f"أخطاء شائعة في {topic} (وكيف تتجنبها)",
            ]
        elif lang == "fr":
            base = [
                f"Guide complet: {topic} en 2026",
                f"5 secrets sur {topic} que personne ne dit",
                f"Comment réussir en {topic}? Étape par étape",
                f"{topic}: de zéro à expert",
                f"Erreurs courantes en {topic} (et comment les éviter)",
            ]
        else:
            base = [
                f"Complete Guide: {topic} in 2026",
                f"5 Secrets about {topic} Nobody Tells You",
                f"How to Succeed in {topic}? Step by Step",
                f"{topic}: From Zero to Expert",
                f"Common Mistakes in {topic} (and How to Avoid Them)",
            ]
        return base[:count]


# ============ اختبار ============
if __name__ == "__main__":
    print("🧪 اختبار Content Writer Agent\n")
    agent = ContentWriterAgent()

    # اختبار 1: منشور سوشيال
    print("--- 1. منشور سوشيال ---")
    r = agent.generate("social", "خدمات المحاسبة للمقاولات الصغيرة",
                       tone="marketing", length="short", lang="ar")
    print(f"المصدر: {r['source']}")
    print(f"النوع: {r['type_label']} | النبرة: {r['tone']}")
    print(f"المحتوى:\n{r['content'][:300]}...")
    print()

    # اختبار 2: hashtags
    print("--- 2. Hashtags مقترحة ---")
    tags = agent.suggest_hashtags("محاسبة")
    print(" | ".join(tags[:8]))
    print()

    # اختبار 3: عناوين
    print("--- 3. عناوين مقترحة ---")
    titles = agent.suggest_titles("التسويق الرقمي")
    for t in titles:
        print(f"  • {t}")
