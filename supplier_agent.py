"""
Supplier Agent
وكيل الموردين: مقارنة، تقييم، تواصل، إدارة
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


class SupplierAgent:
    """وكيل الموردين متعدد اللغات"""

    REQUEST_TYPES = {
        "quote": {"ar": "طلب عرض سعر", "fr": "Demande de devis", "en": "Quote Request", "icon": "💰"},
        "negotiation": {"ar": "تفاوض", "fr": "Négociation", "en": "Negotiation", "icon": "🤝"},
        "complaint": {"ar": "شكوى", "fr": "Réclamation", "en": "Complaint", "icon": "⚠️"},
        "followup": {"ar": "متابعة", "fr": "Suivi", "en": "Follow-up", "icon": "🔔"},
        "termination": {"ar": "إنهاء تعاقد", "fr": "Résiliation", "en": "Termination", "icon": "📤"},
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

    def _build_prompt(self, request_type, supplier_name, context, lang, sender):
        lang_names = {"ar": "العربية", "fr": "Français", "en": "English"}
        type_label = self.REQUEST_TYPES[request_type][lang]

        system = f"""أنت مدير مشتريات محترف.
اكتب رسالة {type_label} باللغة {lang_names[lang]}.
كن مهنياً وواضحاً ومحدداً.
تنسيق: موضوع، تحية، جسم، طلب واضح، خاتمة.
لا شرح إضافي — فقط الرسالة."""

        user = f"المورد: {supplier_name or 'غير محدد'}\nالسياق: {context}\nالمرسل: {sender or 'قسم المشتريات'}"
        return system, user

    def _fallback(self, request_type, supplier_name, context, lang):
        templates = {
            "ar": {
                "quote": f"الموضوع: طلب عرض سعر\n\nالسيد {supplier_name}،\n\nنطلب منكم إرسال عرض سعر بخصوص:\n{context}\n\nيرجى تحديد: السعر، مدة التسليم، شروط الدفع.\n\nمع التحية",
                "negotiation": f"الموضوع: طلب تفاوض\n\nالسيد {supplier_name}،\n\nبخصوص {context}، نقترح مراجعة الشروط.\n\nمع التحية",
                "complaint": f"الموضوع: شكوى\n\nالسيد {supplier_name}،\n\nنبلغكم بمشكلة بخصوص {context}.\n\nنطلب حلاً عاجلاً.\n\nمع التحية",
                "followup": f"الموضوع: متابعة\n\nالسيد {supplier_name}،\n\nنتابع ما تم بخصوص {context}.\n\nمع التحية",
                "termination": f"الموضوع: إنهاء تعاقد\n\nالسيد {supplier_name}،\n\nنبلغكم بإنهاء التعاقد بخصوص {context}.\n\nمع التحية",
            },
            "fr": {
                "quote": f"Objet: Demande de devis\n\nCher {supplier_name},\n\nMerci de nous envoyer un devis pour: {context}\n\nCordialement",
                "negotiation": f"Objet: Négociation\n\nCher {supplier_name},\n\nConcernant {context}, nous proposons une révision.\n\nCordialement",
                "complaint": f"Objet: Réclamation\n\nCher {supplier_name},\n\nProblème concernant {context}.\n\nCordialement",
                "followup": f"Objet: Suivi\n\nCher {supplier_name},\n\nSuivi de {context}.\n\nCordialement",
                "termination": f"Objet: Résiliation\n\nCher {supplier_name},\n\nRésiliation concernant {context}.\n\nCordialement",
            },
            "en": {
                "quote": f"Subject: Quote Request\n\nDear {supplier_name},\n\nPlease send a quote for: {context}\n\nBest regards",
                "negotiation": f"Subject: Negotiation\n\nDear {supplier_name},\n\nRegarding {context}, we propose a revision.\n\nBest regards",
                "complaint": f"Subject: Complaint\n\nDear {supplier_name},\n\nIssue regarding {context}.\n\nBest regards",
                "followup": f"Subject: Follow-up\n\nDear {supplier_name},\n\nFollowing up on {context}.\n\nBest regards",
                "termination": f"Subject: Termination\n\nDear {supplier_name},\n\nTermination regarding {context}.\n\nBest regards",
            },
        }
        return templates[lang][request_type]

    def generate_request(self, request_type, supplier_name, context, lang="ar", sender=""):
        """توليد رسالة للمورد"""
        result = {
            "type": request_type,
            "type_label": self.REQUEST_TYPES[request_type][lang],
            "supplier": supplier_name,
            "lang": lang,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        if self.client is not None:
            try:
                system, user = self._build_prompt(request_type, supplier_name, context, lang, sender)
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    temperature=0.6,
                    max_tokens=2000,
                )
                content = resp.choices[0].message.content
                if content and content.strip():
                    result["content"] = content.strip()
                    result["source"] = "AI"
                    return result
                result["content"] = self._fallback(request_type, supplier_name, context, lang)
                result["source"] = "قوالب (AI أرجع نصاً فارغاً)"
                return result
            except Exception as e:
                result["content"] = self._fallback(request_type, supplier_name, context, lang)
                result["source"] = f"قوالب (خطأ AI: {str(e)[:60]})"
                return result
        else:
            result["content"] = self._fallback(request_type, supplier_name, context, lang)
            result["source"] = "قوالب (AI غير متوفر)"
            return result

    def compare_suppliers(self, suppliers_data, lang="ar"):
        """مقارنة موردين (قائمة dicts)"""
        if not suppliers_data:
            return None
        criteria = ["price", "quality", "delivery", "payment", "service"]
        scores = {}
        for s in suppliers_data:
            total = sum(s.get(c, 0) for c in criteria) / len(criteria)
            scores[s.get("name", "?")] = round(total, 2)
        best = max(scores, key=scores.get)
        return {
            "ranking": sorted(scores.items(), key=lambda x: -x[1]),
            "best": best,
            "criteria": criteria,
        }


if __name__ == "__main__":
    print("🧪 اختبار Supplier Agent\n")
    agent = SupplierAgent()
    print("--- طلب عرض سعر ---")
    r = agent.generate_request("quote", "شركة التوريدات المغربية",
                               "توريد 100 وحدة من المادة الخام X",
                               lang="ar")
    print(f"المصدر: {r['source']} | النوع: {r['type_label']}")
    print(f"المحتوى:\n{r['content'][:400]}...")
    print()
    print("--- مقارنة موردين ---")
    suppliers = [
        {"name": "مورد A", "price": 8, "quality": 9, "delivery": 7, "payment": 6, "service": 8},
        {"name": "مورد B", "price": 9, "quality": 7, "delivery": 8, "payment": 9, "service": 7},
        {"name": "مورد C", "price": 6, "quality": 9, "delivery": 9, "payment": 8, "service": 9},
    ]
    result = agent.compare_suppliers(suppliers)
    print(f"الأفضل: {result['best']}")
    for name, score in result["ranking"]:
        print(f"  {name}: {score}")
