import streamlit as st
import os
from datetime import datetime
from accountant import AccountantAgent, generate_accounting_pdf
from translations import get_text
from hr import HRAgent
from cfo import CFOAgent
from reports import generate_hr_report, generate_cfo_report
from invoice import InvoiceAgent
from moroccan_admin import MoroccanAdmin
from customer_support import CustomerSupportAgent
from content_writer import ContentWriterAgent
from email_agent import EmailAgent
from social_media import SocialMediaAgent
from meeting_notes import MeetingNotesAgent
from supplier_agent import SupplierAgent
import streamlit_authenticator as stauth
import yaml

# نظام الوكلاء السبعة
import sys
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Yonah Ashkenaz",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# تسجيل الدخول (Authentication)
# ============================================
import os as _os
_auth_file = _os.path.join(_os.path.dirname(__file__), "auth_config.yaml")

if _os.path.exists(_auth_file):
    with open(_auth_file, "r", encoding="utf-8") as _f:
        _auth_config = yaml.safe_load(_f)

    _authenticator = stauth.Authenticate(
        _auth_config["credentials"],
        _auth_config["cookie"]["name"],
        _auth_config["cookie"]["key"],
        _auth_config["cookie"]["expiry_days"],
    )

    _authenticator.login(
        location="main",
        key="main_login",
        fields={
            "Form name": "🔐 تسجيل الدخول",
            "Username": "اسم المستخدم",
            "Password": "كلمة السر",
            "Login": "دخول",
        },
    )

    if st.session_state.get("authentication_status") is False:
        st.error("❌ اسم المستخدم أو كلمة السر خاطئة")
        st.stop()
    elif st.session_state.get("authentication_status") is None:
        st.warning("🔒 يرجى تسجيل الدخول للمتابعة")
        st.stop()
    else:
        # عرض شريط علوي مع اسم المستخدم وزر خروج
        _col1, _col2 = st.columns([4, 1])
        with _col1:
            st.caption(f"👋 مرحباً **{st.session_state.get('name', 'مستخدم')}**")
        with _col2:
            if st.button("📊 لوحتي", key="goto_dash"):
                st.session_state.page = "dashboard"
                st.rerun()
        with st.container():
            _authenticator.logout(location="main", key="main_logout")



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


# ============================================
# مساعد: رابط واتساب مع رسالة
# ============================================
def make_whatsapp_link(plan_name, price):
    import urllib.parse
    number = "212719082215"
    message = f"مرحباً، أرغب في الاشتراك في حزمة *{plan_name}* ({price} درهم/شهر). هل يمكنكم مساعدتي؟"
    return f"https://wa.me/{number}?text={urllib.parse.quote(message)}"

def show_dashboard():
    """لوحة تحكم العميل"""
    st.markdown('<div class="main-header">📊 لوحة التحكم</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">نظرة عامة على حسابك</div>', unsafe_allow_html=True)

    # معلومات المستخدم
    if st.button("⬅️ رجوع", key="dash_back"):
        st.session_state.page = "landing"
        st.rerun()

    name = st.session_state.get("name", "مستخدم")
    username = st.session_state.get("username", "")
    roles = st.session_state.get("roles") or []

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("👤 المستخدم", name)
    with c2:
        st.metric("🏷️ الحساب", username)
    with c3:
        plan = "Business" if "admin" in roles else "Starter"
        st.metric("💎 الحزمة", plan)

    st.divider()

    # إحصائيات سريعة
    st.markdown("### 📈 إحصائيات سريعة")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🤖 الوكلاء المتاحون", "12")
    c2.metric("🌍 اللغات المدعومة", "3")
    c3.metric("📅 منذ التسجيل", "اليوم")
    c4.metric("⚡ الاستخدام", "غير محدود")

    st.divider()

    # اختصارات سريعة
    st.markdown("### ⚡ اختصارات سريعة")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🧾 فاتورة جديدة", use_container_width=True, key="dash_inv"):
            st.session_state.page = "invoice"
            st.rerun()
    with c2:
        if st.button("📞 دعم العملاء", use_container_width=True, key="dash_cs"):
            st.session_state.page = "customer_support"
            st.rerun()
    with c3:
        if st.button("✍️ محتوى جديد", use_container_width=True, key="dash_cw"):
            st.session_state.page = "content_writer"
            st.rerun()

    st.divider()

    # التواصل
    st.markdown("### 📞 تواصل مع الدعم")
    st.markdown("""
    - 📧 **البريد:** ashkenazyonah@gmail.com
    - 💬 **واتساب:** +212719082215
    """)


def show_features():
    """صفحة الميزات التفصيلية"""
    st.markdown('<div class="main-header">✨ الميزات الكاملة</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">12 وكيلاً ذكياً لإدارة أعمالك</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="feat_back"):
        st.session_state.page = "landing"
        st.rerun()

    st.divider()
    st.markdown("### 🤖 الوكلاء المالية والمحاسبية")

    features = [
        ("📊 المحاسب الذكي", "يقرأ Excel/CSV، يكشف الأخطاء، يولّد تقارير PDF بـ 3 لغات", "AI"),
        ("💰 المدير المالي (CFO)", "تحليل الربحية، حساب TVA/IS/CNSS، توصيات ذكية", "AI"),
        ("🇲🇦 Moroccan Admin", "TVA، IS، IR، CNSS، Payroll، تقويم ضريبي مغربي", "AI"),
        ("🧾 وكيل الفواتير", "فواتير احترافية مع ICE، TVA تلقائي، PDF بـ 3 لغات", "AI"),
    ]

    for name, desc, badge in features:
        with st.expander(f"{name}"):
            st.markdown(f"**الوصف:** {desc}")
            st.markdown(f"**التقنية:** {badge}")

    st.divider()
    st.markdown("### 📢 الوكلاء التسويقية")

    marketing = [
        ("✍️ كاتب المحتوى", "مقالات، وصف منتجات، سوشيال ميديا، إعلانات (6 أنواع)"),
        ("📱 Social Media", "منشورات لـ 6 منصات (Facebook, Instagram, LinkedIn, X, TikTok, WhatsApp)"),
        ("📧 البريد الإلكتروني", "ردود، حملات، متابعة، دعوات (7 أنواع)"),
        ("🎨 CMO (المسؤول التسويقي)", "استراتيجيات تسويق متكاملة"),
    ]

    for name, desc in marketing:
        with st.expander(f"{name}"):
            st.markdown(desc)

    st.divider()
    st.markdown("### 👥 الوكلاء الإدارية والدعم")

    admin = [
        ("👥 HR Agent", "فرز CVs، إعلانات توظيف، أسئلة مقابلات"),
        ("📞 Customer Support", "تصنيف التذاكر، ردود AI، اقتراح إجراءات"),
        ("📝 Meeting Notes", "محاضر اجتماعات مع مهام وقرارات"),
        ("🚚 Supplier Agent", "طلبات، تفاوض، مقارنة موردين"),
    ]

    for name, desc in admin:
        with st.expander(f"{name}"):
            st.markdown(desc)

    st.divider()
    st.markdown("### 🎯 ميزات إضافية")
    st.markdown("""
    - 🌍 **3 لغات:** عربي، فرنسي، إنجليزي
    - 📄 **تقارير PDF** احترافية
    - 🔒 **تسجيل دخول آمن**
    - ⚡ **سريع** (نتائج في ثوانٍ)
    - ☁️ **سحابي** (يعمل من أي جهاز)
    - 💬 **دعم واتساب مباشر**
    """)

    st.divider()
    if st.button("💬 اشترك الآن", type="primary", key="feat_subscribe"):
        st.markdown("[اضغط هنا للاشتراك عبر واتساب](https://wa.me/212719082215?text=" + urllib.parse.quote("مرحباً، أرغب في الاشتراك في منصة Yonah Ashkenaz") + ")")


def show_landing():
    # عدّاد الوكلاء
    st.markdown(
        '<div style="text-align:center; margin: 20px 0; font-size:1.4rem; color:#00d4ff;">'
        '🎯 <strong>12 وكيلاً ذكياً</strong> · '
        '7 مدعومة بالذكاء الاصطناعي · '
        '3 لغات (عربي · فرنسي · إنجليزي)'
        '</div>',
        unsafe_allow_html=True
    )
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

    if st.button("🧾 جرّب Invoice", use_container_width=True, key="btn_invoice"):
        st.session_state.page = "invoice"
        st.rerun()

    if st.button("🇲🇦 جرّب Moroccan Admin", use_container_width=True, key="btn_moroccan"):
        st.session_state.page = "moroccan_admin"
        st.rerun()

    if st.button("📞 جرّب Customer Support", use_container_width=True, key="btn_customer_support"):
        st.session_state.page = "customer_support"
        st.rerun()

    if st.button("✍️ جرّب Content Writer", use_container_width=True, key="btn_content_writer"):
        st.session_state.page = "content_writer"
        st.rerun()

    if st.button("📧 جرّب Email Agent", use_container_width=True, key="btn_email_agent"):
        st.session_state.page = "email_agent"
        st.rerun()

    if st.button("📱 جرّب Social Media", use_container_width=True, key="btn_social_media"):
        st.session_state.page = "social_media"
        st.rerun()

    if st.button("📝 جرّب Meeting Notes", use_container_width=True, key="btn_meeting_notes"):
        st.session_state.page = "meeting_notes"
        st.rerun()

    if st.button("✨ الميزات الكاملة", use_container_width=True, key="btn_features"):
        st.session_state.page = "features"
        st.rerun()

    if st.button("🚚 جرّب Supplier", use_container_width=True, key="btn_supplier"):
        st.session_state.page = "supplier"
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
        <a href="https://wa.me/212719082215?text=%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D9%8B%D8%8C%20%D8%A3%D8%B1%D8%BA%D8%A8%20%D9%81%D9%8A%20%D8%A7%D9%84%D8%A7%D8%B4%D8%AA%D8%B1%D8%A7%D9%83%20%D9%81%D9%8A%20%D8%AD%D8%B2%D9%85%D8%A9%20Starter%20%28500%20%D8%AF%D8%B1%D9%87%D9%85/%D8%B4%D9%87%D8%B1%29." target="_blank" style="display:block; text-align:center; margin-top:15px; background:linear-gradient(90deg,#00d4ff,#00ff88); color:#0f1428; padding:12px; border-radius:10px; text-decoration:none; font-weight:bold;">💬 اشترك الآن</a>
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
        <a href="https://wa.me/212719082215?text=%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D9%8B%D8%8C%20%D8%A3%D8%B1%D8%BA%D8%A8%20%D9%81%D9%8A%20%D8%A7%D9%84%D8%A7%D8%B4%D8%AA%D8%B1%D8%A7%D9%83%20%D9%81%D9%8A%20%D8%AD%D8%B2%D9%85%D8%A9%20Pro%20%281200%20%D8%AF%D8%B1%D9%87%D9%85/%D8%B4%D9%87%D8%B1%29." target="_blank" style="display:block; text-align:center; margin-top:15px; background:linear-gradient(90deg,#00d4ff,#00ff88); color:#0f1428; padding:12px; border-radius:10px; text-decoration:none; font-weight:bold;">💬 اشترك الآن</a>
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
        <a href="https://wa.me/212719082215?text=%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D9%8B%D8%8C%20%D8%A3%D8%B1%D8%BA%D8%A8%20%D9%81%D9%8A%20%D8%A7%D9%84%D8%A7%D8%B4%D8%AA%D8%B1%D8%A7%D9%83%20%D9%81%D9%8A%20%D8%AD%D8%B2%D9%85%D8%A9%20Business%20%282500%20%D8%AF%D8%B1%D9%87%D9%85/%D8%B4%D9%87%D8%B1%29." target="_blank" style="display:block; text-align:center; margin-top:15px; background:linear-gradient(90deg,#00d4ff,#00ff88); color:#0f1428; padding:12px; border-radius:10px; text-decoration:none; font-weight:bold;">💬 اشترك الآن</a>
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
def show_invoice():
    lang = st.selectbox("Choix", ["fr", "ar", "en"], key="inv_lang_main")
    st.session_state.lang = lang

    # زر تحميل النموذج التجريبي
    demo_path = os.path.join(os.path.dirname(__file__), "demo_invoice.xlsx")
    if os.path.exists(demo_path):
        with open(demo_path, "rb") as f:
            demo_bytes = f.read()
        st.download_button(
            "⬇️ تحميل نموذج Excel",
            data=demo_bytes,
            file_name="demo_invoice.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="inv_demo_dl",
        )
    st.markdown('<div class="main-header">🧾 Yonah Invoice</div>', unsafe_allow_html=True)
    if st.button("⬅️ رجوع", key="inv_back"):
        st.session_state.page = "landing"
        st.rerun()
    st.markdown("### 📝 بيانات الفاتورة")
    client_name = st.text_input("اسم العميل *", key="inv_client")
    client_address = st.text_input("عنوان العميل", key="inv_addr")
    n_items = st.number_input("عدد البنود", min_value=1, max_value=20, value=1, step=1, key="inv_n")
    items = []
    for i in range(int(n_items)):
        st.markdown(f"**البند {i+1}**")
        desc = st.text_input("الوصف", key=f"inv_desc_{i}")
        qty = st.number_input("الكمية", min_value=0.01, value=1.0, step=1.0, key=f"inv_qty_{i}")
        price = st.number_input("السعر (درهم)", min_value=0.0, value=100.0, step=10.0, key=f"inv_price_{i}")
        items.append({"description": desc or f"بند {i+1}", "quantity": qty, "unit_price": price})
    if st.button("🔨 إنشاء الفاتورة", type="primary", key="inv_create"):
        if not client_name.strip():
            st.error("⚠️ اسم العميل مطلوب")
        else:
            try:
                agent = InvoiceAgent()
                inv = agent.create_invoice(client_name=client_name, client_address=client_address or "-", items=items, tax_rate=0.20)
                st.session_state["inv_dict"] = inv
                st.success(f"✅ تم إنشاء الفاتورة {inv['number']}")
            except Exception as e:
                st.error(f"خطأ: {e}")
    if "inv_dict" in st.session_state:
        inv = st.session_state["inv_dict"]
        st.divider()
        st.markdown("### 👁️ معاينة الفاتورة")
        st.markdown(f"**رقم الفاتورة:** {inv['number']} | **التاريخ:** {inv['date']}")
        st.markdown(f"**العميل:** {inv['client_name']}")
        items_display = [{"الوصف": it["description"], "الكمية": it["quantity"], "السعر": f"{it['unit_price']:.2f}", "المجموع": f"{it['quantity'] * it['unit_price']:.2f}"} for it in inv["items"]]
        st.dataframe(items_display, use_container_width=True, hide_index=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("المجموع HT", f"{inv['subtotal']:.2f} DH")
        c2.metric(f"TVA {int(inv['tax_rate'] * 100)}%", f"{inv['tax']:.2f} DH")
        c3.metric("المجموع TTC", f"{inv['total']:.2f} DH")
        if st.button("📄 توليد PDF", type="primary", key="inv_pdf"):
            try:
                with st.spinner("جاري التوليد..."):
                    agent = InvoiceAgent()
                    pdf_path = agent.generate_pdf(inv, lang=lang)
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.session_state["inv_pdf_bytes"] = pdf_bytes
                    st.session_state["inv_pdf_name"] = pdf_path
                    st.success("✅ تم توليد الفاتورة")
                else:
                    st.error(f"❌ لم يُنشأ الملف: {pdf_path}")
            except Exception as e:
                st.error(f"خطأ: {e}")
        if st.session_state.get("inv_pdf_bytes"):
            st.download_button("⬇️ تحميل PDF", data=st.session_state["inv_pdf_bytes"], file_name=os.path.basename(st.session_state["inv_pdf_name"]), mime="application/pdf", use_container_width=True, key="inv_dl")
        if st.button("🗑️ مسح", key="inv_clear"):
            for k in ["inv_dict", "inv_pdf_bytes", "inv_pdf_name"]:
                st.session_state.pop(k, None)
            st.rerun()


# Router
# ============================================================
def show_moroccan_admin():
    st.markdown('<div class="main-header">🇲🇦 Moroccan Admin</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">TVA · IS · IR · CNSS · Payroll</div>', unsafe_allow_html=True)
    if st.button("⬅️ رجوع", key="ma_back"):
        st.session_state.page = "landing"
        st.rerun()

    admin = MoroccanAdmin()
    tab1, tab2, tab3, tab4 = st.tabs(["📊 TVA", "💰 IS", "👥 Payroll", "📅 التقويم"])

    with tab1:
        st.markdown("### حساب TVA")
        c1, c2 = st.columns(2)
        with c1:
            sales = st.number_input("المبيعات HT (DH)", min_value=0.0, value=100000.0, step=1000.0, key="ma_sales")
        with c2:
            purchases = st.number_input("المشتريات HT (DH)", min_value=0.0, value=40000.0, step=1000.0, key="ma_purch")
        rate = st.selectbox("المعدل", ["standard", "reduced1", "reduced2", "reduced3", "exempt"],
                            format_func=lambda x: {"standard":"20%","reduced1":"14%","reduced2":"10%","reduced3":"7%","exempt":"معفى"}[x],
                            key="ma_rate")
        if st.button("احسب TVA", type="primary", key="ma_calc_tva"):
            r = admin.calculate_tva(sales, purchases, rate)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("TVA محصلة", f"{r['tva_collected']:,.2f} DH")
            c2.metric("TVA قابلة للخصم", f"{r['tva_deductible']:,.2f} DH")
            c3.metric("TVA المستحقة", f"{r['tva_due']:,.2f} DH")
            c4.metric("الحالة", r["status"])

    with tab2:
        st.markdown("### حساب IS (ضريبة الشركات)")
        c1, c2 = st.columns(2)
        with c1:
            revenue = st.number_input("الإيرادات السنوية (DH)", min_value=0.0, value=500000.0, step=10000.0, key="ma_rev")
        with c2:
            expenses = st.number_input("المصاريف السنوية (DH)", min_value=0.0, value=300000.0, step=10000.0, key="ma_exp")
        if st.button("احسب IS", type="primary", key="ma_calc_is"):
            r = admin.calculate_is(revenue, expenses)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("الربح", f"{r['profit']:,.2f} DH")
            c2.metric("IS", f"{r['is_due']:,.2f} DH")
            c3.metric("المعدل الفعال", f"{r['effective_rate']}%")
            c4.metric("الحالة", r["status"])

    with tab3:
        st.markdown("### حساب Payroll (كشف الراتب)")
        salary = st.number_input("الأجر الخام الشهري (DH)", min_value=0.0, value=8000.0, step=500.0, key="ma_sal")
        if st.button("احسب Payroll", type="primary", key="ma_calc_pay"):
            r = admin.calculate_payroll(salary)
            st.markdown("**خصومات الموظف:**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("CNSS", f"{r['cnss_employee']} DH")
            c2.metric("AMO", f"{r['amo_employee']} DH")
            c3.metric("IR", f"{r['ir_monthly']} DH")
            c4.metric("✅ الصافي", f"{r['net_salary']:,.2f} DH")
            st.markdown("**على صاحب العمل:**")
            c1, c2 = st.columns(2)
            c1.metric("CNSS صاحب العمل", f"{r['cnss_employer']} DH")
            c2.metric("💰 التكلفة الكلية", f"{r['total_cost_employer']:,.2f} DH")

    with tab4:
        st.markdown("### 📅 التقويم الضريبي")
        days = st.slider("الأيام القادمة", 7, 90, 30, key="ma_days")
        deadlines = admin.get_upcoming_deadlines(days)
        if deadlines:
            for d in deadlines:
                st.markdown(f"{d['urgency']} **{d['date']}** — {d['obligation']} *({d['days_left']} يوم)*")
        else:
            st.info(f"لا مواعيد خلال {days} يوماً")


def show_customer_support():
    st.markdown('<div class="main-header">📞 Customer Support</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">تصنيف التذاكر · ردود ذكية · إجراءات مقترحة</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="cs_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = CustomerSupportAgent()

    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox("اللغة", ["ar", "fr", "en"], key="cs_lang")
    with c2:
        tone = st.selectbox("النبرة", ["formal", "friendly", "apologetic"],
                            format_func=lambda x: {"formal":"رسمي","friendly":"ودي","apologetic":"اعتذاري"}[x],
                            key="cs_tone")
    with c3:
        client_name = st.text_input("اسم العميل (اختياري)", key="cs_name")

    text = st.text_area("نص تذكرة العميل", height=150, key="cs_text",
                        placeholder="الصق هنا رسالة العميل...")

    if st.button("🔍 تحليل وتوليد رد", type="primary", key="cs_analyze"):
        if not text.strip():
            st.error("⚠️ اكتب نص التذكرة أولاً")
        else:
            result = agent.classify_ticket(text, lang=lang)
            result["client_name"] = client_name

            st.divider()
            st.markdown("### 📊 التصنيف")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("النوع", f"{result['type_icon']} {result['type_label']}")
            c2.metric("الأولوية", f"{result['priority_icon']} {result['priority_label']}")
            c3.metric("المشاعر", f"{result['sentiment_emoji']} {result['sentiment_label']}")
            c4.metric("التصعيد", "⚠️ نعم" if result['needs_escalation'] else "✅ لا")
            if result['needs_escalation']:
                st.warning(f"⚠️ يحتاج تصعيد: {result['escalation_reason']}")

            st.divider()
            st.markdown("### ✉️ الرد المقترح")
            with st.spinner("جاري توليد الرد..."):
                resp = agent.generate_response(result, tone=tone, lang=lang)
            st.info(f"المصدر: {resp['source']}")
            st.text_area("الرد", value=resp["text"], height=200, key="cs_response")
            st.download_button("⬇️ تحميل الرد", data=resp["text"],
                               file_name=f"response_{lang}.txt", mime="text/plain",
                               key="cs_dl")

            st.divider()
            st.markdown("### 🎯 الإجراءات المقترحة")
            for action in agent.suggest_actions(result, lang=lang):
                st.markdown(f"- {action}")

    with st.expander("📚 الأسئلة الشائعة"):
        faqs = agent.get_faq(lang=lang)
        for faq in faqs:
            st.markdown(f"**{faq['q']}**")
            st.caption(faq["a"])


def show_content_writer():
    st.markdown('<div class="main-header">✍️ Content Writer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">مقالات · وصف منتجات · سوشيال ميديا · إعلانات</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="cw_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = ContentWriterAgent()

    # الإعدادات
    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox("اللغة", ["ar", "fr", "en"], key="cw_lang")
    with c2:
        tone = st.selectbox("النبرة", list(agent.TONES.keys()),
                            format_func=lambda x: agent.TONES[x][lang],
                            key="cw_tone")
    with c3:
        length = st.selectbox("الطول", list(agent.LENGTHS.keys()),
                              format_func=lambda x: agent.LENGTHS[x][lang],
                              key="cw_length")

    c1, c2 = st.columns(2)
    with c1:
        content_type = st.selectbox("نوع المحتوى", list(agent.CONTENT_TYPES.keys()),
                                    format_func=lambda x: f"{agent.CONTENT_TYPES[x]['icon']} {agent.CONTENT_TYPES[x][lang]}",
                                    key="cw_type")
    with c2:
        topic = st.text_input("الموضوع *", key="cw_topic", placeholder="مثال: خدمات المحاسبة")

    c1, c2 = st.columns(2)
    with c1:
        audience = st.text_input("الجمهور المستهدف (اختياري)", key="cw_aud")
    with c2:
        keywords = st.text_input("كلمات مفتاحية (اختياري)", key="cw_kw")

    if st.button("✍️ توليد المحتوى", type="primary", key="cw_generate"):
        if not topic.strip():
            st.error("⚠️ اكتب الموضوع أولاً")
        else:
            with st.spinner("جاري التوليد..."):
                result = agent.generate(content_type, topic, tone, length, lang, audience, keywords)

            st.divider()
            st.info(f"المصدر: {result['source']} | النوع: {result['type_label']} | النبرة: {result['tone']}")

            st.text_area("المحتوى", value=result["content"], height=400, key="cw_output")

            # أزرار التحميل
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "⬇️ تحميل .txt",
                    data=result["content"],
                    file_name=f"content_{content_type}_{lang}.txt",
                    mime="text/plain",
                    key="cw_dl_txt"
                )
            with c2:
                # اقتراحات إضافية
                if content_type in ["social", "ad"]:
                    hashtags = agent.suggest_hashtags(topic, lang=lang)
                    st.download_button(
                        "⬇️ تحميل Hashtags",
                        data=" ".join(hashtags),
                        file_name=f"hashtags_{lang}.txt",
                        mime="text/plain",
                        key="cw_dl_tags"
                    )

            # Hashtags مقترحة
            if content_type in ["social", "ad"]:
                st.markdown("### 🔖 Hashtags مقترحة")
                hashtags = agent.suggest_hashtags(topic, lang=lang)
                st.code(" ".join(hashtags))

            # عناوين مقترحة
            if content_type in ["article", "email"]:
                st.markdown("### 📰 عناوين مقترحة")
                for t in agent.suggest_titles(topic, lang=lang):
                    st.markdown(f"- {t}")


def show_email_agent():
    st.markdown('<div class="main-header">📧 Email Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">ردود · حملات · متابعة · دعوات</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="em_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = EmailAgent()

    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox("اللغة", ["ar", "fr", "en"], key="em_lang")
    with c2:
        tone = st.selectbox("النبرة", list(agent.TONES.keys()),
                            format_func=lambda x: agent.TONES[x][lang],
                            key="em_tone")
    with c3:
        email_type = st.selectbox("نوع البريد", list(agent.EMAIL_TYPES.keys()),
                                  format_func=lambda x: f"{agent.EMAIL_TYPES[x]['icon']} {agent.EMAIL_TYPES[x][lang]}",
                                  key="em_type")

    subject = st.text_input("الموضوع *", key="em_subject", placeholder="مثال: عرض خاص للعملاء")

    c1, c2 = st.columns(2)
    with c1:
        recipient = st.text_input("المستقبل (اختياري)", key="em_recip")
    with c2:
        sender = st.text_input("المرسل (اختياري)", key="em_sender")

    context = st.text_area("السياق الإضافي (اختياري)", height=100, key="em_context",
                           placeholder="معلومات إضافية للرد عليها...")

    if st.button("📧 توليد البريد", type="primary", key="em_generate"):
        if not subject.strip():
            st.error("⚠️ اكتب الموضوع أولاً")
        else:
            with st.spinner("جاري التوليد..."):
                result = agent.generate(email_type, subject, context, tone, lang, recipient, sender)

            st.divider()
            st.info(f"المصدر: {result['source']} | النوع: {result['type_label']} | النبرة: {result['tone']}")
            st.text_area("البريد", value=result["content"], height=400, key="em_output")
            st.download_button(
                "⬇️ تحميل .txt",
                data=result["content"],
                file_name=f"email_{email_type}_{lang}.txt",
                mime="text/plain",
                key="em_dl"
            )

            st.divider()
            st.markdown("### 💡 عناوين مقترحة")
            for s in agent.suggest_subjects(subject, lang=lang):
                st.markdown(f"- {s}")


def show_social_media():
    st.markdown('<div class="main-header">📱 Social Media Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">منشورات جاهزة · 6 منصات · 3 لغات</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="sm_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = SocialMediaAgent()

    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox("اللغة", ["ar", "fr", "en"], key="sm_lang")
    with c2:
        platform = st.selectbox("المنصة", list(agent.PLATFORMS.keys()),
                                format_func=lambda x: f"{agent.PLATFORMS[x]['icon']} {agent.PLATFORMS[x][lang]}",
                                key="sm_platform")
    with c3:
        post_type = st.selectbox("نوع المنشور", list(agent.POST_TYPES.keys()),
                                 format_func=lambda x: f"{agent.POST_TYPES[x]['icon']} {agent.POST_TYPES[x][lang]}",
                                 key="sm_type")

    c1, c2 = st.columns(2)
    with c1:
        tone = st.selectbox("النبرة", list(agent.TONES.keys()),
                            format_func=lambda x: agent.TONES[x][lang],
                            key="sm_tone")
    with c2:
        audience = st.text_input("الجمهور (اختياري)", key="sm_aud")

    topic = st.text_input("الموضوع *", key="sm_topic", placeholder="مثال: نصائح إنتاجية")

    if st.button("📱 توليد المنشور", type="primary", key="sm_generate"):
        if not topic.strip():
            st.error("⚠️ اكتب الموضوع")
        else:
            with st.spinner("جاري التوليد..."):
                r = agent.generate_post(platform, post_type, topic, tone, lang, audience)

            st.divider()
            best = r['best_chars']
            status = "✅ ممتاز" if r['char_count'] <= best else "⚠️ طويل قليلاً"
            st.info(f"المصدر: {r['source']} | {r['platform_icon']} {r['platform_label']} | الأحرف: {r['char_count']}/{best} {status}")

            st.text_area("المنشور", value=r["content"], height=300, key="sm_output")
            st.download_button("⬇️ تحميل .txt", data=r["content"],
                               file_name=f"post_{platform}_{lang}.txt", mime="text/plain",
                               key="sm_dl")

            st.markdown("### 🔖 Hashtags مقترحة")
            st.code(" ".join(agent.suggest_hashtags(topic, platform, lang)))


def show_meeting_notes():
    st.markdown('<div class="main-header">📝 Meeting Notes</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">محاضر اجتماعات · مهام · قرارات</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="mn_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = MeetingNotesAgent()

    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox("اللغة", ["ar", "fr", "en"], key="mn_lang")
    with c2:
        mtype = st.selectbox("نوع الاجتماع", list(agent.MEETING_TYPES.keys()),
                             format_func=lambda x: f"{agent.MEETING_TYPES[x]['icon']} {agent.MEETING_TYPES[x][lang]}",
                             key="mn_type")
    with c3:
        date = st.text_input("التاريخ", value=datetime.now().strftime("%Y-%m-%d"), key="mn_date")

    title = st.text_input("عنوان الاجتماع", key="mn_title", placeholder="مثال: اجتماع شهري")
    transcript = st.text_area("نص الاجتماع *", height=250, key="mn_text",
                              placeholder="الصق هنا نص الحوار أو الملاحظات...")

    if st.button("📝 توليد المحضر", type="primary", key="mn_generate"):
        if not transcript.strip():
            st.error("⚠️ الصق نص الاجتماع")
        else:
            with st.spinner("جاري التوليد..."):
                r = agent.generate_minutes(transcript, mtype, lang, title, date)

            st.divider()
            st.info(f"المصدر: {r['source']} | النوع: {r['type_label']}")
            st.markdown(r["minutes"])
            st.download_button("⬇️ تحميل المحضر (.md)", data=r["minutes"],
                               file_name=f"meeting_{date}.md", mime="text/markdown",
                               key="mn_dl")


def show_supplier():
    st.markdown('<div class="main-header">🚚 Supplier Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">طلبات · تفاوض · مقارنة الموردين</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="sp_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = SupplierAgent()

    c1, c2 = st.columns(2)
    with c1:
        lang = st.selectbox("اللغة", ["ar", "fr", "en"], key="sp_lang")
    with c2:
        rtype = st.selectbox("نوع الرسالة", list(agent.REQUEST_TYPES.keys()),
                             format_func=lambda x: f"{agent.REQUEST_TYPES[x]['icon']} {agent.REQUEST_TYPES[x][lang]}",
                             key="sp_type")

    c1, c2 = st.columns(2)
    with c1:
        supplier = st.text_input("اسم المورد", key="sp_sup")
    with c2:
        sender = st.text_input("المرسل (شركتك)", key="sp_sender")

    context = st.text_area("السياق *", height=120, key="sp_ctx",
                           placeholder="مثال: توريد 100 وحدة، ميزانية محددة، شروط...")

    if st.button("🚚 توليد الرسالة", type="primary", key="sp_gen"):
        if not context.strip():
            st.error("⚠️ اكتب السياق")
        else:
            with st.spinner("جاري التوليد..."):
                r = agent.generate_request(rtype, supplier, context, lang, sender)
            st.divider()
            st.info(f"المصدر: {r['source']} | النوع: {r['type_label']}")
            st.text_area("الرسالة", value=r["content"], height=300, key="sp_out")
            st.download_button("⬇️ تحميل", data=r["content"],
                               file_name=f"supplier_{rtype}_{lang}.txt",
                               mime="text/plain", key="sp_dl")


if st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "features":
    show_features()
elif st.session_state.page == "landing":
    show_landing()
elif st.session_state.page == "accountant":
    show_accountant()
elif st.session_state.page == "agents":
    show_agents()
elif st.session_state.page == "hr":
    show_hr()
elif st.session_state.page == "cfo":
    show_cfo()
elif st.session_state.page == "invoice":
    show_invoice()
elif st.session_state.page == "moroccan_admin":
    show_moroccan_admin()
elif st.session_state.page == "customer_support":
    show_customer_support()
elif st.session_state.page == "content_writer":
    show_content_writer()
elif st.session_state.page == "email_agent":
    show_email_agent()
elif st.session_state.page == "social_media":
    show_social_media()
elif st.session_state.page == "meeting_notes":
    show_meeting_notes()
elif st.session_state.page == "supplier":
    show_supplier()
