"""
Email Agent
وكيل البريد الإلكتروني: ردود، حملات، متابعة، دعوات
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


class EmailAgent:
    """وكيل البريد الإلكتروني متعدد اللغات"""

    EMAIL_TYPES = {
        "reply": {"ar": "رد على عميل", "fr": "Réponse client", "en": "Customer Reply", "icon": "↩️"},
        "campaign": {"ar": "حملة تسويقية", "fr": "Campagne marketing", "en": "Marketing Campaign", "icon": "📢"},
        "followup": {"ar": "بريد متابعة", "fr": "Email de suivi", "en": "Follow-up", "icon": "🔔"},
        "invitation": {"ar": "دعوة", "fr": "Invitation", "en": "Invitation", "icon": "🎫"},
        "apology": {"ar": "اعتذار", "fr": "Excuses", "en": "Apology", "icon": "🙏"},
        "welcome": {"ar": "ترحيب بعميل جديد", "fr": "Bienvenue", "en": "Welcome", "icon": "🎉"},
        "reminder": {"ar": "تذكير", "fr": "Rappel", "en": "Reminder", "icon": "⏰"},
    }

    TONES = {
        "professional": {"ar": "احترافي", "fr": "Professionnel", "en": "Professional"},
        "friendly": {"ar": "ودي", "fr": "Amical", "en": "Friendly"},
        "formal": {"ar": "رسمي", "fr": "Formel", "en": "Formal"},
        "apologetic": {"ar": "اعتذاري", "fr": "Apologétique", "en": "Apologetic"},
        "persuasive": {"ar": "إقناعي", "fr": "Persuasif", "en": "Persuasive"},
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

    def _build_prompt(self, email_type, subject, context, tone, lang, recipient, sender):
        lang_names = {"ar": "العربية", "fr": "Français", "en": "English"}
        tone_desc = self.TONES[tone][lang]
        type_desc = self.EMAIL_TYPES[email_type][lang]

        instructions = {
            "ar": {
                "reply": f"اكتب رداً على بريد عميل بخصوص: {subject}",
                "campaign": f"اكتب بريد حملة تسويقية حول: {subject}",
                "followup": f"اكتب بريد متابعة بخصوص: {subject}",
                "invitation": f"اكتب دعوة لـ: {subject}",
                "apology": f"اكتب بريد اعتذار بخصوص: {subject}",
                "welcome": f"اكتب بريد ترحيب بعميل جديد بخصوص: {subject}",
                "reminder": f"اكتب بريد تذكير بخصوص: {subject}",
            },
            "fr": {
                "reply": f"Rédigez une réponse à un client concernant: {subject}",
                "campaign": f"Rédigez un email de campagne marketing sur: {subject}",
                "followup": f"Rédigez un email de suivi concernant: {subject}",
                "invitation": f"Rédigez une invitation pour: {subject}",
                "apology": f"Rédigez des excuses concernant: {subject}",
                "welcome": f"Rédigez un email de bienvenue sur: {subject}",
                "reminder": f"Rédigez un rappel concernant: {subject}",
            },
            "en": {
                "reply": f"Write a reply to a customer regarding: {subject}",
                "campaign": f"Write a marketing campaign email about: {subject}",
                "followup": f"Write a follow-up email regarding: {subject}",
                "invitation": f"Write an invitation for: {subject}",
                "apology": f"Write an apology email regarding: {subject}",
                "welcome": f"Write a welcome email about: {subject}",
                "reminder": f"Write a reminder email regarding: {subject}",
            },
        }

        prompt = instructions[lang][email_type]
        if context:
            prompt += f"\n\nالسياق / Context:\n{context}"

        system = f"""أنت كاتب بريد إلكتروني محترف.
اكتب باللغة: {lang_names[lang]}
النبرة: {tone_desc}
النوع: {type_desc}
{'المرسل: ' + sender if sender else ''}
{'المستقبل: ' + recipient if recipient else ''}

اكتب البريد كاملاً بتنسيق:
Subject: [الموضوع]
---
[جسم البريد]

كن مختصراً وواضحاً ومهنياً."""

        return system, prompt

    def _fallback_email(self, email_type, subject, lang, recipient, sender):
        sender_line = f"من: {sender}" if sender else ""
        recipient_line = f"إلى: {recipient}" if recipient else ""
        templates = {
            "ar": {
                "reply": f"الموضوع: رد بخصوص {subject}\n\nمرحباً،\n\nشكراً لتواصلك بخصوص {subject}. نود إعلامك بأننا نعمل على الأمر وسنوافيك بالتفاصيل قريباً.\n\nمع التحية",
                "campaign": f"الموضوع: عرض خاص — {subject}\n\nمرحباً،\n\nيسعدنا أن نقدم لك عرضاً خاصاً بخصوص {subject}.\n\nلا تفوّت الفرصة!\n\nاطلب الآن",
                "followup": f"الموضوع: متابعة — {subject}\n\nمرحباً،\n\nنود متابعة ما تم بخصوص {subject}. هل لديك أي استفسارات؟\n\nمع التحية",
                "invitation": f"الموضوع: دعوة — {subject}\n\nمرحباً،\n\nيسعدنا دعوتك لـ {subject}.\n\nيرجى تأكيد الحضور.",
                "apology": f"الموضوع: اعتذار — {subject}\n\nمرحباً،\n\nنعتذر بشدة عن {subject}. نأخذ الأمر بجدية وسنعمل على تصحيحه فوراً.\n\nمع التحية",
                "welcome": f"الموضوع: مرحباً بك!\n\nمرحباً،\n\nنرحب بك في {subject}. نتمنى لك تجربة رائعة!\n\nفريق العمل",
                "reminder": f"الموضوع: تذكير — {subject}\n\nمرحباً،\n\nنذكرك بخصوص {subject}.\n\nمع التحية",
            },
            "fr": {
                "reply": f"Objet: Réponse concernant {subject}\n\nBonjour,\n\nMerci pour votre message. Nous travaillons sur votre demande.\n\nCordialement",
                "campaign": f"Objet: Offre spéciale — {subject}\n\nBonjour,\n\nNous avons le plaisir de vous offrir une offre spéciale.\n\nCommandez maintenant",
                "followup": f"Objet: Suivi — {subject}\n\nBonjour,\n\nNous faisons suite à {subject}.\n\nCordialement",
                "invitation": f"Objet: Invitation — {subject}\n\nBonjour,\n\nNous vous invitons à {subject}.\n\nMerci de confirmer.",
                "apology": f"Objet: Excuses — {subject}\n\nBonjour,\n\nNous vous prions de nous excuser.\n\nCordialement",
                "welcome": f"Objet: Bienvenue!\n\nBonjour,\n\nBienvenue chez {subject}.\n\nL'équipe",
                "reminder": f"Objet: Rappel — {subject}\n\nBonjour,\n\nNous vous rappelons {subject}.\n\nCordialement",
            },
            "en": {
                "reply": f"Subject: Reply regarding {subject}\n\nHello,\n\nThank you for your message. We're working on it.\n\nBest regards",
                "campaign": f"Subject: Special Offer — {subject}\n\nHello,\n\nWe have a special offer for you.\n\nOrder now",
                "followup": f"Subject: Follow-up — {subject}\n\nHello,\n\nFollowing up on {subject}.\n\nBest regards",
                "invitation": f"Subject: Invitation — {subject}\n\nHello,\n\nWe invite you to {subject}.\n\nPlease confirm.",
                "apology": f"Subject: Apology — {subject}\n\nHello,\n\nWe sincerely apologize.\n\nBest regards",
                "welcome": f"Subject: Welcome!\n\nHello,\n\nWelcome to {subject}.\n\nTeam",
                "reminder": f"Subject: Reminder — {subject}\n\nHello,\n\nReminder about {subject}.\n\nBest regards",
            },
        }
        return templates[lang][email_type]

    def generate(self, email_type, subject, context="", tone="professional",
                 lang="ar", recipient="", sender=""):
        """توليد بريد إلكتروني"""
        result = {
            "type": email_type,
            "type_label": self.EMAIL_TYPES[email_type][lang],
            "subject": subject,
            "tone": self.TONES[tone][lang],
            "lang": lang,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        if self.client is not None:
            try:
                system, prompt = self._build_prompt(email_type, subject, context, tone, lang, recipient, sender)
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1200,
                )
                content = resp.choices[0].message.content
                if content and content.strip():
                    result["content"] = content.strip()
                    result["source"] = "AI"
                    return result
                result["content"] = self._fallback_email(email_type, subject, lang, recipient, sender)
                result["source"] = "قوالب (AI أرجع نصاً فارغاً)"
                return result
            except Exception as e:
                result["content"] = self._fallback_email(email_type, subject, lang, recipient, sender)
                result["source"] = f"قوالب (خطأ AI: {str(e)[:60]})"
                return result
        else:
            result["content"] = self._fallback_email(email_type, subject, lang, recipient, sender)
            result["source"] = "قوالب (AI غير متوفر)"
            return result

    def suggest_subjects(self, topic, lang="ar", count=5):
        """اقتراح عناوين بريد"""
        if lang == "ar":
            base = [
                f"عرض خاص: {topic}",
                f"تحديث مهم بخصوص {topic}",
                f"هل أنت مستعد لـ {topic}؟",
                f"خبر سار بخصوص {topic}",
                f"لا تفوّت: {topic} الآن",
            ]
        elif lang == "fr":
            base = [
                f"Offre spéciale: {topic}",
                f"Mise à jour importante: {topic}",
                f"Êtes-vous prêt pour {topic}?",
                f"Bonne nouvelle: {topic}",
                f"Ne manquez pas: {topic}",
            ]
        else:
            base = [
                f"Special offer: {topic}",
                f"Important update: {topic}",
                f"Are you ready for {topic}?",
                f"Good news: {topic}",
                f"Don't miss: {topic}",
            ]
        return base[:count]


# ============ اختبار ============
if __name__ == "__main__":
    print("🧪 اختبار Email Agent\n")
    agent = EmailAgent()

    # اختبار 1
    print("--- 1. رد على عميل ---")
    r = agent.generate("reply", "استفسار عن الطلب",
                       context="العميل يسأل عن موعد وصول طلبه",
                       tone="friendly", lang="ar", recipient="محمد")
    print(f"المصدر: {r['source']}")
    print(f"النوع: {r['type_label']} | النبرة: {r['tone']}")
    print(f"المحتوى:\n{r['content'][:400]}...")
    print()

    # اختبار 2
    print("--- 2. عناوين مقترحة ---")
    for s in agent.suggest_subjects("خصم 30%"):
        print(f"  • {s}")
