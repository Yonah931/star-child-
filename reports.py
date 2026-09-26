"""
تقارير PDF لـ HR و CFO - Yonah Ashkenaz
"""

import os
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF
from datetime import datetime


def fix_arabic(text):
    if not text:
        return ""
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except:
        return str(text)


class BaseReport(FPDF):
    def __init__(self, lang='ar', title_ar="", title_fr=""):
        super().__init__()
        self.lang = lang
        self.font_name = "Amiri" if lang == 'ar' else "DejaVu"
        self.is_rtl = (lang == 'ar')
        self.align = "R" if self.is_rtl else "L"
        self.title_ar = title_ar
        self.title_fr = title_fr

    def header(self):
        self.set_fill_color(15, 20, 40)
        self.rect(0, 0, 210, 25, "F")
        self.set_font(self.font_name, size=16)
        self.set_text_color(0, 212, 255)
        self.cell(0, 15, "Yonah Ashkenaz", ln=True, align="C")
        self.set_text_color(200, 200, 200)
        self.set_font(self.font_name, size=10)
        title = self.title_ar if self.lang == 'ar' else self.title_fr
        if self.is_rtl:
            title = fix_arabic(title)
        self.cell(0, 8, title, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_name, size=8)
        self.set_text_color(150, 150, 150)
        txt = f"{'صفحة' if self.is_rtl else 'Page'} {self.page_no()}"
        if self.is_rtl:
            txt = fix_arabic(txt)
        self.cell(0, 10, txt, align="C")

    def _txt(self, t):
        return fix_arabic(t) if self.is_rtl else t

    def section_title(self, text):
        self.set_font(self.font_name, size=14)
        self.set_text_color(0, 100, 180)
        self.cell(0, 10, self._txt(text), ln=True, align=self.align)
        self.ln(2)

    def body_line(self, label, value):
        self.set_font(self.font_name, size=11)
        self.set_text_color(30, 30, 30)
        self.cell(0, 8, self._txt(f"{label}: {value}"), ln=True, align=self.align)


# ============================================================
# تقرير HR
# ============================================================
def generate_hr_report(candidates, stats, lang='ar', filename=None):
    """تقرير فرز السير الذاتية"""
    pdf = BaseReport(lang=lang,
        title_ar="تقرير فرز السير الذاتية",
        title_fr="Rapport de tri des CV")

    if lang == 'ar':
        font_path = os.path.expanduser("~/.fonts/Amiri-Regular.ttf")
        if not os.path.exists(font_path):
            font_path = "Amiri-Regular.ttf"
        pdf.add_font("Amiri", "", font_path, uni=True)
    else:
        font_path = "DejaVuSans.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        pdf.add_font("DejaVu", "", font_path, uni=True)

    pdf.add_page()

    # === الإحصائيات ===
    labels = {
        'ar': {
            'stats': 'إحصائيات الفرز',
            'total': 'إجمالي المرشحين',
            'avg_score': 'متوسط النقاط',
            'avg_exp': 'متوسط الخبرة (سنوات)',
            'top': 'أفضل مرشح',
            'top_score': 'نقاط الأفضل',
            'ranking': 'ترتيب المرشحين',
            'name': 'الاسم',
            'email': 'البريد',
            'experience': 'الخبرة',
            'skills': 'المهارات المطابقة',
            'score': 'النقاط',
        },
        'fr': {
            'stats': 'Statistiques',
            'total': 'Total candidats',
            'avg_score': 'Score moyen',
            'avg_exp': 'Expérience moyenne (ans)',
            'top': 'Meilleur candidat',
            'top_score': 'Score du meilleur',
            'ranking': 'Classement des candidats',
            'name': 'Nom',
            'email': 'Email',
            'experience': 'Expérience',
            'skills': 'Compétences',
            'score': 'Score',
        },
    }
    L = labels.get(lang, labels['ar'])

    pdf.section_title(L['stats'])
    pdf.body_line(L['total'], stats.get('total_candidates', 0))
    pdf.body_line(L['avg_score'], stats.get('average_score', 0))
    pdf.body_line(L['avg_exp'], stats.get('average_experience', 0))
    pdf.body_line(L['top'], stats.get('top_candidate', '—'))
    pdf.body_line(L['top_score'], f"{stats.get('top_score', 0)}/100")

    pdf.ln(5)
    pdf.section_title(L['ranking'])

    # === الترتيب ===
    for i, c in enumerate(candidates[:15], 1):
        pdf.set_font(pdf.font_name, size=11)
        pdf.set_text_color(0, 100, 180)
        pdf.cell(0, 8, pdf._txt(f"#{i} {c['name']} - {c['score']}/100"),
                 ln=True, align=pdf.align)

        pdf.set_font(pdf.font_name, size=9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, pdf._txt(f"  {L['email']}: {c['email']}"),
                 ln=True, align=pdf.align)
        pdf.cell(0, 6, pdf._txt(f"  {L['experience']}: {c['experience']}"),
                 ln=True, align=pdf.align)
        skills_txt = ', '.join(c['matched_skills']) or '—'
        pdf.cell(0, 6, pdf._txt(f"  {L['skills']}: {skills_txt}"),
                 ln=True, align=pdf.align)
        pdf.ln(2)

    # التذييل
    pdf.ln(5)
    pdf.set_font(pdf.font_name, size=9)
    pdf.set_text_color(120, 120, 120)
    footer = "Une révision humaine est recommandée avant toute décision" if lang == 'fr' \
             else "يُنصح بمراجعة بشرية قبل اتخاذ أي قرار"
    pdf.multi_cell(0, 6, pdf._txt(footer), align=pdf.align)

    if filename is None:
        filename = f"hr_report_{lang}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename


# ============================================================
# تقرير CFO
# ============================================================
def generate_cfo_report(summary, taxes, insights, lang='ar', filename=None):
    """تقرير التحليل المالي"""
    pdf = BaseReport(lang=lang,
        title_ar="تقرير التحليل المالي",
        title_fr="Rapport d'Analyse Financière")

    if lang == 'ar':
        font_path = os.path.expanduser("~/.fonts/Amiri-Regular.ttf")
        if not os.path.exists(font_path):
            font_path = "Amiri-Regular.ttf"
        pdf.add_font("Amiri", "", font_path, uni=True)
    else:
        font_path = "DejaVuSans.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        pdf.add_font("DejaVu", "", font_path, uni=True)

    pdf.add_page()

    labels = {
        'ar': {
            'profit': 'تحليل الربحية',
            'revenue': 'إجمالي الإيرادات',
            'expense': 'إجمالي المصاريف',
            'net': 'الربح الصافي',
            'margin': 'الهامش',
            'taxes': 'الضرائب (المغرب 2026)',
            'tva': 'TVA (20%)',
            'is': 'IS (20%)',
            'cnss': 'CNSS (26.77%)',
            'total_tax': 'إجمالي الضرائب',
            'cash': 'التدفق النقدي',
            'cashflow': 'التدفق التشغيلي',
            'burn': 'معدل الاستهلاك الشهري',
            'insights': 'التوصيات',
        },
        'fr': {
            'profit': 'Analyse de rentabilité',
            'revenue': 'Chiffre d\'affaires',
            'expense': 'Total dépenses',
            'net': 'Bénéfice net',
            'margin': 'Marge',
            'taxes': 'Taxes (Maroc 2026)',
            'tva': 'TVA (20%)',
            'is': 'IS (20%)',
            'cnss': 'CNSS (26.77%)',
            'total_tax': 'Total taxes',
            'cash': 'Flux de trésorerie',
            'cashflow': 'Flux opérationnel',
            'burn': 'Burn mensuel',
            'insights': 'Recommandations',
        },
    }
    L = labels.get(lang, labels['ar'])

    # === الربحية ===
    pdf.section_title(L['profit'])
    pdf.body_line(L['revenue'], f"{summary.get('total_revenue', 0):,.2f}")
    pdf.body_line(L['expense'], f"{summary.get('total_expense', 0):,.2f}")
    pdf.body_line(L['net'], f"{summary.get('net_profit', 0):,.2f}")
    pdf.body_line(L['margin'], f"{summary.get('margin_percent', 0)}%")

    pdf.ln(5)

    # === الضرائب ===
    pdf.section_title(L['taxes'])
    pdf.body_line(L['tva'], f"{taxes.get('tva', 0):,.2f}")
    pdf.body_line(L['is'], f"{taxes.get('is', 0):,.2f}")
    pdf.body_line(L['cnss'], f"{taxes.get('cnss', 0):,.2f}")
    pdf.body_line(L['total_tax'], f"{taxes.get('total_taxes', 0):,.2f}")

    pdf.ln(5)

    # === التدفق النقدي ===
    pdf.section_title(L['cash'])
    pdf.body_line(L['cashflow'], f"{summary.get('cash_flow', 0):,.2f}")
    pdf.body_line(L['burn'], f"{summary.get('monthly_burn', 0):,.2f}")

    pdf.ln(5)

    # === التوصيات ===
    pdf.section_title(L['insights'])
    for insight in insights:
        pdf.set_font(pdf.font_name, size=10)
        msg = insight['message'].replace('✅', '').replace('⚠️', '').replace('🚨', '').replace('💡', '').replace('🎉', '')
        pdf.multi_cell(0, 6, pdf._txt(f"• {msg}"), align=pdf.align)
        pdf.ln(1)

    pdf.ln(5)
    pdf.set_font(pdf.font_name, size=9)
    pdf.set_text_color(120, 120, 120)
    footer = "Une révision humaine est recommandée avant toute décision" if lang == 'fr' \
             else "يُنصح بمراجعة بشرية قبل اتخاذ أي قرار"
    pdf.multi_cell(0, 6, pdf._txt(footer), align=pdf.align)

    if filename is None:
        filename = f"cfo_report_{lang}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename


if __name__ == "__main__":
    print("✅ reports.py جاهز")
