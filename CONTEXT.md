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


## 16. Moroccan Admin Agent
- الملف: moroccan_admin.py
- الفئة: MoroccanAdmin
- الدوال:
  - calculate_tva(sales_ht, purchases_ht, rate) -> dict
  - calculate_is(annual_revenue, annual_expenses) -> dict
  - calculate_ir_annual(annual_net_salary) -> dict
  - calculate_payroll(salary_brut) -> dict
  - get_tax_calendar(year) -> list
  - get_upcoming_deadlines(days) -> list
- معدلات 2025:
  - TVA: 20%, 14%, 10%, 7%, exempt
  - IS: 10% / 20% / 31% / 34%
  - IR: 0% / 10% / 20% / 30% / 34% / 37%
  - CNSS موظف: 4.48% (سقف 6000)
  - AMO موظف: 2.26%
  - CNSS صاحب عمل: 21.09%


## 17. WeasyPrint (حل العربية PDF)
- الملف: invoice.py v4
- الطريقة: HTML + CSS RTL → PDF
- يعمل في: Chrome, Firefox, Evince, Okular (كل العارضات)
- محلياً: `pip install weasyprint`
- على Cloud: يحتاج packages.txt (7 مكتبات نظام)
- packages.txt يحتوي: libpango, libharfbuzz, libffi, libcairo, libgdk-pixbuf, shared-mime-info, fonts-dejavu-core
- آخر commit: 88d6d52

## 18. جميع الوكلاء (12)
| # | الملف | الوصف |
|---|---|---|
| 1 | accountant.py | المحاسب |
| 2 | hr.py | HR |
| 3 | cfo.py | CFO |
| 4 | invoice.py | Invoice (WeasyPrint) |
| 5 | moroccan_admin.py | Moroccan Admin |
| 6 | customer_support.py | Customer Support (AI) |
| 7 | content_writer.py | Content Writer (AI) |
| 8 | email_agent.py | Email Agent (AI) |
| 9 | social_media.py | Social Media (AI) |
| 10 | meeting_notes.py | Meeting Notes (AI) |
| 11 | supplier_agent.py | Supplier (AI) |

**جميع الوكلاء يعملون بـ Groq AI (openai/gpt-oss-20b)**
