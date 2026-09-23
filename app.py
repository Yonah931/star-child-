import streamlit as st
import os
from datetime import datetime
from accountant import AccountantAgent, generate_accounting_pdf
from translations import get_text

st.set_page_config(
    page_title="Yonah Ashkenaz",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === CSS مشترك ===
st.markdown("""
<style>
    /* Hero */
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
    .hero-subtitle {color: #a8b4c8; font-size: 1.2rem;}
    
    /* Features */
    .feature-card {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid #00d4ff;
        margin: 1rem 0;
        height: 100%;
    }
    .feature-icon {font-size: 2.5rem; margin-bottom: 1rem;}
    .feature-title {font-size: 1.3rem; font-weight: bold; color: #0a0e1a; margin-bottom: 0.5rem;}
    .feature-desc {color: #555; line-height: 1.6;}
    
    /* Price cards */
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
    .price-amount {font-size: 2.5rem; font-weight: bold; color: #00d4ff; margin: 1rem 0;}
    .price-currency {font-size: 1rem; color: #888;}
    
    /* Result boxes */
    .issue-box {background: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 4px solid #ffc107; margin: 0.5rem 0;}
    .success-box {background: #d4edda; padding: 1rem; border-radius: 10px; border-left: 4px solid #28a745; margin: 0.5rem 0;}
    .error-box {background: #f8d7da; padding: 1rem; border-radius: 10px; border-left: 4px solid #dc3545; margin: 0.5rem 0;}
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff, #00ff88) !important;
        color: #0a0e1a !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(90deg, #00ff88, #00d4ff) !important;
        color: #0a0e1a !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    
    /* Header app */
    .app-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .app-sub {text-align: center; color: #666; margin-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

# === إدارة الصفحات ===
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "lang" not in st.session_state:
    st.session_state.lang = "ar"


# =====================================================
# الصفحة 1: Landing Page (التسويقية)
# =====================================================
def show_landing():
    st.markdown("""
    <div class="hero">
        <div class="hero-title">📊 Yonah Ashkenaz</div>
        <div class="hero-subtitle">المحاسب الذكي - وفّر 10 ساعات أسبوعياً في مراجعة بيانات عملائك</div>
    </div>
    """, unsafe_allow_html=True)

    # CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 جرّب مجاناً الآن", use_container_width=True, key="cta_btn"):
            st.session_state.page = "app"
            st.rerun()

    st.markdown("---")
    st.markdown("## ✨ لماذا Yonah Ashkenaz؟")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">سرعة فائقة</div>
            <div class="feature-desc">حلّل ملفات Excel بمئات الصفوف في ثوانٍ. لا مزيد من المراجعة اليدوية المملة.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">اكتشاف الأخطاء</div>
            <div class="feature-desc">يكشف القيم السالبة، الصفوف المكررة، الأرقام الضخمة، والقيود الناقصة تلقائياً.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">تقارير احترافية</div>
            <div class="feature-desc">تقارير PDF بالعربية والفرنسية والإنجليزية، جاهزة للإرسال للعملاء.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🎯 كيف يعمل؟")
    col1, col2, col3, col4 = st.columns(4)
    steps = [
        ("1️⃣", "ارفع الملف", "Excel أو CSV"),
        ("2️⃣", "انتظر ثوانٍ", "تحليل تلقائي"),
        ("3️⃣", "راجع النتائج", "قائمة الأخطاء"),
        ("4️⃣", "حمّل PDF", "تقرير جاهز"),
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
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:2rem;">
        <h2>📞 ابدأ اليوم</h2>
        <p style="font-size:1.1rem; color:#666;">جرّب مجاناً لمدة 7 أيام، بدون التزام.</p>
        <p style="font-size:1.2rem; margin-top:1rem; direction:ltr; text-align:center;">
            📧 <b>ashkenazyonah@gmail.com</b><br>
            💬 <b>WhatsApp: +212719082215</b>
        </p>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# الصفحة 2: تطبيق المحاسب
# =====================================================
def show_app():
    # زر الرجوع
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← الرئيسية", key="back_btn"):
            st.session_state.page = "landing"
            st.rerun()

    # اختيار اللغة
    with st.sidebar:
        st.markdown("### 🌍 Language")
        lang_choice = st.selectbox(
            "Choisir la langue",
            options=["ar", "fr", "en"],
            format_func=lambda x: {"ar": "🇲🇦 العربية", "fr": "🇫🇷 Français", "en": "🇬🇧 English"}[x],
            index=["ar", "fr", "en"].index(st.session_state.lang)
        )
        st.session_state.lang = lang_choice

        st.markdown("---")
        st.markdown(f"### 📁 {get_text(lang_choice, 'upload_file')}")
        uploaded = st.file_uploader(
            get_text(lang_choice, "choose_file"),
            type=['xlsx', 'xls', 'csv']
        )
        st.markdown("---")
        st.markdown("### ℹ️ Steps")
        st.markdown(f"""
        {get_text(lang_choice, 'step1')}
        
        {get_text(lang_choice, 'step2')}
        
        {get_text(lang_choice, 'step3')}
        
        {get_text(lang_choice, 'step4')}
        """)

    lang = st.session_state.lang

    st.markdown('<div class="app-header">📊 Yonah Ashkenaz</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-sub">{get_text(lang, "subtitle")}</div>', unsafe_allow_html=True)

    if uploaded is None:
        st.info(f"👈 {get_text(lang, 'upload_prompt')}")
        return

    temp_path = f"/tmp/{uploaded.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    agent = AccountantAgent()
    load_result = agent.load_file(temp_path)

    if not load_result['success']:
        st.error(f"❌ {get_text(lang, 'file_error')}: {load_result.get('error')}")
        return

    st.markdown(f"### 📂 {get_text(lang, 'file_label')}: `{uploaded.name}`")
    st.markdown(f"**{get_text(lang, 'rows_count')}:** {load_result['rows']} | **{get_text(lang, 'columns_count')}:** {len(load_result['columns'])}")

    cols = agent.detect_columns()
    if not cols['debit'] or not cols['credit']:
        st.error(f"⚠️ {get_text(lang, 'columns_error')}")
        st.write("**Columns detected:**", load_result['columns'])
        return

    balance = agent.check_balance(cols['debit'], cols['credit'])
    issues = agent.find_issues(cols['debit'], cols['credit'], lang=lang)
    summary = agent.generate_summary(cols['debit'], cols['credit'])

    st.markdown("---")
    st.markdown(f"### 📊 {get_text(lang, 'analysis_results')}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(f"📋 {get_text(lang, 'rows_count')}", summary['total_rows'])
    with c2:
        st.metric(f"💰 {get_text(lang, 'total_debit')}", f"{summary['total_debit']:,.2f}")
    with c3:
        st.metric(f"💵 {get_text(lang, 'total_credit')}", f"{summary['total_credit']:,.2f}")
    with c4:
        st.metric(f"⚠️ {get_text(lang, 'issues_count')}", summary['issues_count'])

    st.markdown("---")

    if balance.get('balanced'):
        st.markdown(f'<div class="success-box"><b>✅ {get_text(lang, "balance_ok")}</b></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="error-box"><b>❌ {get_text(lang, "balance_warning")}</b><br>{get_text(lang, "difference")}: <b>{balance.get("difference", 0):,.2f}</b></div>', unsafe_allow_html=True)

    st.markdown(f"### ⚠️ {get_text(lang, 'issues')}")
    if issues:
        for i, issue in enumerate(issues, 1):
            st.markdown(f'<div class="issue-box">{i}. {issue}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="success-box">{get_text(lang, "no_issues")} ✅</div>', unsafe_allow_html=True)

    st.markdown("---")
    with st.expander(f"👁️ {get_text(lang, 'preview')}"):
        st.dataframe(agent.df.head(10))

    st.markdown("---")
    st.markdown(f"### 📄 {get_text(lang, 'report')}")

    if st.button(f"📥 {get_text(lang, 'generate_pdf')}", use_container_width=True, key="pdf_btn"):
        with st.spinner(get_text(lang, "generating")):
            pdf_file = generate_accounting_pdf(summary, balance, issues, lang=lang)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    f"⬇️ {get_text(lang, 'download_pdf')}",
                    f,
                    file_name=f"report_{lang}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )


# === Router ===
if st.session_state.page == "landing":
    show_landing()
else:
    show_app()
