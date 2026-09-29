"""
Invoice Agent v4 — HTML/CSS + WeasyPrint
Arabic renders correctly in ALL PDF viewers (Chrome, Firefox, Evince, Okular...)
"""
import os
from datetime import datetime
from html import escape

from weasyprint import HTML, CSS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class InvoiceAgent:
    def __init__(self, company_name="Yonah Tech",
                 company_address="Casablanca, Maroc",
                 company_ice="000000000000"):
        self.company_name = company_name
        self.company_address = company_address
        self.company_ice = company_ice
        self.invoices = []

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

    def _build_html(self, invoice, lang="fr"):
        # اتجاه الصفحة
        direction = "rtl" if lang == "ar" else "ltr"
        align = "right" if lang == "ar" else "left"

        # العناوين حسب اللغة
        if lang == "ar":
            title = "فاتورة"
            lbl_client = "العميل"
            lbl_number = "رقم الفاتورة"
            lbl_date = "التاريخ"
            ths = ["الوصف", "الكمية", "السعر", "المجموع"]
            lbl_sub = "المجموع HT"
            lbl_tax = f"TVA {int(invoice['tax_rate']*100)}%"
            lbl_total = "المجموع TTC"
            currency = "MAD"
        else:
            title = "FACTURE"
            lbl_client = "Client"
            lbl_number = "N°"
            lbl_date = "Date"
            ths = ["Description", "Qté", "Prix", "Total"]
            lbl_sub = "Sous-total"
            lbl_tax = f"TVA {int(invoice['tax_rate']*100)}%"
            lbl_total = "TOTAL"
            currency = "MAD"

        # بناء صفوف البنود
        rows = ""
        for it in invoice["items"]:
            line_total = it["quantity"] * it["unit_price"]
            rows += f"""
            <tr>
                <td>{escape(str(it['description']))}</td>
                <td class="center">{it['quantity']}</td>
                <td class="center">{it['unit_price']:.2f}</td>
                <td class="center">{line_total:.2f}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="UTF-8">
<style>
@page {{ size: A4; margin: 15mm; }}
* {{ box-sizing: border-box; }}
body {{
    font-family: "Amiri", "DejaVu Sans", sans-serif;
    color: #1e1e1e;
    font-size: 12px;
    direction: {direction};
    text-align: {align};
}}
.header {{
    background: linear-gradient(90deg, #0f1428, #1a1f38);
    color: #00d4ff;
    padding: 20px;
    margin-bottom: 25px;
    border-radius: 6px;
}}
.header h1 {{
    margin: 0 0 6px 0;
    font-size: 24px;
    text-align: center;
}}
.header .sub {{
    color: #ccc;
    font-size: 10px;
    text-align: center;
}}
.header .ice {{
    color: #888;
    font-size: 9px;
    text-align: center;
    margin-top: 4px;
}}
.title {{
    color: #0064b4;
    text-align: center;
    font-size: 22px;
    margin: 10px 0 20px 0;
    font-weight: bold;
}}
.info-grid {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    font-size: 11px;
}}
.client-info {{
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    flex: 1;
    margin-{('left' if lang=='ar' else 'right')}: 15px;
    border-{('right' if lang=='ar' else 'left')}: 3px solid #0064b4;
}}
.client-info strong {{ color: #0064b4; }}
.invoice-info {{
    text-align: {('left' if lang=='ar' else 'right')};
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    direction: {direction};
}}
thead th {{
    background: #c8dcf0;
    color: #003c78;
    padding: 10px 8px;
    border: 1px solid #a8c4e0;
    font-size: 12px;
    text-align: center;
}}
tbody td {{
    padding: 8px;
    border: 1px solid #e0e0e0;
    font-size: 11px;
}}
tbody td.center {{ text-align: center; }}
.totals {{
    width: 320px;
    margin-{'right' if lang=='ar' else 'left'}: auto;
    margin-{'left' if lang=='ar' else 'right'}: 0;
    font-size: 13px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    overflow: hidden;
}}
.totals .row {{
    display: flex;
    justify-content: space-between;
    padding: 6px 10px;
    border-bottom: 1px solid #eee;
}}
.totals .row.final {{
    background: #0064b4;
    color: white;
    font-weight: bold;
    font-size: 15px;
    border-radius: 4px;
    margin-top: 8px;
}}
</style>
</head>
<body>
    <div class="header">
        <h1>{escape(self.company_name)}</h1>
        <div class="sub">{escape(self.company_address)}</div>
        <div class="ice">ICE: {escape(self.company_ice)}</div>
    </div>

    <div class="title">{title}</div>

    <div class="info-grid">
        <div class="client-info">
            <strong>{lbl_client}:</strong><br>
            {escape(str(invoice['client_name']))}<br>
            {escape(str(invoice['client_address'])) if invoice.get('client_address') else ''}
        </div>
        <div class="invoice-info">
            <strong>{lbl_number}:</strong> {escape(invoice['number'])}<br>
            <strong>{lbl_date}:</strong> {escape(invoice['date'])}
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>{ths[0]}</th>
                <th>{ths[1]}</th>
                <th>{ths[2]}</th>
                <th>{ths[3]}</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>

    <div class="totals">
        <div class="row">
            <span>{lbl_sub}</span>
            <span>{invoice['subtotal']:.2f} {currency}</span>
        </div>
        <div class="row">
            <span>{lbl_tax}</span>
            <span>{invoice['tax']:.2f} {currency}</span>
        </div>
        <div class="row final">
            <span>{lbl_total}</span>
            <span>{invoice['total']:.2f} {currency}</span>
        </div>
    </div>
</body>
</html>"""
        return html

    def generate_pdf(self, invoice, lang="fr", filename=None):
        html_content = self._build_html(invoice, lang=lang)

        if filename is None:
            filename = f"{invoice['number']}_{lang}.pdf"

        # خطوط Amiri
        font_css = ""
        for fp in [
            os.path.join(BASE_DIR, "Amiri-Regular.ttf"),
            os.path.join(os.path.expanduser("~"), ".fonts", "Amiri-Regular.ttf"),
        ]:
            if os.path.exists(fp):
                font_css = f"""
                @font-face {{
                    font-family: "Amiri";
                    src: url("file://{fp}");
                }}"""
                break

        HTML(string=html_content, base_url=BASE_DIR).write_pdf(
            filename,
            stylesheets=[CSS(string=font_css)] if font_css else None,
        )
        return filename


if __name__ == "__main__":
    print("OK invoice.py v4 (weasyprint) ready")
    a = InvoiceAgent()
    inv = a.create_invoice(
        "عميل تجريبي",
        "الدار البيضاء",
        [{"description": "خدمة استشارية", "quantity": 2, "unit_price": 500}]
    )
    p_ar = a.generate_pdf(inv, lang="ar")
    p_fr = a.generate_pdf(inv, lang="fr")
    print(f"AR: {p_ar}")
    print(f"FR: {p_fr}")
