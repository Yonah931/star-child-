import os
from datetime import datetime
from fpdf import FPDF

class InvoiceAgent:
    def __init__(self, company_name="Yonah Tech", company_address="Casablanca, Maroc", company_ice="000000000000"):
        self.company_name = company_name
        self.company_address = company_address
        self.company_ice = company_ice
        self.invoices = []

    def create_invoice(self, client_name, client_address, items, tax_rate=0.20):
        subtotal = sum(i["quantity"] * i["unit_price"] for i in items)
        tax = subtotal * tax_rate
        total = subtotal + tax
        inv = {
            "number": f"INV-{datetime.now().strftime("%Y%m%d%H%M%S")}",
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
        pdf = FPDF()
        pdf.add_page()
        fp = "DejaVuSans.ttf"
        if not os.path.exists(fp):
            fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        pdf.add_font("DejaVu", "", fp, uni=True)
        fn = "DejaVu"
        pdf.set_fill_color(15, 20, 40)
        pdf.rect(0, 0, 210, 30, "F")
        pdf.set_font(fn, size=20)
        pdf.set_text_color(0, 212, 255)
        pdf.cell(0, 15, self.company_name, ln=True, align="C")
        pdf.set_font(fn, size=9)
        pdf.set_text_color(200, 200, 200)
        pdf.cell(0, 6, self.company_address, ln=True, align="C")
        pdf.cell(0, 6, f"ICE: {self.company_ice}", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font(fn, size=16)
        pdf.set_text_color(0, 100, 180)
        pdf.cell(0, 10, "FACTURE", ln=True, align="C")
        pdf.set_font(fn, size=10)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 7, f"N: {invoice["number"]}", ln=True, align="L")
        pdf.cell(0, 7, f"Date: {invoice["date"]}", ln=True, align="L")
        pdf.ln(3)
        pdf.cell(0, 7, invoice["client_name"], ln=True, align="L")
        pdf.cell(0, 7, invoice["client_address"], ln=True, align="L")
        pdf.ln(5)
        pdf.set_fill_color(200, 220, 240)
        pdf.set_text_color(0, 60, 120)
        hs = ["Desc", "Qte", "Prix", "Total"]
        ws = [90, 20, 35, 40]
        for h, w in zip(hs, ws):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_font(fn, size=9)
        pdf.set_text_color(30, 30, 30)
        for it in invoice["items"]:
            row = [it["description"], str(it["quantity"]), f"{it["unit_price"]:,.2f}", f"{it["quantity"]*it["unit_price"]:,.2f}"]
            for v, w in zip(row, ws):
                pdf.cell(w, 7, v, border=1, align="C")
            pdf.ln()
        pdf.ln(5)
        pdf.set_font(fn, size=11)
        for lb, vl in [("Sous-total", invoice["subtotal"]), (f"TVA {int(invoice["tax_rate"]*100)}%", invoice["tax"]), ("TOTAL", invoice["total"])]:
            pdf.cell(120, 8, lb, align="L")
            pdf.cell(50, 8, f"{vl:,.2f} MAD", ln=True)
        if filename is None:
            filename = f"{invoice["number"]}_{lang}.pdf"
        pdf.output(filename)
        return filename

if __name__ == "__main__":
    print("OK invoice.py ready")
    a = InvoiceAgent()
    inv = a.create_invoice("Client Test", "Casa", [{"description": "Service", "quantity": 2, "unit_price": 1500}])
    p = a.generate_pdf(inv, lang="fr")
    print(f"PDF: {p}")
