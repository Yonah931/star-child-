"""
Customer Support Agent
وكيل خدمة العملاء: تصنيف التذاكر، توليد الردود، اقتراح الإجراءات، كشف التصعيد
"""
import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class CustomerSupportAgent:
    """وكيل خدمة العملاء متعدد اللغات"""

    # ============ تصنيفات التذاكر ============
    TICKET_TYPES = {
        "complaint": {"ar": "شكوى", "fr": "Réclamation", "en": "Complaint", "icon": "😠"},
        "inquiry": {"ar": "استفسار", "fr": "Demande d'information", "en": "Inquiry", "icon": "❓"},
        "request": {"ar": "طلب خدمة", "fr": "Demande de service", "en": "Service Request", "icon": "📋"},
        "return": {"ar": "إرجاع/استبدال", "fr": "Retour/Échange", "en": "Return/Exchange", "icon": "↩️"},
        "technical": {"ar": "مشكلة تقنية", "fr": "Problème technique", "en": "Technical Issue", "icon": "🔧"},
        "billing": {"ar": "مشكلة فواتير", "fr": "Problème de facturation", "en": "Billing Issue", "icon": "💳"},
        "feedback": {"ar": "اقتراح/رأي", "fr": "Suggestion/Avis", "en": "Feedback", "icon": "💡"},
    }

    # ============ الأولويات ============
    PRIORITIES = {
        "urgent": {"ar": "عاجل", "fr": "Urgent", "en": "Urgent", "color": "#e74c3c", "icon": "🔴"},
        "high": {"ar": "مرتفعة", "fr": "Haute", "en": "High", "color": "#e67e22", "icon": "🟠"},
        "medium": {"ar": "متوسطة", "fr": "Moyenne", "en": "Medium", "color": "#f39c12", "icon": "🟡"},
        "low": {"ar": "منخفضة", "fr": "Basse", "en": "Low", "color": "#27ae60", "icon": "🟢"},
    }

    # ============ المشاعر ============
    SENTIMENTS = {
        "angry": {"ar": "غاضب", "fr": "En colère", "en": "Angry", "emoji": "😡"},
        "frustrated": {"ar": "محبط", "fr": "Frustré", "en": "Frustrated", "emoji": "😤"},
        "neutral": {"ar": "محايد", "fr": "Neutre", "en": "Neutral", "emoji": "😐"},
        "happy": {"ar": "راضٍ", "fr": "Content", "en": "Happy", "emoji": "😊"},
    }

    # ============ كلمات مفتاحية للتصنيف (بدون AI) ============
    KEYWORDS = {
        "complaint": [
            "شكوى", "سيء", "فظيع", "مشكلة", "غير راض", "احتجاج", "تذمر",
            "réclamation", "plainte", "mauvais", "problème", "insatisfait",
            "complaint", "bad", "terrible", "problem", "dissatisfied",
        ],
        "inquiry": [
            "استفسار", "سؤال", "أريد معرفة", "كيف", "متى", "أين", "هل",
            "question", "renseignement", "comment", "quand", "où", "est-ce",
            "inquiry", "question", "how", "when", "where", "do you",
        ],
        "return": [
            "إرجاع", "استبدال", "استرداد", "أرجع", "أعيد",
            "retour", "échange", "remboursement", "retourner",
            "return", "exchange", "refund", "returning",
        ],
        "technical": [
            "لا يعمل", "خطأ", "تعطل", "لا يفتح", "بطيء", "مشكلة تقنية",
            "ne marche pas", "erreur", "bug", "planté", "lent",
            "not working", "error", "bug", "crashed", "slow",
        ],
        "billing": [
            "فاتورة", "دفع", "مبلغ", "رسوم", "استرداد مال", "ثمن",
            "facture", "paiement", "montant", "frais", "prix",
            "invoice", "payment", "amount", "charge", "price",
        ],
        "feedback": [
            "اقتراح", "رأي", "ملاحظة", "فكرة", "أقترح",
            "suggestion", "avis", "idée", "propose",
            "suggestion", "feedback", "idea", "propose",
        ],
    }

    # ============ كلمات الأولوية العاجلة ============
    URGENT_WORDS = [
        "عاجل", "فوراً", "فوري", "فورية", "الآن", "بسرعة", "طوارئ", "خسارة", "قانوني", "محامي",
        "urgent", "immédiatement", "tout de suite", "avocat", "perte",
        "urgent", "immediately", "right now", "lawyer", "loss",
    ]

    # ============ كلمات التصعيد ============
    ESCALATION_WORDS = [
        "قانوني", "محامي", "قضية", "محكمة", "استقالة", "إلغاء العقد",
        "juridique", "avocat", "tribunal", "annulation", "résiliation",
        "legal", "lawyer", "court", "cancel", "termination",
    ]

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

    # ============ 1. تصنيف التذكرة (Rule-based) ============
    def _classify_by_keywords(self, text):
        """تصنيف بالقواعد — لا يحتاج AI"""
        text_lower = text.lower()
        scores = {}
        for ttype, words in self.KEYWORDS.items():
            score = sum(1 for w in words if w in text_lower)
            if score > 0:
                scores[ttype] = score

        if not scores:
            return "inquiry", 0.5  # افتراضي

        best_type = max(scores, key=scores.get)
        confidence = min(0.5 + scores[best_type] * 0.15, 0.95)
        return best_type, round(confidence, 2)

    def _detect_priority(self, text):
        text_lower = text.lower()
        # فحص كلمات عاجلة
        if any(w in text_lower for w in self.URGENT_WORDS):
            return "urgent"
        # طول النص (نص طويل = أولوية أعلى)
        if len(text) > 300:
            return "high"
        if len(text) > 150:
            return "medium"
        return "low"

    def _detect_sentiment(self, text):
        text_lower = text.lower()
        angry = ["غاضب", "فظيع", "سيء جداً", "احتيال", "سرقة",
                 "furieux", "inadmissible", "scandale", "vol",
                 "furious", "unacceptable", "scam", "steal"]
        frustrated = ["محبط", "تعبت", "مرهق", "زعلان", "غير راض",
                      "frustré", "fatigué", "déçu", "mécontent",
                      "frustrated", "tired", "disappointed", "unsatisfied"]
        happy = ["شكراً", "ممتاز", "رائع", "سعيد", "أحببت",
                 "merci", "excellent", "parfait", "content",
                 "thanks", "great", "perfect", "love"]

        if any(w in text_lower for w in angry):
            return "angry"
        if any(w in text_lower for w in frustrated):
            return "frustrated"
        if any(w in text_lower for w in happy):
            return "happy"
        return "neutral"

    def classify_ticket(self, text, lang="ar"):
        """تصنيف تذكرة: النوع، الأولوية، المشاعر، التصعيد"""
        ticket_type, confidence = self._classify_by_keywords(text)
        priority = self._detect_priority(text)
        sentiment = self._detect_sentiment(text)
        escalation = self.detect_escalation(text)

        return {
            "text": text,
            "type": ticket_type,
            "type_label": self.TICKET_TYPES[ticket_type][lang],
            "type_icon": self.TICKET_TYPES[ticket_type]["icon"],
            "confidence": confidence,
            "priority": priority,
            "priority_label": self.PRIORITIES[priority][lang],
            "priority_icon": self.PRIORITIES[priority]["icon"],
            "priority_color": self.PRIORITIES[priority]["color"],
            "sentiment": sentiment,
            "sentiment_label": self.SENTIMENTS[sentiment][lang],
            "sentiment_emoji": self.SENTIMENTS[sentiment]["emoji"],
            "needs_escalation": escalation["needs_escalation"],
            "escalation_reason": escalation["reason"],
            "classified_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # ============ 2. كشف التصعيد ============
    def detect_escalation(self, text):
        text_lower = text.lower()
        for w in self.ESCALATION_WORDS:
            if w in text_lower:
                return {
                    "needs_escalation": True,
                    "reason": f"كلمة مفتاحية: '{w}'",
                }
        return {"needs_escalation": False, "reason": ""}

    # ============ 3. توليد الرد ============
    def _fallback_response(self, ticket, tone, lang):
        """رد احتياطي بلا AI"""
        ttype = ticket["type"]
        client_name = ticket.get("client_name", "")
        greeting = {
            "ar": f"عزيزي {client_name}," if client_name else "عزيزنا العميل،",
            "fr": f"Cher {client_name}," if client_name else "Cher client,",
            "en": f"Dear {client_name}," if client_name else "Dear customer,",
        }[lang]

        body_templates = {
            "ar": {
                "complaint": "نأسف بشدة لانزعاجك. نأخذ شكواك على محمل الجد وسنراجع الأمر فوراً. سيتواصل معك فريقنا خلال 24 ساعة.",
                "inquiry": "شكراً لتواصلك. سعداء بمساعدتك. سنجيب على استفسارك بالتفصيل خلال 24 ساعة.",
                "return": "يسعدنا مساعدتك في عملية الإرجاع/الاستبدال. يرجى إرسال رقم الطلب وصورة المنتج.",
                "technical": "نأسف للمشكلة التقنية. فريقنا الفني سيتواصل معك خلال 24 ساعة لحل الأمر.",
                "billing": "شكراً لإبلاغنا. سنراجع سجل الفواتير وسنرد عليك بالتفصيل خلال 24 ساعة.",
                "feedback": "شكراً لاقتراحك القيم! نقدّر مشاركتك ونعمل باستمرار على التحسين.",
                "request": "استلمنا طلبك بنجاح. سيتواصل معك فريقنا خلال 24 ساعة لترتيب التفاصيل.",
            },
            "fr": {
                "complaint": "Nous sommes désolés pour ce désagrément. Nous prenons votre réclamation très au sérieux et reviendrons vers vous sous 24h.",
                "inquiry": "Merci de nous avoir contactés. Nous serons ravis de vous aider et vous répondrons en détail sous 24h.",
                "return": "Nous vous accompagnons pour votre retour/échange. Merci d'envoyer votre numéro de commande et une photo.",
                "technical": "Nous sommes désolés pour ce problème technique. Notre équipe vous contactera sous 24h.",
                "billing": "Merci de nous avoir informés. Nous allons vérifier votre facturation et vous répondre sous 24h.",
                "feedback": "Merci pour votre suggestion précieuse ! Nous apprécions votre contribution.",
                "request": "Votre demande a bien été reçue. Notre équipe vous contactera sous 24h.",
            },
            "en": {
                "complaint": "We are very sorry for this inconvenience. We take your complaint seriously and will respond within 24 hours.",
                "inquiry": "Thank you for contacting us. We'll be happy to help and will reply in detail within 24 hours.",
                "return": "We'll help you with the return/exchange. Please send your order number and a photo.",
                "technical": "We're sorry for this technical issue. Our team will contact you within 24 hours.",
                "billing": "Thank you for letting us know. We'll review your billing and reply within 24 hours.",
                "feedback": "Thank you for your valuable suggestion! We appreciate your input.",
                "request": "We've received your request. Our team will contact you within 24 hours.",
            },
        }

        closing = {
            "ar": "مع تحياتنا،\nفريق خدمة العملاء",
            "fr": "Cordialement,\nL'équipe du service client",
            "en": "Best regards,\nCustomer Support Team",
        }[lang]

        return f"{greeting}\n\n{body_templates[lang][ttype]}\n\n{closing}"

    def _ai_response(self, ticket, tone, lang):
        """رد بـ Groq AI"""
        tone_map = {
            "formal": {"ar": "رسمي ومهني", "fr": "formel et professionnel", "en": "formal and professional"},
            "friendly": {"ar": "ودي ودافئ", "fr": "amical et chaleureux", "en": "friendly and warm"},
            "apologetic": {"ar": "متعاطف واعتذاري", "fr": "compatissant et apologétique", "en": "empathetic and apologetic"},
        }

        lang_names = {"ar": "العربية", "fr": "Français", "en": "English"}

        system_prompt = (
            f"You are a professional customer support agent. "
            f"Write a response in {lang_names[lang]}, tone: {tone_map[tone][lang]}. "
            f"Ticket type: {ticket['type_label']}. "
            f"Priority: {ticket['priority_label']}. "
            f"Be concise (max 120 words). Include: greeting, acknowledgment, action, closing. "
            f"If escalation needed, mention a manager will contact them."
        )

        user_prompt = f"Client message:\n{ticket['text']}\n\nClient name: {ticket.get('client_name', 'غير محدد')}"

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        content = resp.choices[0].message.content
        if not content or not content.strip():
            # احتياطي: استخدم القوالب إن كان الرد فارغاً
            return None
        return content.strip()

    def generate_response(self, ticket, tone="formal", lang="ar"):
        """توليد رد جاهز للإرسال"""
        if self.client is not None:
            try:
                text = self._ai_response(ticket, tone, lang)
                if text:
                    return {"text": text, "source": "AI"}
                else:
                    fb = self._fallback_response(ticket, tone, lang)
                    return {"text": fb, "source": "قوالب (AI أرجع نصاً فارغاً)"}
            except Exception as e:
                text = self._fallback_response(ticket, tone, lang)
                return {"text": text, "source": f"قوالب (خطأ AI: {str(e)[:50]})"}
        else:
            text = self._fallback_response(ticket, tone, lang)
            return {"text": text, "source": "قوالب (AI غير متوفر)"}

    # ============ 4. اقتراح الإجراءات ============
    def suggest_actions(self, ticket, lang="ar"):
        ttype = ticket["type"]
        priority = ticket["priority"]
        actions = []

        # إجراءات حسب النوع
        type_actions = {
            "ar": {
                "complaint": ["📞 اتصال بالعميل خلال 24 ساعة", "🔍 مراجعة تفاصيل الشكوى", "📝 تسجيل في قاعدة البيانات", "✉️ إرسال اعتذار مكتوب"],
                "inquiry": ["📧 إرسال رد تفصيلي", "📎 إرفاق المستندات المطلوبة", "☎️ متابعة بعد 48 ساعة"],
                "return": ["📋 التحقق من رقم الطلب", "📦 ترتيب شحن الإرجاع", "💰 معالجة الاسترداد"],
                "technical": ["🔧 تعيين مهندس دعم", "📊 فحص سجلات النظام", "🧪 اختبار الحل المقترح"],
                "billing": ["💳 مراجعة سجل الدفع", "📄 التحقق من الفاتورة", "💰 تعديل أو استرداد"],
                "feedback": ["📊 توثيق الاقتراح", "👥 مشاركته مع الفريق", "✉️ شكر العميل"],
                "request": ["📋 تسجيل الطلب", "👤 تعيين مسؤول", "⏰ تحديد موعد التنفيذ"],
            },
            "fr": {
                "complaint": ["📞 Appel client sous 24h", "🔍 Analyser la réclamation", "📝 Enregistrer dans la base", "✉️ Envoyer des excuses écrites"],
                "inquiry": ["📧 Envoyer une réponse détaillée", "📎 Joindre les documents", "☎️ Suivi après 48h"],
                "return": ["📋 Vérifier le numéro de commande", "📦 Organiser le retour", "💰 Traiter le remboursement"],
                "technical": ["🔧 Assigner un technicien", "📊 Examiner les logs", "🧪 Tester la solution"],
                "billing": ["💳 Vérifier l'historique de paiement", "📄 Contrôler la facture", "💰 Ajuster ou rembourser"],
                "feedback": ["📊 Documenter la suggestion", "👥 Partager avec l'équipe", "✉️ Remercier le client"],
                "request": ["📋 Enregistrer la demande", "👤 Assigner un responsable", "⏰ Fixer une échéance"],
            },
            "en": {
                "complaint": ["📞 Call client within 24h", "🔍 Review complaint details", "📝 Log in database", "✉️ Send written apology"],
                "inquiry": ["📧 Send detailed reply", "📎 Attach documents", "☎️ Follow up after 48h"],
                "return": ["📋 Verify order number", "📦 Arrange return shipping", "💰 Process refund"],
                "technical": ["🔧 Assign support engineer", "📊 Check system logs", "🧪 Test solution"],
                "billing": ["💳 Review payment history", "📄 Check invoice", "💰 Adjust or refund"],
                "feedback": ["📊 Document suggestion", "👥 Share with team", "✉️ Thank client"],
                "request": ["📋 Register request", "👤 Assign owner", "⏰ Set deadline"],
            },
        }

        actions = list(type_actions[lang][ttype])

        # إجراءات إضافية للأولوية
        if priority == "urgent":
            extra = {
                "ar": "🚨 إبلاغ المدير فوراً",
                "fr": "🚨 Informer le manager immédiatement",
                "en": "🚨 Notify manager immediately",
            }[lang]
            actions.insert(0, extra)

        if ticket.get("needs_escalation"):
            extra = {
                "ar": "⚖️ تحويل للقسم القانوني",
                "fr": "⚖️ Transférer au service juridique",
                "en": "⚖️ Escalate to legal department",
            }[lang]
            actions.append(extra)

        return actions

    # ============ 5. الأسئلة الشائعة ============
    def get_faq(self, category=None, lang="ar"):
        faqs = {
            "ar": [
                {"q": "كيف أطلب استرداد؟", "a": "تواصل معنا برقم الطلب خلال 30 يوماً من الشراء."},
                {"q": "ما هي مدة الشحن؟", "a": "2-5 أيام عمل داخل المغرب."},
                {"q": "هل يمكنني تغيير طلبي؟", "a": "نعم، قبل الشحن — تواصل معنا فوراً."},
                {"q": "كيف أتتبع طلبي؟", "a": "ستصلك رسالة برقم التتبع عند الشحن."},
                {"q": "ما هي طرق الدفع؟", "a": "بطاقة بنكية، تحويل بنكي، أو الدفع عند الاستلام."},
            ],
            "fr": [
                {"q": "Comment demander un remboursement ?", "a": "Contactez-nous avec votre numéro de commande sous 30 jours."},
                {"q": "Quel est le délai de livraison ?", "a": "2 à 5 jours ouvrés au Maroc."},
                {"q": "Puis-je modifier ma commande ?", "a": "Oui, avant expédition — contactez-nous immédiatement."},
                {"q": "Comment suivre ma commande ?", "a": "Vous recevrez un numéro de suivi à l'expédition."},
                {"q": "Quels sont les modes de paiement ?", "a": "Carte bancaire, virement ou paiement à la livraison."},
            ],
            "en": [
                {"q": "How to request a refund?", "a": "Contact us with your order number within 30 days."},
                {"q": "What's the shipping time?", "a": "2-5 business days within Morocco."},
                {"q": "Can I change my order?", "a": "Yes, before shipping — contact us immediately."},
                {"q": "How to track my order?", "a": "You'll get a tracking number at shipping."},
                {"q": "What are payment methods?", "a": "Card, bank transfer, or cash on delivery."},
            ],
        }
        return faqs[lang]


# ============ اختبار سريع ============
if __name__ == "__main__":
    print("🧪 اختبار Customer Support Agent\n")
    agent = CustomerSupportAgent()

    # تذاكر تجريبية
    tickets = [
        "المنتج وصل مكسور وأنا غاضب جداً! أريد استرداد فوري.",
        "Comment puis-je suivre ma commande ?",
        "الموقع لا يعمل، أريد التحدث مع محامي!",
        "شكراً على الخدمة الممتازة",
    ]

    for i, t in enumerate(tickets, 1):
        print(f"--- التذكرة {i} ---")
        print(f"النص: {t[:60]}...")
        result = agent.classify_ticket(t, lang="ar")
        print(f"  النوع: {result['type_icon']} {result['type_label']} (ثقة {result['confidence']})")
        print(f"  الأولوية: {result['priority_icon']} {result['priority_label']}")
        print(f"  المشاعر: {result['sentiment_emoji']} {result['sentiment_label']}")
        print(f"  تصعيد: {'⚠️ نعم — ' + result['escalation_reason'] if result['needs_escalation'] else '✅ لا'}")
        resp = agent.generate_response(result, tone="apologetic", lang="ar")
        print(f"  الرد ({resp['source']}):")
        print(f"    {resp['text'][:150]}...")
        print()

    print("=" * 50)
    print("📋 الإجراءات المقترحة للتذكرة الأولى:")
    r1 = agent.classify_ticket(tickets[0], lang="ar")
    for a in agent.suggest_actions(r1, lang="ar"):
        print(f"  {a}")
