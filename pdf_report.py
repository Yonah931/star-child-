import os
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF
from datetime import datetime

def fix_arabic(text):
    """إصلاح النص العربي ليكون مقروءاً في PDF"""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)

def generate_pdf(messages, filename="sureflow_report.pdf"):
    """توليد تقرير PDF من المحادثة"""
    pdf = FPDF()
    pdf.add_page()
    
    font_path = "Amiri-Regular.ttf"
    pdf.add_font("Amiri", "", font_path, uni=True)
    
    # === الترويسة ===
    pdf.set_fill_color(10, 14, 26)
    pdf.rect(0, 0, 210, 40, "F")
    
    pdf.set_font("Amiri", size=24)
    pdf.set_text_color(0, 212, 255)
    pdf.cell(0, 20, fix_arabic("Sureflow Agentic OS"), ln=True, align="C")
    
    pdf.set_font("Amiri", size=11)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 10, fix_arabic(f"تقرير المهام - {datetime.now().strftime('%Y-%m-%d %H:%M')}"), ln=True, align="C")
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    
    # === ملخص ===
    pdf.set_font("Amiri", size=14)
    pdf.set_fill_color(240, 240, 240)
    total_msgs = len(messages)
    user_msgs = sum(1 for m in messages if m["role"] == "user")
    pdf.cell(0, 10, fix_arabic(f"ملخص: {user_msgs} مهمة من أصل {total_msgs} رسالة"), ln=True, align="R", fill=True)
    pdf.ln(5)
    
    # === المحتوى ===
    for i, msg in enumerate(messages, 1):
        role_label = "👤 المستخدم" if msg["role"] == "user" else "🤖 النظام"
        content = fix_arabic(msg["content"])
        
        pdf.set_font("Amiri", size=11)
        pdf.set_text_color(0, 100, 180)
        pdf.cell(0, 8, fix_arabic(f"{role_label}:"), ln=True, align="R")
        
        pdf.set_font("Amiri", size=10)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 6, content, align="R")
        pdf.ln(4)
        
        # فاصل بين الرسائل
        if i < len(messages):
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
    
    # === التذييل ===
    pdf.set_y(-25)
    pdf.set_font("Amiri", size=8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, fix_arabic("تم إنشاء هذا التقرير تلقائياً بواسطة Sureflow Agentic OS"), ln=True, align="C")
    
    pdf.output(filename)
    return filename
