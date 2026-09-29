import os
from datetime import datetime
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class InvoiceAgent:
    def __init__(self, company_name="Yonah Tech", company_address="Casablanca, Maroc", company_ice="000000000000"):
        self.company_name = company_name
        self.company_address = company_address
        self.company_ice = company_ice
        self.invoices = []

    def _setup_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        # تفعيل تشكيل النص العربي الأصلي
        try:
            pdf.set_text_shaping(True)
        except Exception:
            pass

        # DejaVu (للأرقام والفرنسية)
        fp = os.path.join(BASE_DIR, "DejaVuSans.ttf")
        if not os.path.exists(fp):
            fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        pdf.add_font("DejaVu", "", fp)

        # Amiri (للعربية)
        amiri = None
        for ap in [
            os.path.join(BASE_DIR, "Amiri-Regular.ttf"),
            os.path.join(os.path.expanduser("~"), ".fonts", "Amiri-Regular.ttf"),
        ]:
            if os.path.exists(ap):
                amiri = ap
                break
        if amiri:
            pdf.add_font("Amiri", "", amiri)
        return pdf, bool(amiri)

    def create_invoice(self, client_name, client_address, items, tax_rate=0.20):
        subtotal = sum([i["quantity"] * i["unit_price"] for i in items])
        tax = subtotal * tax_rate
        total = subtotal + tax
        inv = {
            "number": f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "client_name": client_name,
            "client_address": client_address,
            "items": items,
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
            "tax_rate": tax_rate,
        }
        self.invoices.append(inv)
        return inv

    def generate_pdf(self, invoice, lang="fr", filename=None):
        pdf, has_amiri = self._setup_pdf()

        # ===== Header =====
        pdf.set_fill_color(15, 20, 40)
        pdf.rect(0, 0, 210, 30, "F")
        pdf.set_font("DejaVu", size=20)
        pdf.set_text_color(0, 212, 255)
        pdf.cell(0, 15, self.company_name, ln=True, align="C")
        pdf.set_font("DejaVu", size=9)
        pdf.set_text_color(200, 200, 200)
        pdf.cell(0, 6, self.company_address, ln=True, align="C")
        pdf.cell(0, 6, f"ICE: {self.company_ice}", ln=True, align="C")
        pdf.ln(5)

        # ===== Title =====
        pdf.set_text_color(0, 100, 180)
        if lang == "ar" and has_amiri:
            pdf.set_font("Amiri", size=18)
            pdf.cell(0, 10, "فاتورة", ln=True, align="C")
        else:
            pdf.set_font("DejaVu", size=16)
            pdf.cell(0, 10, "FACTURE", ln=True, align="C")

        # ===== Info =====
        pdf.set_font("DejaVu", size=10)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 7, f"N: {invoice['number']}", ln=True, align="L")
        pdf.cell(0, 7, f"Date: {invoice['date']}", ln=True, align="L")
        pdf.ln(3)

        # ===== Client (auto Arabic detection) =====
        def write_text(text, size=10, align="L"):
            text = str(text)
            if any('\u0600' <= c <= '\u06FF' for c in text) and has_amiri:
                pdf.set_font("Amiri", size=size)
            else:
                pdf.set_font("DejaVu", size=size)
            pdf.cell(0, 7, text, ln=True, align=align)

        write_text(invoice["client_name"])
        write_text(invoice["client_address"])
        pdf.ln(5)

        # ===== Table header =====
        pdf.set_fill_color(200, 220, 240)
        pdf.set_text_color(0, 60, 120)
        if lang == "ar" and has_amiri:
            hs = ["الوصف", "الكمية", "السعر", "المجموع"]
            pdf.set_font("Amiri", size=11)
        else:
            hs = ["Desc", "Qté", "Prix", "Total"]
            pdf.set_font("DejaVu", size=10)
        ws = [90, 20, 35, 40]
        for h, w in zip(hs, ws):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln()

        # ===== Items =====
        pdf.set_text_color(30, 30, 30)
        for it in invoice["items"]:
            row = [
                it["description"],
                str(it["quantity"]),
                f"{it['unit_price']:.2f}",
                f"{it['quantity'] * it['unit_price']:.2f}",
            ]
            for v, w in zip(row, ws):
                is_ar = any('\u0600' <= c <= '\u06FF' for c in str(v))
                if is_ar and has_amiri:
                    pdf.set_font("Amiri", size=10)
                else:
                    pdf.set_font("DejaVu", size=9)
                pdf.cell(w, 7, str(v), border=1, align="C")
            pdf.ln()
        pdf.ln(5)

        # ===== Totals =====
        values = [invoice["subtotal"], invoice["tax"], invoice["total"]]
        if lang == "ar" and has_amiri:
            labels = ["المجموع HT", f"TVA {int(invoice['tax_rate']*100)}%", "المجموع TTC"]
            pdf.set_font("Amiri", size=12)
        else:
            labels = ["Sous-total", f"TVA {int(invoice['tax_rate']*100)}%", "TOTAL"]
            pdf.set_font("DejaVu", size=11)
        for lb, vl in zip(labels, values):
            pdf.cell(120, 8, lb, align="L")
            pdf.set_font("DejaVu", size=11)
            pdf.cell(50, 8, f"{vl:.2f} MAD", ln=True)

        if filename is None:
            filename = f"{invoice['number']}_{lang}.pdf"
        pdf.output(filename)
        return filename


if __name__ == "__main__":
    print("OK invoice.py v3 ready")
    a = InvoiceAgent()
    inv = a.create_invoice("عميل تجريبي", "الدار البيضاء",
                           [{"description": "خدمة استشارية", "quantity": 2, "unit_price": 500}])
    p_ar = a.generate_pdf(inv, lang="ar")
    p_fr = a.generate_pdf(inv, lang="fr")
    print(f"AR: {p_ar}")
    print(f"FR: {p_fr}")
