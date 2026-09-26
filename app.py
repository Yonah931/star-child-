import streamlit as st
import os
from datetime import datetime
from accountant import AccountantAgent, generate_accounting_pdf
from translations import get_text
from hr import HRAgent
from cfo import CFOAgent
from reports import generate_hr_report, generate_cfo_report

# نظام الوكلاء السبعة
import sys
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Yonah Ashkenaz",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: bold; text-align: center;
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .sub-header {text-align: center; color: #666; margin-bottom: 2rem;}
    .feature-card {background: #f8f9fa; padding: 2rem; border-radius: 15px;
        border-left: 4px solid #00d4ff; margin: 1rem 0; height: 100%;}
    .feature-icon {font-size: 2.5rem; margin-bottom: 1rem;}
    .feature-title {font-size: 1.3rem; font-weight: bold; color: #0a0e1a; margin-bottom: 0.5rem;}
    .feature-desc {color: #555; line-height: 1.6;}
    .price-card {background: white; padding: 2rem; border-radius: 15px;
        border: 2px solid #e0e0e0; text-align: center; height: 100%;}
    .price-card.featured {border-color: #00d4ff; box-shadow: 0 0 30px rgba(0,212,255,0.2);}
    .price-amount {font-size: 2.5rem; font-weight: bold; color: #00d4ff; margin: 1rem 0;}
    .price-currency {font-size: 1rem; color: #888;}
    .issue-box {background: #fff3cd; padding: 1rem; border-radius: 10px;
        border-left: 4px solid #ffc107; margin: 0.5rem 0;}
    .success-box {background: #d4edda; padding: 1rem; border-radius: 10px;
        border-left: 4px solid #28a745; margin: 0.5rem 0;}
    .error-box {background: #f8d7da; padding: 1rem; border-radius: 10px;
        border-left: 4px solid #dc3545; margin: 0.5rem 0;}
    .stButton > button {background: linear-gradient(90deg, #00d4ff, #00ff88) !important;
        color: #0a0e1a !important; border: none !important; font-weight: bold !important;
        border-radius: 10px !important; padding: 0.75rem 2rem !important;}
</style>
""", unsafe_allow_html=True)

# === التنقل ===
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "lang" not in st.session_state:
    st.session_state.lang = "ar"


# ============================================================
# الصفحة 1: التسويقية
# ============================================================
def show_landing():
    st.markdown("""
    <div style="text-align:center; padding:3rem 1rem;
        background:linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%);
        border-radius:20px; margin-bottom:2rem;">
        <div class="main-header">📊 Yonah Ashkenaz</div>
        <div style="color:#a8b4c8; font-size:1.2rem; margin-top:1rem;">
            منصة الذكاء الاصطناعي لإدارة الأعمال
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🎯 اختر الحل المناسب لك")
    st.markdown("---")

    # === المنتجان ===
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">المحاسب الذكي</div>
            <div class="feature-desc">
                حلّل ملفات Excel المحاسبية في ثوانٍ.<br>
                اكتشف الأخطاء، احصل على تقارير PDF.<br>
                3 لغات: عربي / فرنسي / إنجليزي.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 جرّب المحاسب", key="go_accountant", use_container_width=True):
            st.session_state.page = "accountant"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">نظام الوكلاء السبعة</div>
            <div class="feature-desc">
                CEO + 6 وكلاء متخصصين.<br>
                بحث حقيقي، مبيعات، تسويق، برمجة، تحليل.<br>
                حل متكامل لإدارة الأعمال.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 جرّب الوكلاء", key="go_agents", use_container_width=True):
            st.session_state.page = "agents"
            st.rerun()

    # صف ثانٍ
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👥</div>
            <div class="feature-title">وكيل الموارد البشرية</div>
            <div class="feature-desc">
                فرز السير الذاتية، توليد إعلانات التوظيف،<br>
                أسئلة المقابلات، تحليل المرشحين.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 جرّب HR", key="go_hr", use_container_width=True):
            st.session_state.page = "hr"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <div class="feature-title">المدير المالي (CFO)</div>
            <div class="feature-desc">
                تحليل الربحية، حساب الضرائب،<br>
                التدفق النقدي، التوصيات المالية.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 جرّب CFO", key="go_cfo", use_container_width=True):
            st.session_state.page = "cfo"
            st.rerun()

    st.markdown("---")
    st.markdown("## 💰 الأسعار")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="price-card">
            <h3>Starter</h3>
            <div class="price-amount">500 <span class="price-currency">درهم/شهر</span></div>
            <p>✅ وكيل واحد من اختيارك</p>
            <p>✅ 20 مهمة شهرياً</p>
            <p>✅ دعم واتساب</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="price-card featured">
            <h3>Pro 🔥</h3>
            <div class="price-amount">1,200 <span class="price-currency">درهم/شهر</span></div>
            <p>✅ 3 وكلاء</p>
            <p>✅ 100 مهمة شهرياً</p>
            <p>✅ كل الميزات</p>
            <p>✅ دعم أولوية</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="price-card">
            <h3>Business</h3>
            <div class="price-amount">2,500 <span class="price-currency">درهم/شهر</span></div>
            <p>✅ كل الوكلاء (8)</p>
            <p>✅ غير محدود</p>
            <p>✅ تخصيص كامل</p>
            <p>✅ دعم 24/7</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:2rem;">
        <h2>📞 ابدأ اليوم</h2>
        <p>جرّب مجاناً لمدة 7 أيام، بدون التزام.</p>
        <p style="direction:ltr;">
            📧 <b>ashkenazyonah@gmail.com</b><br>
            💬 <b>WhatsApp: +212719082215</b>
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# الصفحة 2: المحاسب
# ============================================================
def show_accountant():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← الرئيسية", key="back_acc"):
            st.session_state.page = "landing"
            st.rerun()

    with st.sidebar:
        st.markdown("### 🌍 Language")
        lang = st.selectbox("Choisir", ["ar", "fr", "en"],
            format_func=lambda x: {"ar":"🇲🇦 العربية","fr":"🇫🇷 Français","en":"🇬🇧 English"}[x])
        st.session_state.lang = lang
        st.markdown("---")
        st.markdown(f"### 📁 {get_text(lang, 'upload_file')}")
        uploaded = st.file_uploader(get_text(lang, "choose_file"), type=['xlsx','xls','csv'])

    lang = st.session_state.lang
    st.markdown('<div class="main-header">📊 المحاسب الذكي</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{get_text(lang, "subtitle")}</div>', unsafe_allow_html=True)

    if uploaded is None:
        st.info(f"👈 {get_text(lang, 'upload_prompt')}")
        return

    temp_path = f"/tmp/{uploaded.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    agent = AccountantAgent()
    result = agent.load_file(temp_path)
    if not result['success']:
        st.error(f"❌ {get_text(lang,'file_error')}")
        return

    st.markdown(f"### 📂 {get_text(lang,'file_label')}: `{uploaded.name}`")
    st.markdown(f"**{get_text(lang,'rows_count')}:** {result['rows']} | **{get_text(lang,'columns_count')}:** {len(result['columns'])}")

    cols = agent.detect_columns()
    if not cols['debit'] or not cols['credit']:
        st.error(f"⚠️ {get_text(lang,'columns_error')}")
        return

    balance = agent.check_balance(cols['debit'], cols['credit'])
    issues = agent.find_issues(cols['debit'], cols['credit'], lang=lang)
    summary = agent.generate_summary(cols['debit'], cols['credit'])

    st.markdown("---")
    st.markdown(f"### 📊 {get_text(lang,'analysis_results')}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"📋 {get_text(lang,'rows_count')}", summary['total_rows'])
    c2.metric(f"💰 {get_text(lang,'total_debit')}", f"{summary['total_debit']:,.2f}")
    c3.metric(f"💵 {get_text(lang,'total_credit')}", f"{summary['total_credit']:,.2f}")
    c4.metric(f"⚠️ {get_text(lang,'issues_count')}", summary['issues_count'])

    st.markdown("---")
    if balance.get('balanced'):
        st.markdown(f'<div class="success-box">✅ {get_text(lang,"balance_ok")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="error-box">❌ {get_text(lang,"balance_warning")}<br>{get_text(lang,"difference")}: <b>{balance.get("difference",0):,.2f}</b></div>', unsafe_allow_html=True)

    st.markdown(f"### ⚠️ {get_text(lang,'issues')}")
    if issues:
        for i, issue in enumerate(issues, 1):
            st.markdown(f'<div class="issue-box">{i}. {issue}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="success-box">{get_text(lang,"no_issues")} ✅</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button(f"📥 {get_text(lang,'generate_pdf')}", key="pdf_acc"):
        pdf = generate_accounting_pdf(summary, balance, issues, lang=lang)
        with open(pdf, "rb") as f:
            st.download_button(f"⬇️ {get_text(lang,'download_pdf')}", f,
                file_name=f"report_{lang}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf")


# ============================================================
# الصفحة 3: نظام الوكلاء السبعة
# ============================================================
def show_agents():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← الرئيسية", key="back_agents"):
            st.session_state.page = "landing"
            st.rerun()

    st.markdown('<div class="main-header">🤖 نظام الوكلاء السبعة</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">CEO + 6 وكلاء متخصصين</div>', unsafe_allow_html=True)

    st.markdown("### 🎯 الوكلاء المتاحون")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**👑 CEO** — المنسق الرئيسي")
        st.markdown("**🤖 Assistant** — الأسئلة العامة")
        st.markdown("**🔍 Researcher** — بحث في الإنترنت")
    with col2:
        st.markdown("**📢 CMO** — التسويق والمحتوى")
        st.markdown("**💼 SalesRep** — المبيعات والعملاء")
        st.markdown("**💻 Dev** — التطوير التقني")
    with col3:
        st.markdown("**📊 DataAnalyst** — تحليل البيانات")

    st.markdown("---")
    st.success("✅ النظام جاهز ويعمل على السحابة")

    st.markdown("### 📝 افتح التطبيق الكامل")
    st.markdown("انقر على الرابط أدناه لفتح النظام الكامل (7 وكلاء):")

    st.link_button(
        "🚀 افتح نظام الوكلاء السبعة",
        "https://yonah-agents.streamlit.app",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("### 🎯 أو جرّب المحاسب الذكي")
    if st.button("📊 فتح المحاسب", key="go_acc_from_agents", use_container_width=True):
        st.session_state.page = "accountant"
        st.rerun()


# ============================================================
# الصفحة 4: وكيل HR
# ============================================================
def show_hr():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← الرئيسية", key="back_hr"):
            st.session_state.page = "landing"
            st.rerun()

    st.markdown('<div class="main-header">👥 وكيل الموارد البشرية</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">فرز CV • إعلانات توظيف • أسئلة مقابلات</div>', unsafe_allow_html=True)

    # التبويبات
    tab1, tab2, tab3 = st.tabs(["🔍 فرز CV", "📢 إعلان توظيف", "❓ أسئلة المقابلة"])

    # === تبويب 1: فرز CV ===
    with tab1:
        st.markdown("### ارفع ملف السير الذاتية (Excel/CSV)")
        st.markdown("يجب أن يحتوي الملف على أعمدة: `Name`, `Email`, `Experience`, `Skills`")

        uploaded = st.file_uploader("اختر الملف", type=['xlsx', 'xls', 'csv'], key="hr_cv_upload")

        if uploaded:
            temp_path = f"/tmp/{uploaded.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded.getbuffer())

            hr = HRAgent()
            result = hr.load_cvs(temp_path)

            if not result['success']:
                st.error(f"❌ خطأ: {result['error']}")
            else:
                st.success(f"✅ تم تحميل {result['count']} سيرة ذاتية")

                st.markdown("---")
                st.markdown("### ⚙️ معايير الفرز")

                col1, col2 = st.columns(2)
                with col1:
                    skills_input = st.text_input("المهارات المطلوبة (مفصولة بفاصلة)", "Python, Git, SQL")
                with col2:
                    min_exp = st.number_input("الحد الأدنى للخبرة (سنوات)", 0, 20, 2)

                if st.button("🔍 ابدأ الفرز", key="hr_screen_btn", use_container_width=True):
                    skills = [s.strip() for s in skills_input.split(',')]
                    candidates = hr.screen_cvs(required_skills=skills, min_experience=min_exp, lang='ar')
                    stats = hr.get_statistics()
                    # حفظ النتائج
                    st.session_state['hr_candidates'] = candidates
                    st.session_state['hr_stats'] = stats
                    st.session_state['hr_screened'] = True

                # عرض النتائج (حتى بعد إعادة التشغيل)
                if st.session_state.get('hr_screened'):
                    candidates = st.session_state['hr_candidates']
                    stats = st.session_state['hr_stats']

                    st.markdown("---")
                    st.markdown(f"### 🏆 أفضل المرشحين ({len(candidates)})")

                    for i, c in enumerate(candidates, 1):
                        with st.expander(f"#{i} {c['name']} — {c['score']}/100"):
                            st.markdown(f"**📧 البريد:** {c['email']}")
                            st.markdown(f"**💼 الخبرة:** {c['experience']} سنوات")
                            st.markdown(f"**✅ المهارات المطابقة:** {', '.join(c['matched_skills']) or '—'}")

                    st.markdown("---")
                    st.markdown("### 📊 الإحصائيات")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("📋 المرشحون", stats.get('total_candidates', 0))
                    c2.metric("⭐ متوسط النقاط", stats.get('average_score', 0))
                    c3.metric("💼 متوسط الخبرة", f"{stats.get('average_experience', 0)} سنوات")
                    c4.metric("🏆 الأفضل", stats.get('top_candidate', '—'))

                    # === زر تقرير PDF ===
                    st.markdown("---")
                    st.markdown("### 📄 توليد التقرير")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("📥 تقرير PDF (عربي)", key="hr_pdf_ar", use_container_width=True):
                            with st.spinner("جاري التوليد..."):
                                pdf_path = generate_hr_report(candidates, stats, lang='ar')
                                with open(pdf_path, "rb") as f:
                                    st.session_state['hr_pdf_ar_bytes'] = f.read()
                                st.session_state['hr_pdf_ar_ready'] = True
                    with col_b:
                        if st.button("📥 Rapport PDF (Français)", key="hr_pdf_fr", use_container_width=True):
                            with st.spinner("Génération..."):
                                pdf_path = generate_hr_report(candidates, stats, lang='fr')
                                with open(pdf_path, "rb") as f:
                                    st.session_state['hr_pdf_fr_bytes'] = f.read()
                                st.session_state['hr_pdf_fr_ready'] = True

                    # أزرار التحميل
                    if st.session_state.get('hr_pdf_ar_ready'):
                        st.download_button(
                            "⬇️ تحميل التقرير العربي",
                            st.session_state['hr_pdf_ar_bytes'],
                            file_name=f"hr_report_ar_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    if st.session_state.get('hr_pdf_fr_ready'):
                        st.download_button(
                            "⬇️ Télécharger le rapport",
                            st.session_state['hr_pdf_fr_bytes'],
                            file_name=f"hr_report_fr_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

    # === تبويب 2: إعلان توظيف ===
    with tab2:
        st.markdown("### 📢 توليد إعلان توظيف")

        col1, col2 = st.columns(2)
        with col1:
            job_type = st.selectbox("نوع الوظيفة",
                options=["developer", "accountant", "sales", "marketing", "hr"],
                format_func=lambda x: {
                    "developer": "💻 مطور برمجيات",
                    "accountant": "📊 محاسب",
                    "sales": "💼 مندوب مبيعات",
                    "marketing": "📢 مسؤول تسويق",
                    "hr": "👥 مسؤول HR"
                }[x])
        with col2:
            company_name = st.text_input("اسم الشركة", "Yonah Tech")

        lang_job = st.selectbox("اللغة", ["ar", "fr", "en"],
            format_func=lambda x: {"ar": "🇲🇦 العربية", "fr": "🇫🇷 Français", "en": "🇬🇧 English"}[x])

        if st.button("📢 توليد الإعلان", key="hr_job_btn", use_container_width=True):
            hr = HRAgent()
            posting = hr.generate_job_posting(job_type, company_name, lang=lang_job)
            st.markdown("---")
            st.markdown("### 📄 الإعلان الجاهز")
            st.text_area("", posting, height=400)

    # === تبويب 3: أسئلة المقابلة ===
    with tab3:
        st.markdown("### ❓ أسئلة المقابلة")

        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("الفئة", ["general", "technical"],
                format_func=lambda x: {"general": "📋 عامة", "technical": "💼 تقنية"}[x])
        with col2:
            lang_q = st.selectbox("اللغة ", ["ar", "fr", "en"],
                format_func=lambda x: {"ar": "🇲🇦 العربية", "fr": "🇫🇷 Français", "en": "🇬🇧 English"}[x])

        if st.button("❓ توليد الأسئلة", key="hr_q_btn", use_container_width=True):
            hr = HRAgent()
            questions = hr.get_interview_questions(category, lang_q)
            st.markdown("---")
            for i, q in enumerate(questions, 1):
                st.markdown(f"**{i}.** {q}")


# ============================================================
# الصفحة 5: وكيل CFO
# ============================================================
def show_cfo():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← الرئيسية", key="back_cfo"):
            st.session_state.page = "landing"
            st.rerun()

    st.markdown('<div class="main-header">💰 المدير المالي (CFO)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">تحليل الربحية • حساب الضرائب • التدفق النقدي • التوصيات</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 📁 رفع البيانات المالية")
        uploaded = st.file_uploader(
            "ملف Excel/CSV",
            type=['xlsx', 'xls', 'csv'],
            key="cfo_upload"
        )
        st.markdown("---")
        st.markdown("### ℹ️ الأعمدة المطلوبة")
        st.markdown("""
        - **Revenus** أو **Revenue** (الإيرادات)
        - **Dépenses** أو **Expense** (المصاريف)
        - **Date** (التاريخ) — اختياري
        """)

    if uploaded is None:
        st.info("👈 ارفع ملف البيانات المالية من الشريط الجانبي")
        return

    temp_path = f"/tmp/{uploaded.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    cfo = CFOAgent()
    result = cfo.load_file(temp_path)

    if not result['success']:
        st.error(f"❌ خطأ: {result['error']}")
        return

    st.markdown(f"### 📂 الملف: `{uploaded.name}`")
    st.markdown(f"**عدد الصفوف:** {result['rows']}")

    cols = cfo.detect_columns()
    if not cols['revenue'] or not cols['expense']:
        st.error("⚠️ لم يتم العثور على أعمدة الإيرادات والمصاريف")
        st.write("**الأعمدة المكتشفة:**", result['columns'])
        return

    # التحليل
    cfo.analyze_profitability(cols['revenue'], cols['expense'])
    cfo.calculate_taxes()
    cfo.analyze_cash_flow()
    cfo.generate_recommendations()

    summary = cfo.summary
    taxes = cfo.taxes

    st.markdown("---")
    st.markdown("### 📊 تحليل الربحية")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 إجمالي الإيرادات", f"{summary['total_revenue']:,.2f}")
    c2.metric("💸 إجمالي المصاريف", f"{summary['total_expense']:,.2f}")
    c3.metric("📈 الربح الصافي", f"{summary['net_profit']:,.2f}")
    c4.metric("🎯 الهامش", f"{summary['margin_percent']}%")

    st.markdown("---")
    st.markdown("### 💰 الضرائب (المغرب 2026)")

    t1, t2, t3, t4 = st.columns(4)
    t1.metric("TVA (20%)", f"{taxes['tva']:,.2f}")
    t2.metric("IS (20%)", f"{taxes['is']:,.2f}")
    t3.metric("CNSS (26.77%)", f"{taxes['cnss']:,.2f}")
    t4.metric("إجمالي الضرائب", f"{taxes['total_taxes']:,.2f}")

    st.markdown("---")
    st.markdown("### 💵 التدفق النقدي")

    f1, f2 = st.columns(2)
    f1.metric("Cash Flow", f"{summary['cash_flow']:,.2f}")
    f2.metric("معدل الاستهلاك الشهري", f"{summary['monthly_burn']:,.2f}")

    st.markdown("---")
    st.markdown("### 💡 التوصيات الذكية")

    for insight in cfo.insights:
        itype = insight['type']
        msg = insight['message']

        if itype == 'success':
            st.markdown(f'<div class="success-box">{msg}</div>', unsafe_allow_html=True)
        elif itype == 'warning':
            st.markdown(f'<div class="issue-box">{msg}</div>', unsafe_allow_html=True)
        elif itype == 'danger':
            st.markdown(f'<div class="error-box">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-box">{msg}</div>', unsafe_allow_html=True)

    # === زر تقرير PDF ===
    st.markdown("---")
    st.markdown("### 📄 توليد التقرير المالي")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📥 تقرير PDF (عربي)", key="cfo_pdf_ar", use_container_width=True):
            with st.spinner("جاري التوليد..."):
                pdf_path = generate_cfo_report(cfo.summary, cfo.taxes, cfo.insights, lang='ar')
                with open(pdf_path, "rb") as f:
                    st.session_state['cfo_pdf_ar_bytes'] = f.read()
                st.session_state['cfo_pdf_ar_ready'] = True
    with col_b:
        if st.button("📥 Rapport PDF (Français)", key="cfo_pdf_fr", use_container_width=True):
            with st.spinner("Génération..."):
                pdf_path = generate_cfo_report(cfo.summary, cfo.taxes, cfo.insights, lang='fr')
                with open(pdf_path, "rb") as f:
                    st.session_state['cfo_pdf_fr_bytes'] = f.read()
                st.session_state['cfo_pdf_fr_ready'] = True

    # أزرار التحميل
    if st.session_state.get('cfo_pdf_ar_ready'):
        st.download_button(
            "⬇️ تحميل التقرير العربي",
            st.session_state['cfo_pdf_ar_bytes'],
            file_name=f"cfo_report_ar_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    if st.session_state.get('cfo_pdf_fr_ready'):
        st.download_button(
            "⬇️ Télécharger le rapport",
            st.session_state['cfo_pdf_fr_bytes'],
            file_name=f"cfo_report_fr_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ============================================================
# Router
# ============================================================
if st.session_state.page == "landing":
    show_landing()
elif st.session_state.page == "accountant":
    show_accountant()
elif st.session_state.page == "agents":
    show_agents()
elif st.session_state.page == "hr":
    show_hr()
elif st.session_state.page == "cfo":
    show_cfo()
