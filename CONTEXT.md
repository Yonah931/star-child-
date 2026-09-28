# Yonah Ashkenaz — Agentic OS
آخر تحديث: 2026-09-28

## 1. نظرة عامة
- المسار: /home/yonah-ashkenaz/sureflow_agentic_os
- GitHub: https://github.com/Yonah931/star-child-
- النشر: Streamlit Cloud
- الرابط الرئيسي: https://star-child-agentic-os-yonah-ashkenaz-morocco-sureflow-business1.streamlit.app
- رابط الوكلاء السبعة: https://yonah-agents.streamlit.app

## 2. البيئة
- Linux Mint Cinnamon + nano
- Python 3.14 (Streamlit Cloud)
- venv: `source venv/bin/activate`
- Secrets: GROQ_API_KEY, TAVILY_API_KEY

## 3. ملفات المشروع وحالتها
| الملف | الحالة | الدالة/الفئة الرئيسية |
|---|---|---|
| app.py | ✅ يعمل | show_landing, show_accountant, show_hr, show_cfo, show_agents, show_invoice |
| invoice.py | ✅ يعمل (العربية معطوبة) | InvoiceAgent |
| accountant.py | ✅ يعمل | AccountantAgent |
| hr.py | ✅ يعمل | HRAgent |
| cfo.py | ✅ يعمل | CFOAgent |
| multiagent.py | ✅ يعمل | 7 agents |
| reports.py | ✅ يعمل | generate_hr_report, generate_cfo_report |
| translations.py | ✅ يعمل | get_text(lang, key) |

## 4. توقيعات InvoiceAgent
```python
InvoiceAgent()  # defaults: company_name="Yonah Tech", company_address="Casablanca, Maroc", company_ice="000000000000"
create_invoice(client_name, client_address, items, tax_rate=0.20) -> dict
# items = [{"description": str, "quantity": float, "unit_price": float}]
# يرجع: {number, date, client_name, client_address, items, subtotal, tax, total, tax_rate}
generate_pdf(invoice, lang='ar'/'fr', filename=None) -> path
