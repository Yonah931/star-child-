"""
Moroccan Admin Agent
وكيل الإدارة المغربية: TVA, IS, IR, CNSS, Payroll
"""
from datetime import datetime, timedelta


class MoroccanAdmin:
    """وكيل الإدارة المغربية"""
    
    # ============ معدلات الضرائب 2025 ============
    
    # TVA
    TVA_RATES = {
        "standard": 0.20,      # 20%
        "reduced1": 0.14,      # 14%
        "reduced2": 0.10,      # 10%
        "reduced3": 0.07,      # 7%
        "exempt": 0.00         # معفى
    }
    
    # IS - Impôt sur les Sociétés (2025) - شرائح
    IS_BRACKETS = [
        (300_000, 0.10),        # 0 - 300K: 10%
        (1_000_000, 0.20),      # 300K - 1M: 20%
        (100_000_000, 0.31),    # 1M - 100M: 31%
        (float('inf'), 0.34),   # > 100M: 34%
    ]
    
    # IR - Impôt sur le Revenu (2025) - شرائح سنوية
    IR_BRACKETS = [
        (30_000, 0.00),         # 0 - 30K: 0%
        (50_000, 0.10),         # 30K - 50K: 10%
        (60_000, 0.20),         # 50K - 60K: 20%
        (80_000, 0.30),         # 60K - 80K: 30%
        (180_000, 0.34),        # 80K - 180K: 34%
        (float('inf'), 0.37),   # > 180K: 37%
    ]
    
    # CNSS 2025
    CNSS_EMPLOYEE = 0.0448        # 4.48% (CNSS salariale)
    AMO_EMPLOYEE = 0.0226         # 2.26% (AMO salariale)
    CNSS_EMPLOYER = 0.2109        # 21.09% (CNSS patronale)
    CNSS_TOTAL = 0.2677           # 26.77% (المجموع)
    CNSS_CEILING = 6_000          # سقف شهري للاشتراك CNSS
    
    # IR: خصم سنوي للأعباء المهنية
    IR_ANNUAL_DEDUCTION = 30_000
    
    # ============ الحسابات ============
    
    def __init__(self, company_name="Yonah Tech", company_ice="000000000000"):
        self.company_name = company_name
        self.company_ice = company_ice
    
    # ---------- TVA ----------
    def calculate_tva(self, sales_ht, purchases_ht, rate="standard"):
        """
        حساب TVA المستحقة
        sales_ht: المبيعات خارج الضريبة
        purchases_ht: المشتريات خارج الضريبة
        rate: نوع المعدل (standard/reduced1/...)
        """
        tva_rate = self.TVA_RATES.get(rate, 0.20)
        tva_collected = round(sales_ht * tva_rate, 2)
        tva_deductible = round(purchases_ht * tva_rate, 2)
        tva_due = round(tva_collected - tva_deductible, 2)
        
        return {
            "rate": tva_rate,
            "sales_ht": sales_ht,
            "purchases_ht": purchases_ht,
            "tva_collected": tva_collected,
            "tva_deductible": tva_deductible,
            "tva_due": tva_due,
            "status": "à payer" if tva_due > 0 else "crédit de TVA"
        }
    
    # ---------- IS ----------
    def calculate_is(self, annual_revenue, annual_expenses):
        """
        حساب IS (ضريبة الشركات)
        الشرائح تصاعدية على الربح الصافي
        """
        profit = annual_revenue - annual_expenses
        if profit <= 0:
            return {
                "revenue": annual_revenue,
                "expenses": annual_expenses,
                "profit": profit,
                "is_due": 0,
                "effective_rate": 0,
                "status": "déficit"
            }
        
        is_due = 0
        remaining = profit
        prev_limit = 0
        
        for limit, rate in self.IS_BRACKETS:
            bracket_size = min(remaining, limit - prev_limit)
            if bracket_size <= 0:
                break
            is_due += bracket_size * rate
            remaining -= bracket_size
            prev_limit = limit
            if remaining <= 0:
                break
        
        is_due = round(is_due, 2)
        effective_rate = round(is_due / profit * 100, 2) if profit > 0 else 0
        
        return {
            "revenue": annual_revenue,
            "expenses": annual_expenses,
            "profit": round(profit, 2),
            "is_due": is_due,
            "effective_rate": effective_rate,
            "status": "à payer"
        }
    
    # ---------- IR ----------
    def calculate_ir_annual(self, annual_net_salary):
        """
        حساب IR السنوي على الأجر الصافي
        مع خصم الأعباء المهنية (30,000 درهم)
        """
        taxable = max(0, annual_net_salary - self.IR_ANNUAL_DEDUCTION)
        
        ir = 0
        remaining = taxable
        prev_limit = 0
        
        for limit, rate in self.IR_BRACKETS:
            bracket_size = min(remaining, limit - prev_limit)
            if bracket_size <= 0:
                break
            ir += bracket_size * rate
            remaining -= bracket_size
            prev_limit = limit
            if remaining <= 0:
                break
        
        return {
            "annual_net_salary": annual_net_salary,
            "deduction": self.IR_ANNUAL_DEDUCTION,
            "taxable": round(taxable, 2),
            "ir_annual": round(ir, 2),
            "ir_monthly": round(ir / 12, 2)
        }
    
    # ---------- Payroll ----------
    def calculate_payroll(self, salary_brut):
        """
        حساب كشف الراتب الشهري
        salary_brut: الأجر الخام الشهري
        """
        # CNSS + AMO على الموظف (بسقف)
        base_cnss = min(salary_brut, self.CNSS_CEILING)
        cnss_employee = round(base_cnss * self.CNSS_EMPLOYEE, 2)
        amo_employee = round(base_cnss * self.AMO_EMPLOYEE, 2)
        
        # CNSS على صاحب العمل
        cnss_employer = round(base_cnss * self.CNSS_EMPLOYER, 2)
        
        # الأجر الخاضع للضريبة
        taxable = salary_brut - cnss_employee - amo_employee
        annual_taxable = taxable * 12
        
        # IR
        ir_result = self.calculate_ir_annual(annual_taxable)
        ir_monthly = ir_result["ir_monthly"]
        
        # الأجر الصافي
        net_salary = round(salary_brut - cnss_employee - amo_employee - ir_monthly, 2)
        
        # التكلفة الإجمالية على صاحب العمل
        total_cost = round(salary_brut + cnss_employer, 2)
        
        return {
            "salary_brut": salary_brut,
            "cnss_employee": cnss_employee,
            "amo_employee": amo_employee,
            "ir_monthly": ir_monthly,
            "net_salary": net_salary,
            "cnss_employer": cnss_employer,
            "total_cost_employer": total_cost
        }
    
    # ---------- التقويم الضريبي ----------
    def get_tax_calendar(self, year=None):
        """
        مواعيد الالتزامات الضريبية السنوية
        """
        if year is None:
            year = datetime.now().year
        
        calendar = [
            {"date": f"{year}-01-31", "obligation": "TVA Décembre", "penalty": "10% + 5%"},
            {"date": f"{year}-01-31", "obligation": "IR salaires Décembre", "penalty": "10%"},
            {"date": f"{year}-01-31", "obligation": "CNSS Décembre", "penalty": "3%"},
            {"date": f"{year}-03-31", "obligation": "IS acompte (31/03)", "penalty": "10%"},
            {"date": f"{year}-04-30", "obligation": "Déclaration IS (exercice N-1)", "penalty": "10%"},
            {"date": f"{year}-06-30", "obligation": "IS acompte (30/06)", "penalty": "10%"},
            {"date": f"{year}-09-30", "obligation": "IS acompte (30/09)", "penalty": "10%"},
            {"date": f"{year}-12-31", "obligation": "IS acompte (31/12)", "penalty": "10%"},
        ]
        
        # TVA + IR + CNSS شهرياً
        for month in range(1, 13):
            calendar.append({
                "date": f"{year}-{month:02d}-{'28' if month == 2 else '30' if month in [4,6,9,11] else '31'}",
                "obligation": f"TVA + IR + CNSS Mois {month:02d}",
                "penalty": "10% + 5%"
            })
        
        return sorted(calendar, key=lambda x: x["date"])
    
    def get_upcoming_deadlines(self, days=30):
        """
        المواعيد القادمة خلال N يوم
        """
        today = datetime.now()
        limit = today + timedelta(days=days)
        
        calendar = self.get_tax_calendar(today.year)
        upcoming = []
        
        for item in calendar:
            try:
                date = datetime.strptime(item["date"], "%Y-%m-%d")
                if today <= date <= limit:
                    days_left = (date - today).days
                    upcoming.append({
                        **item,
                        "days_left": days_left,
                        "urgency": "🔴" if days_left <= 7 else "🟡" if days_left <= 15 else "🟢"
                    })
            except ValueError:
                continue
        
        return upcoming


# ============ اختبار سريع ============
if __name__ == "__main__":
    print("🧪 اختبار Moroccan Admin Agent\n")
    
    agent = MoroccanAdmin()
    
    # 1. TVA
    print("1️⃣ TVA:")
    tva = agent.calculate_tva(sales_ht=100_000, purchases_ht=40_000)
    print(f"   المبيعات HT: {tva['sales_ht']:,} DH")
    print(f"   TVA محصلة: {tva['tva_collected']:,} DH")
    print(f"   TVA قابلة للخصم: {tva['tva_deductible']:,} DH")
    print(f"   TVA المستحقة: {tva['tva_due']:,} DH ({tva['status']})\n")
    
    # 2. IS
    print("2️⃣ IS:")
    is_r = agent.calculate_is(annual_revenue=500_000, annual_expenses=300_000)
    print(f"   الإيرادات: {is_r['revenue']:,} DH")
    print(f"   المصاريف: {is_r['expenses']:,} DH")
    print(f"   الربح: {is_r['profit']:,} DH")
    print(f"   IS: {is_r['is_due']:,} DH (معدل فعال: {is_r['effective_rate']}%)\n")
    
    # 3. Payroll
    print("3️⃣ Payroll (راتب 8,000 DH):")
    p = agent.calculate_payroll(salary_brut=8_000)
    print(f"   الأجر الخام: {p['salary_brut']:,} DH")
    print(f"   CNSS موظف: {p['cnss_employee']} DH")
    print(f"   AMO موظف: {p['amo_employee']} DH")
    print(f"   IR: {p['ir_monthly']} DH")
    print(f"   ✅ الصافي: {p['net_salary']:,} DH")
    print(f"   CNSS صاحب العمل: {p['cnss_employer']} DH")
    print(f"   💰 التكلفة الكلية: {p['total_cost_employer']:,} DH\n")
    
    # 4. التقويم
    print("4️⃣ المواعيد القادمة (30 يوماً):")
    deadlines = agent.get_upcoming_deadlines(30)
    if deadlines:
        for d in deadlines[:5]:
            print(f"   {d['urgency']} {d['date']} — {d['obligation']} ({d['days_left']} يوم)")
    else:
        print("   لا مواعيد قريبة")
