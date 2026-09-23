import streamlit as st

st.set_page_config(
    page_title="Yonah Ashkenaz - المحاسب الذكي",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .hero {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .hero-subtitle {
        color: #a8b4c8;
        font-size: 1.2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid #00d4ff;
        margin: 1rem 0;
        height: 100%;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #0a0e1a;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        color: #555;
        line-height: 1.6;
    }
    .cta-button {
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        color: #0a0e1a;
        padding: 1rem 3rem;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.1rem;
        display: inline-block;
        margin-top: 1rem;
    }
    .price-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        text-align: center;
        height: 100%;
    }
    .price-card.featured {
        border-color: #00d4ff;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
    }
    .price-amount {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00d4ff;
        margin: 1rem 0;
    }
    .price-currency {
        font-size: 1rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# === Hero Section ===
st.markdown("""
<div class="hero">
    <div class="hero-title">📊 Yonah Ashkenaz</div>
    <div class="hero-subtitle">المحاسب الذكي - وفّر 10 ساعات أسبوعياً في مراجعة بيانات عملائك</div>
</div>
""", unsafe_allow_html=True)

# === CTA ===
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align:center;">
        <a href="http://localhost:8502" target="_blank" class="cta-button">
            🚀 جرّب مجاناً الآن
        </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === الميزات ===
st.markdown("## ✨ لماذا Yonah Ashkenaz؟")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">سرعة فائقة</div>
        <div class="feature-desc">
            حلّل ملفات Excel بمئات الصفوف في ثوانٍ معدودة.
            لا مزيد من المراجعة اليدوية المملة.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">اكتشاف الأخطاء</div>
        <div class="feature-desc">
            يكشف القيم السالبة، الصفوف المكررة، الأرقام الضخمة،
            والقيود الناقصة تلقائياً.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <div class="feature-title">تقارير احترافية</div>
        <div class="feature-desc">
            تقارير PDF بالعربية والفرنسية والإنجليزية،
            جاهزة للإرسال للعملاء.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === كيف يعمل ===
st.markdown("## 🎯 كيف يعمل؟")

col1, col2, col3, col4 = st.columns(4)

steps = [
    ("1️⃣", "ارفع الملف", "Excel أو CSV من أي نظام محاسبي"),
    ("2️⃣", "انتظر ثوانٍ", "التحليل يحدث تلقائياً"),
    ("3️⃣", "راجع النتائج", "قائمة الأخطاء والملاحظات"),
    ("4️⃣", "حمّل PDF", "تقرير جاهز للعميل"),
]

for i, (icon, title, desc) in enumerate(steps):
    with [col1, col2, col3, col4][i]:
        st.markdown(f"""
        <div style="text-align:center; padding:1rem;">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-weight:bold; margin:0.5rem 0;">{title}</div>
            <div style="color:#666; font-size:0.9rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# === الأسعار ===
st.markdown("## 💰 الأسعار")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="price-card">
        <h3>Basic</h3>
        <div class="price-amount">500 <span class="price-currency">درهم/شهر</span></div>
        <p>10 ملفات شهرياً</p>
        <p>✓ تحليل كامل</p>
        <p>✓ تقارير PDF</p>
        <p>✓ دعم واتساب</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="price-card featured">
        <h3>Pro 🔥</h3>
        <div class="price-amount">1,200 <span class="price-currency">درهم/شهر</span></div>
        <p>50 ملف شهرياً</p>
        <p>✓ كل ميزات Basic</p>
        <p>✓ 3 لغات</p>
        <p>✓ تقارير مخصصة</p>
        <p>✓ دعم أولوية</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="price-card">
        <h3>Business</h3>
        <div class="price-amount">2,500 <span class="price-currency">درهم/شهر</span></div>
        <p>غير محدود</p>
        <p>✓ كل ميزات Pro</p>
        <p>✓ تخصيص كامل</p>
        <p>✓ API للربط</p>
        <p>✓ دعم 24/7</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === التواصل ===
st.markdown("""
<div style="text-align:center; padding:2rem;">
    <h2>📞 ابدأ اليوم</h2>
    <p style="font-size:1.1rem; color:#666;">جرّب مجاناً لمدة 7 أيام، بدون التزام.</p>
    <p style="font-size:1.2rem; margin-top:1rem; direction:ltr; text-align:center;">
        📧 <b>ashkenazyonah@gmail.com</b><br>
        💬 💬 <b>WhatsApp: +212719082215</b>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.9rem;">
    © 2026 Yonah Ashkenaz - جميع الحقوق محفوظة
</div>
""", unsafe_allow_html=True)
