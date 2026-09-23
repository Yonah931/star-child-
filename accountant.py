"""
وكيل المحاسبة - Yonah Ashkenaz
قراءة وتحليل ملفات Excel/CSV المحاسبية
يدعم: العربية، الفرنسية، الإنجليزية
"""

import pandas as pd
import os
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF
from datetime import datetime
from translations import get_text


# ============================================
# إصلاح النص العربي للعرض في PDF
# ============================================
def fix_arabic(text):
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)


# ============================================
# وكيل المحاسبة
# ============================================
class AccountantAgent:
    def __init__(self):
        self.df = None
        self.issues = []
        self.summary = {}

    def load_file(self, file_path):
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            self.df.columns = [str(c).strip() for c in self.df.columns]
            return {"success": True, "rows": len(self.df), "columns": list(self.df.columns)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def detect_columns(self):
        cols = [c.lower() for c in self.df.columns]
        debit_kw = ['debit', 'débit', 'مدين']
        credit_kw = ['credit', 'crédit', 'دائن']
        date_kw = ['date', 'تاريخ']
        desc_kw = ['description', 'libellé', 'بيان', 'وصف']

        detected = {'debit': None, 'credit': None, 'date': None, 'description': None}

        for i, col in enumerate(cols):
            if any(k in col for k in debit_kw) and not detected['debit']:
                detected['debit'] = self.df.columns[i]
            elif any(k in col for k in credit_kw) and not detected['credit']:
                detected['credit'] = self.df.columns[i]
            elif any(k in col for k in date_kw) and not detected['date']:
                detected['date'] = self.df.columns[i]
            elif any(k in col for k in desc_kw) and not detected['description']:
                detected['description'] = self.df.columns[i]
        return detected

    def check_balance(self, debit_col, credit_col):
        try:
            total_debit = pd.to_numeric(self.df[debit_col], errors='coerce').fillna(0).sum()
            total_credit = pd.to_numeric(self.df[credit_col], errors='coerce').fillna(0).sum()
            diff = abs(total_debit - total_credit)
            return {
                "balanced": diff < 0.01,
                "total_debit": round(total_debit, 2),
                "total_credit": round(total_credit, 2),
                "difference": round(diff, 2)
            }
        except Exception as e:
            return {"balanced": False, "error": str(e)}

    def find_issues(self, debit_col, credit_col, lang='ar'):
        issues = []

        null_count = self.df[[debit_col, credit_col]].isnull().sum().sum()
        if null_count > 0:
            if lang == 'fr':
                issues.append(f"{null_count} valeurs manquantes (Débit/Crédit)")
            elif lang == 'en':
                issues.append(f"{null_count} missing values (Debit/Credit)")
            else:
                issues.append(f"{null_count} قيمة فارغة في المدين/الدائن")

        debit_neg = pd.to_numeric(self.df[debit_col], errors='coerce') < 0
        credit_neg = pd.to_numeric(self.df[credit_col], errors='coerce') < 0
        neg_count = debit_neg.sum() + credit_neg.sum()
        if neg_count > 0:
            if lang == 'fr':
                issues.append(f"{neg_count} valeur(s) négative(s) - à vérifier")
            elif lang == 'en':
                issues.append(f"{neg_count} negative value(s) - to review")
            else:
                issues.append(f"{neg_count} قيم سالبة (تأكد من صحتها)")

        debit_zero = pd.to_numeric(self.df[debit_col], errors='coerce').fillna(0) == 0
        credit_zero = pd.to_numeric(self.df[credit_col], errors='coerce').fillna(0) == 0
        empty_rows = (debit_zero & credit_zero).sum()
        if empty_rows > 0:
            if lang == 'fr':
                issues.append(f"{empty_rows} lignes sans débit ni crédit")
            elif lang == 'en':
                issues.append(f"{empty_rows} rows without debit or credit")
            else:
                issues.append(f"{empty_rows} صفوف بدون مدين ولا دائن")

        big_debit = pd.to_numeric(self.df[debit_col], errors='coerce') > 100000
        big_credit = pd.to_numeric(self.df[credit_col], errors='coerce') > 100000
        big_count = big_debit.sum() + big_credit.sum()
        if big_count > 0:
            if lang == 'fr':
                issues.append(f"{big_count} montants très élevés (>100,000) - à examiner")
            elif lang == 'en':
                issues.append(f"{big_count} very large amounts (>100,000) - review")
            else:
                issues.append(f"{big_count} قيم كبيرة جداً (>100,000) - للمراجعة")

        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            if lang == 'fr':
                issues.append(f"{duplicates} lignes dupliquées")
            elif lang == 'en':
                issues.append(f"{duplicates} duplicated rows")
            else:
                issues.append(f"{duplicates} صفوف مكررة")

        self.issues = issues
        return issues

    def generate_summary(self, debit_col, credit_col):
        self.summary = {
            "total_rows": len(self.df),
            "total_debit": round(pd.to_numeric(self.df[debit_col], errors='coerce').fillna(0).sum(), 2),
            "total_credit": round(pd.to_numeric(self.df[credit_col], errors='coerce').fillna(0).sum(), 2),
            "issues_count": len(self.issues),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return self.summary


# ============================================
# تقرير PDF متعدد اللغات
# ============================================
class AccountingReport(FPDF):
    def __init__(self, lang='ar'):
        super().__init__()
        self.lang = lang
        self.font_name = "Amiri" if lang == 'ar' else "Helvetica"
        self.is_rtl = (lang == 'ar')
        self.align = "R" if self.is_rtl else "L"

    def header(self):
        self.set_fill_color(15, 20, 40)
        self.rect(0, 0, 210, 25, "F")
        self.set_font(self.font_name, size=16)
        self.set_text_color(0, 212, 255)
        self.cell(0, 15, "Yonah Ashkenaz", ln=True, align="C")
        self.set_text_color(200, 200, 200)
        self.set_font(self.font_name, size=10)
        title = get_text(self.lang, "report_title")
        if self.is_rtl:
            title = fix_arabic(title)
        self.cell(0, 8, title, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_name, size=8)
        self.set_text_color(150, 150, 150)
        page_text = f"{get_text(self.lang, 'page')} {self.page_no()}"
        if self.is_rtl:
            page_text = fix_arabic(page_text)
        self.cell(0, 10, page_text, align="C")


def generate_accounting_pdf(summary, balance, issues, lang='ar', filename=None):
    """توليد تقرير PDF متعدد اللغات"""
    pdf = AccountingReport(lang=lang)

    if lang == 'ar':
        font_path = os.path.expanduser("~/.fonts/Amiri-Regular.ttf")
        if not os.path.exists(font_path):
            font_path = "Amiri-Regular.ttf"
        pdf.add_font("Amiri", "", font_path, uni=True)

    pdf.add_page()
    align = pdf.align

    def txt(text):
        return fix_arabic(text) if pdf.is_rtl else text

    # === الملخص ===
    pdf.set_font(pdf.font_name, size=14)
    pdf.set_text_color(0, 100, 180)
    pdf.cell(0, 10, txt(get_text(lang, "summary")), ln=True, align=align)
    pdf.ln(2)

    pdf.set_font(pdf.font_name, size=11)
    pdf.set_text_color(30, 30, 30)

    lines = [
        (get_text(lang, "rows_count"), summary.get("total_rows", 0)),
        (get_text(lang, "total_debit"), f"{summary.get('total_debit', 0):,.2f}"),
        (get_text(lang, "total_credit"), f"{summary.get('total_credit', 0):,.2f}"),
        (get_text(lang, "issues_count"), summary.get("issues_count", 0)),
        (get_text(lang, "date"), summary.get("date", "")),
    ]
    for label, value in lines:
        pdf.cell(0, 8, txt(f"{label}: {value}"), ln=True, align=align)

    pdf.ln(5)

    # === التوازن ===
    pdf.set_font(pdf.font_name, size=14)
    if balance.get("balanced"):
        pdf.set_text_color(0, 150, 0)
        pdf.cell(0, 10, txt(get_text(lang, "balance_ok")), ln=True, align=align)
    else:
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, txt(get_text(lang, "balance_warning")), ln=True, align=align)

    pdf.set_font(pdf.font_name, size=11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, txt(f"{get_text(lang, 'difference')}: {balance.get('difference', 0):,.2f}"), ln=True, align=align)

    pdf.ln(5)

    # === الملاحظات ===
    pdf.set_font(pdf.font_name, size=14)
    pdf.set_text_color(200, 100, 0)
    pdf.cell(0, 10, txt(get_text(lang, "issues")), ln=True, align=align)
    pdf.ln(2)

    pdf.set_font(pdf.font_name, size=10)
    pdf.set_text_color(30, 30, 30)

    if issues:
        for i, issue in enumerate(issues, 1):
            pdf.multi_cell(0, 7, txt(f"{i}. {issue}"), align=align)
            pdf.ln(1)
    else:
        pdf.cell(0, 8, txt(get_text(lang, "no_issues")), ln=True, align=align)

    # === التذييل ===
    pdf.ln(10)
    pdf.set_font(pdf.font_name, size=9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 6, txt(get_text(lang, "review_note")), align=align)

    if filename is None:
        filename = f"report_{lang}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename


if __name__ == "__main__":
    print("✅ accountant.py جاهز (متعدد اللغات)")
