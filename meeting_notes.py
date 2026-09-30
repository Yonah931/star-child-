"""
Meeting Notes Agent
وكيل محاضر الاجتماعات: تلخيص، قرارات، مهام، حضور
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


class MeetingNotesAgent:
    """وكيل محاضر الاجتماعات متعدد اللغات"""

    MEETING_TYPES = {
        "general": {"ar": "اجتماع عام", "fr": "Réunion générale", "en": "General Meeting", "icon": "👥"},
        "sales": {"ar": "اجتماع مبيعات", "fr": "Réunion ventes", "en": "Sales Meeting", "icon": "💰"},
        "project": {"ar": "اجتماع مشروع", "fr": "Réunion projet", "en": "Project Meeting", "icon": "📊"},
        "one_on_one": {"ar": "اجتماع فردي", "fr": "Entretien individuel", "en": "1-on-1", "icon": "👤"},
        "board": {"ar": "مجلس الإدارة", "fr": "Conseil d'administration", "en": "Board Meeting", "icon": "🏛️"},
        "standup": {"ar": "اجتماع يومي", "fr": "Stand-up", "en": "Stand-up", "icon": "⚡"},
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

    def _build_prompt(self, transcript, meeting_type, lang, title, date):
        lang_names = {"ar": "العربية", "fr": "Français", "en": "English"}
        type_label = self.MEETING_TYPES[meeting_type][lang]

        system = f"""أنت مساعد محاضر اجتماعات محترف.
اكتب محضر اجتماع منظم باللغة {lang_names[lang]}.
نوع الاجتماع: {type_label}

استخرج:
1. 📋 ملخص تنفيذي (3-5 أسطر)
2. 💡 النقاط الرئيسية المناقشة
3. ✅ القرارات المتخذة
4. 📌 المهام مع المسؤولين والمواعيد
5. ⚠️ المخاطر أو القضايا المعلقة

تنسيق واضح بعناوين ونقاط. لا تكتب شرحاً — فقط المحضر."""

        user = f"عنوان الاجتماع: {title or 'غير محدد'}\nالتاريخ: {date or datetime.now().strftime('%Y-%m-%d')}\n\nنص الاجتماع:\n{transcript}"

        return system, user

    def _fallback_minutes(self, transcript, meeting_type, lang, title, date):
        lines = transcript.strip().split("\n")
        bullets = "\n".join([f"- {l.strip()}" for l in lines if l.strip()][:10])
        templates = {
            "ar": f"""# محضر الاجتماع: {title or 'غير محدد'}
**التاريخ:** {date or datetime.now().strftime('%Y-%m-%d')}

## 📋 ملخص
تم عقد اجتماع لمناقشة النقاط التالية.

## 💡 النقاط الرئيسية
{bullets}

## ✅ القرارات
- (يُستكمل يدوياً)

## 📌 المهام
- (تُحدد المهام والمسؤولين)

## ⚠️ معلقات
- (لا يوجد)""",
            "fr": f"""# Compte-rendu: {title or 'Sans titre'}
**Date:** {date or datetime.now().strftime('%Y-%m-%d')}

## 📋 Résumé
Réunion tenue pour discuter des points suivants.

## 💡 Points clés
{bullets}

## ✅ Décisions
- (à compléter)

## 📌 Actions
- (à compléter)""",
            "en": f"""# Meeting Minutes: {title or 'Untitled'}
**Date:** {date or datetime.now().strftime('%Y-%m-%d')}

## 📋 Summary
Meeting held to discuss the following points.

## 💡 Key Points
{bullets}

## ✅ Decisions
- (to be completed)

## 📌 Action Items
- (to be completed)""",
        }
        return templates[lang]

    def generate_minutes(self, transcript, meeting_type="general", lang="ar",
                         title="", date=""):
        """توليد محضر الاجتماع"""
        result = {
            "type": meeting_type,
            "type_label": self.MEETING_TYPES[meeting_type][lang],
            "title": title or "اجتماع",
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "lang": lang,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        if self.client is not None:
            try:
                system, user = self._build_prompt(transcript, meeting_type, lang, title, date)
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.5,
                    max_tokens=2500,
                )
                content = resp.choices[0].message.content
                if content and content.strip():
                    result["minutes"] = content.strip()
                    result["source"] = "AI"
                    return result
                result["minutes"] = self._fallback_minutes(transcript, meeting_type, lang, title, date)
                result["source"] = "قوالب (AI أرجع نصاً فارغاً)"
                return result
            except Exception as e:
                result["minutes"] = self._fallback_minutes(transcript, meeting_type, lang, title, date)
                result["source"] = f"قوالب (خطأ AI: {str(e)[:60]})"
                return result
        else:
            result["minutes"] = self._fallback_minutes(transcript, meeting_type, lang, title, date)
            result["source"] = "قوالب (AI غير متوفر)"
            return result

    def extract_action_items(self, transcript, lang="ar"):
        """استخراج المهام فقط (سريع)"""
        system = f"""استخرج فقط المهام من نص الاجتماع.
اكتب كل مهمة في سطر بصيغة: [المسؤول] المهمة (الموعد)
باللغة: {"العربية" if lang == "ar" else "Français" if lang == "fr" else "English"}
لا تكتب شيئاً آخر."""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": transcript[:3000]},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return "⚠️ تعذر الاستخراج (تحقق من الاتصال)"


# ============ اختبار ============
if __name__ == "__main__":
    print("🧪 اختبار Meeting Notes Agent\n")
    agent = MeetingNotesAgent()

    transcript = """
    محمد: نبدأ الاجتماع بمراجعة أداء الشهر الماضي. المبيعات زادت 15%.
    سارة: لكن التأخير في التسليم مشكلة. نحتاج حل.
    محمد: موافق. سارة، تحديث نظام المخزون قبل نهاية الشهر.
    سارة: تمام، سأبدأ الأسبوع القادم.
    أحمد: الميزانية تحتاج مراجعة. سأجهز التقرير المالي.
    محمد: ممتاز. قرار: نرفع ميزانية التسويق 20%.
    """

    print("--- محضر الاجتماع (AI) ---")
    r = agent.generate_minutes(transcript, "general", lang="ar", title="اجتماع شهري")
    print(f"المصدر: {r['source']}")
    print(f"النوع: {r['type_label']}")
    print(f"المحضر:\n{r['minutes'][:600]}...")
    print()
    print("--- استخراج المهام ---")
    print(agent.extract_action_items(transcript, lang="ar"))
