"""
Social Media Agent
وكيل السوشيال ميديا: منشورات، جداول نشر، تحليل هاشتاغات
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class SocialMediaAgent:
    """وكيل السوشيال ميديا متعدد المنصات"""

    PLATFORMS = {
        "facebook": {"ar": "فيسبوك", "fr": "Facebook", "en": "Facebook", "icon": "📘", "max_chars": 63206, "best_chars": 80},
        "instagram": {"ar": "إنستغرام", "fr": "Instagram", "en": "Instagram", "icon": "📷", "max_chars": 2200, "best_chars": 125},
        "linkedin": {"ar": "لينكدإن", "fr": "LinkedIn", "en": "LinkedIn", "icon": "💼", "max_chars": 3000, "best_chars": 150},
        "twitter": {"ar": "تويتر/X", "fr": "Twitter/X", "en": "Twitter/X", "icon": "🐦", "max_chars": 280, "best_chars": 240},
        "tiktok": {"ar": "تيك توك", "fr": "TikTok", "en": "TikTok", "icon": "🎵", "max_chars": 2200, "best_chars": 150},
        "whatsapp": {"ar": "واتساب", "fr": "WhatsApp", "en": "WhatsApp", "icon": "💬", "max_chars": 65536, "best_chars": 300},
    }

    POST_TYPES = {
        "promotion": {"ar": "ترويجي", "fr": "Promotionnel", "en": "Promotional", "icon": "🎯"},
        "educational": {"ar": "تعليمي", "fr": "Éducatif", "en": "Educational", "icon": "📚"},
        "engagement": {"ar": "تفاعلي", "fr": "Engagement", "en": "Engagement", "icon": "💬"},
        "announcement": {"ar": "إعلان", "fr": "Annonce", "en": "Announcement", "icon": "📢"},
        "story": {"ar": "قصة", "fr": "Story", "en": "Story", "icon": "📖"},
        "quote": {"ar": "اقتباس", "fr": "Citation", "en": "Quote", "icon": "💭"},
    }

    TONES = {
        "professional": {"ar": "احترافي", "fr": "Professionnel", "en": "Professional"},
        "casual": {"ar": "عفوي", "fr": "Décontracté", "en": "Casual"},
        "funny": {"ar": "فكاهي", "fr": "Drôle", "en": "Funny"},
        "inspiring": {"ar": "ملهم", "fr": "Inspirant", "en": "Inspiring"},
        "urgent": {"ar": "عاجل", "fr": "Urgent", "en": "Urgent"},
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

    def _build_prompt(self, platform, post_type, topic, tone, lang, target_audience):
        lang_names = {"ar": "العربية", "fr": "Français", "en": "English"}
        platform_info = self.PLATFORMS[platform]
        best_chars = platform_info["best_chars"]
        platform_name = platform_info[lang]

        type_map = {
            "ar": {
                "promotion": "منشور ترويجي يقنع بالشراء",
                "educational": "منشور تعليمي يقدم نصيحة مفيدة",
                "engagement": "منشور تفاعلي يطرح سؤالاً أو يدعو للتعليق",
                "announcement": "منشور إعلان عن خبر أو حدث",
                "story": "منشور قصصي يروي تجربة",
                "quote": "منشور اقتباس ملهم",
            },
            "fr": {
                "promotion": "post promotionnel qui incite à l'achat",
                "educational": "post éducatif avec un conseil utile",
                "engagement": "post engageant avec une question",
                "announcement": "post d'annonce d'une nouvelle",
                "story": "post narratif",
                "quote": "post de citation inspirante",
            },
            "en": {
                "promotion": "promotional post that drives purchase",
                "educational": "educational post with a tip",
                "engagement": "engaging post with a question",
                "announcement": "announcement post",
                "story": "storytelling post",
                "quote": "inspirational quote post",
            },
        }

        system = f"""أنت مسؤول سوشيال ميديا محترف.
المنصة: {platform_name}
الطول المثالي: ~{best_chars} حرف
النبرة: {self.TONES[tone][lang]}
النوع: {type_map[lang][post_type]}

اكتب منشوراً جاهزاً للنشر مباشرة باللغة {lang_names[lang]}.
- استخدم emojis
- أضف hashtags مناسبة في النهاية
- أضف CTA واضح إن أمكن
- لا تكتب شرحاً — فقط المنشور"""

        user = f"الموضوع: {topic}"
        if target_audience:
            user += f"\nالجمهور: {target_audience}"

        return system, user

    def _fallback_post(self, platform, post_type, topic, lang):
        templates = {
            "ar": {
                "promotion": f"🔥 عرض خاص!\n\n{topic}\n\nاطلب الآن قبل نفاد الكمية! 👇\n\n#عرض #تخفيضات",
                "educational": f"💡 نصيحة اليوم:\n\n{topic}\n\nاحفظ المنشور للمراجعة لاحقاً! 📌\n\n#نصائح #تعلم",
                "engagement": f"🤔 سؤال اليوم:\n\n{topic}\n\nشاركنا رأيك في التعليقات! 👇",
                "announcement": f"📢 إعلان:\n\n{topic}\n\nترقبوا المزيد! 🔔",
                "story": f"📖 قصة اليوم:\n\n{topic}\n\n#قصص #تجارب",
                "quote": f"💭 اقتباس:\n\n\"{topic}\"\n\nشاركنا اقتباسك المفضل! ✨",
            },
            "fr": {
                "promotion": f"🔥 Offre spéciale!\n\n{topic}\n\nCommandez maintenant! 👇\n\n#Promo",
                "educational": f"💡 Astuce du jour:\n\n{topic}\n\nEnregistrez ce post! 📌",
                "engagement": f"🤔 Question du jour:\n\n{topic}\n\nVotre avis en commentaire! 👇",
                "announcement": f"📢 Annonce:\n\n{topic}\n\nRestez connectés! 🔔",
                "story": f"📖 Histoire du jour:\n\n{topic}",
                "quote": f"💭 Citation:\n\n\"{topic}\"",
            },
            "en": {
                "promotion": f"🔥 Special offer!\n\n{topic}\n\nOrder now! 👇\n\n#Promo",
                "educational": f"💡 Today's tip:\n\n{topic}\n\nSave this post! 📌",
                "engagement": f"🤔 Question of the day:\n\n{topic}\n\nShare your thoughts! 👇",
                "announcement": f"📢 Announcement:\n\n{topic}\n\nStay tuned! 🔔",
                "story": f"📖 Today's story:\n\n{topic}",
                "quote": f"💭 Quote:\n\n\"{topic}\"",
            },
        }
        return templates[lang][post_type]

    def generate_post(self, platform, post_type, topic, tone="casual",
                      lang="ar", target_audience=""):
        """توليد منشور"""
        result = {
            "platform": platform,
            "platform_label": self.PLATFORMS[platform][lang],
            "platform_icon": self.PLATFORMS[platform]["icon"],
            "type": post_type,
            "type_label": self.POST_TYPES[post_type][lang],
            "type_icon": self.POST_TYPES[post_type]["icon"],
            "topic": topic,
            "tone": self.TONES[tone][lang],
            "lang": lang,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "best_chars": self.PLATFORMS[platform]["best_chars"],
        }

        if self.client is not None:
            try:
                system, user = self._build_prompt(platform, post_type, topic, tone, lang, target_audience)
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.85,
                    max_tokens=2000,
                )
                content = resp.choices[0].message.content
                if content and content.strip():
                    result["content"] = content.strip()
                    result["char_count"] = len(content.strip())
                    result["source"] = "AI"
                    return result
                result["content"] = self._fallback_post(platform, post_type, topic, lang)
                result["char_count"] = len(result["content"])
                result["source"] = "قوالب (AI أرجع نصاً فارغاً)"
                return result
            except Exception as e:
                result["content"] = self._fallback_post(platform, post_type, topic, lang)
                result["char_count"] = len(result["content"])
                result["source"] = f"قوالب (خطأ AI: {str(e)[:60]})"
                return result
        else:
            result["content"] = self._fallback_post(platform, post_type, topic, lang)
            result["char_count"] = len(result["content"])
            result["source"] = "قوالب (AI غير متوفر)"
            return result

    def generate_weekly_plan(self, topics, platforms, lang="ar"):
        """توليد خطة أسبوعية"""
        days_ar = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        days_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days = {"ar": days_ar, "fr": days_fr, "en": days_en}[lang]

        plan = []
        today = datetime.now()
        for i, day in enumerate(days):
            if i >= len(topics):
                break
            date = today + timedelta(days=i+1)
            plan.append({
                "day": day,
                "date": date.strftime("%Y-%m-%d"),
                "platform": platforms[i % len(platforms)],
                "platform_icon": self.PLATFORMS[platforms[i % len(platforms)]]["icon"],
                "topic": topics[i],
            })
        return plan

    def suggest_hashtags(self, topic, platform, lang="ar", count=15):
        """اقتراح hashtags حسب المنصة"""
        base = topic.replace(" ", "").replace("-", "")
        common = ["Maroc", "Morocco", "Business", "Marketing", "Digital"]
        specific = [base, f"{base}Maroc", f"{base}2026", "PME", "Startup", "Entrepreneur"]
        if platform == "linkedin":
            common = ["Leadership", "Business", "Innovation", "Career"] + common
        elif platform == "instagram":
            common = ["Insta", "Vibes", "Life"] + common
        return [f"#{h}" for h in (common + specific)[:count]]


# ============ اختبار ============
if __name__ == "__main__":
    print("🧪 اختبار Social Media Agent\n")
    agent = SocialMediaAgent()

    # 1. منشور LinkedIn
    print("--- 1. منشور LinkedIn ---")
    r = agent.generate_post("linkedin", "educational", "5 خطوات لتحسين إنتاجية فريقك",
                            tone="professional", lang="ar", target_audience="مدراء فرق")
    print(f"المصدر: {r['source']} | المنصة: {r['platform_label']}")
    print(f"الأحرف: {r['char_count']} (المثالي: {r['best_chars']})")
    print(f"المحتوى:\n{r['content'][:300]}...")
    print()

    # 2. hashtags
    print("--- 2. Hashtags لـ Instagram ---")
    print(" ".join(agent.suggest_hashtags("محاسبة", "instagram")[:10]))
