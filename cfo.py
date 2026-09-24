"""
وكيل المدير المالي (CFO) - Yonah Ashkenaz
تحليل مالي + ضرائب + تدفق نقدي + نصائح
"""

import pandas as pd
from datetime import datetime


# ============================================================
# معدلات الضرائب المغربية 2026
# ============================================================
TAX_RATES = {
    "TVA": 0.20,          # الضريبة على القيمة المضافة
    "IS_20": 0.20,        # ضريبة الشركات (المعدل الأساسي)
    "IS_15": 0.15,        # للشركات الصغيرة
    "CNSS": 0.2677,       # الضمان الاجتماعي
    "IR": 0.30,           # ضريبة الدخل (للأفراد)
}


class CFOAgent:
    def __init__(self):
        self.df = None
        self.summary = {}
        self.insights = []
        self.taxes = {}

    def load_file(self, file_path):
        """قراءة ملف Excel/CSV"""
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
        """اكتشاف أعمدة الإيرادات والمصاريف"""
        cols = [c.lower() for c in self.df.columns]

        revenue_kw = ['revenue', 'revenus', 'ventes', 'chiffre', 'ca', 'مبيعات', 'إيرادات', 'مداخيل']
        expense_kw = ['expense', 'expenses', 'dépense', 'dépenses', 'charges', 'coût', 'coûts', 'مصاريف', 'نفقات']
        date_kw = ['date', 'تاريخ']

        detected = {'revenue': None, 'expense': None, 'date': None}

        for i, col in enumerate(cols):
            if any(k in col for k in revenue_kw) and not detected['revenue']:
                detected['revenue'] = self.df.columns[i]
            elif any(k in col for k in expense_kw) and not detected['expense']:
                detected['expense'] = self.df.columns[i]
            elif any(k in col for k in date_kw) and not detected['date']:
                detected['date'] = self.df.columns[i]

        return detected

    def analyze_profitability(self, revenue_col, expense_col):
        """تحليل الربحية والهوامش"""
        total_revenue = pd.to_numeric(self.df[revenue_col], errors='coerce').fillna(0).sum()
        total_expense = pd.to_numeric(self.df[expense_col], errors='coerce').fillna(0).sum()

        net_profit = total_revenue - total_expense
        margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        self.summary = {
            "total_revenue": round(total_revenue, 2),
            "total_expense": round(total_expense, 2),
            "net_profit": round(net_profit, 2),
            "margin_percent": round(margin, 2),
        }

        # نصائح
        if margin < 0:
            self.insights.append({
                "type": "danger",
                "message": f"⚠️ خسارة! هامشك {margin:.1f}%. راجع المصاريف."
            })
        elif margin < 10:
            self.insights.append({
                "type": "warning",
                "message": f"⚠️ هامشك {margin:.1f}% منخفض. قطاعك يحتاج 15-25%."
            })
        elif margin < 20:
            self.insights.append({
                "type": "info",
                "message": f"✅ هامشك {margin:.1f}% مقبول."
            })
        else:
            self.insights.append({
                "type": "success",
                "message": f"🎉 هامشك {margin:.1f}% ممتاز!"
            })

        return self.summary

    def calculate_taxes(self):
        """حساب الضرائب المغربية"""
        revenue = self.summary.get("total_revenue", 0)
        expense = self.summary.get("total_expense", 0)
        profit = self.summary.get("net_profit", 0)

        # TVA على الإيرادات
        tva = revenue * TAX_RATES["TVA"]

        # IS على الربح
        if profit > 0:
            is_tax = profit * TAX_RATES["IS_20"]
        else:
            is_tax = 0

        # CNSS (تقديري على المصاريف)
        cnss = expense * TAX_RATES["CNSS"]

        self.taxes = {
            "tva": round(tva, 2),
            "is": round(is_tax, 2),
            "cnss": round(cnss, 2),
            "total_taxes": round(tva + is_tax + cnss, 2),
        }

        # الربح الصافي بعد الضرائب
        net_after_tax = profit - self.taxes["is"]
        self.summary["net_after_tax"] = round(net_after_tax, 2)

        return self.taxes

    def analyze_cash_flow(self):
        """تحليل التدفق النقدي"""
        revenue = self.summary.get("total_revenue", 0)
        expense = self.summary.get("total_expense", 0)

        # التدفق النقدي التشغيلي
        cash_flow = revenue - expense

        # معدل الاستهلاك النقدي (تقديري)
        monthly_burn = expense / 12 if expense > 0 else 0

        self.summary["cash_flow"] = round(cash_flow, 2)
        self.summary["monthly_burn"] = round(monthly_burn, 2)

        # تحذيرات
        if cash_flow < 0:
            self.insights.append({
                "type": "danger",
                "message": f"🚨 التدفق النقدي سالب: {cash_flow:,.2f} درهم."
            })
        elif cash_flow < monthly_burn * 2:
            self.insights.append({
                "type": "warning",
                "message": f"⚠️ احتياطي نقدي منخفض: {cash_flow:,.2f} درهم."
            })
        else:
            self.insights.append({
                "type": "success",
                "message": f"✅ تدفق نقدي صحي: {cash_flow:,.2f} درهم."
            })

        return self.summary

    def generate_recommendations(self):
        """توصيات مالية"""
        margin = self.summary.get("margin_percent", 0)

        if margin > 20:
            self.insights.append({
                "type": "info",
                "message": "💡 استثمر جزءاً من الربح في التوسع أو التسويق."
            })
        elif margin < 10:
            self.insights.append({
                "type": "warning",
                "message": "💡 راجع أكبر 3 مصاريف، ابحث عن تخفيض 10%."
            })

        # نسبة المصاريف
        if self.summary.get("total_revenue", 0) > 0:
            expense_ratio = (self.summary["total_expense"] / self.summary["total_revenue"]) * 100
            if expense_ratio > 80:
                self.insights.append({
                    "type": "warning",
                    "message": f"💡 مصاريفك {expense_ratio:.1f}% من إيراداتك. مثالي: <70%."
                })

        return self.insights

    def get_full_report(self):
        """تقرير كامل"""
        return {
            "summary": self.summary,
            "taxes": self.taxes,
            "insights": self.insights,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }


if __name__ == "__main__":
    print("✅ cfo.py جاهز")
    print("📊 معدلات الضرائب:")
    for key, val in TAX_RATES.items():
        print(f"   {key}: {val*100}%")
