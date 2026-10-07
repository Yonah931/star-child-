import streamlit as st
import os
import time as _time
from datetime import datetime
from accountant import AccountantAgent, generate_accounting_pdf
from translations import get_text
from translations_ui import t
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
try:
    from multiagent import show_agents_full
except Exception as _e:
    show_agents_full = None
import streamlit_authenticator as stauth
import admin_panel
import database
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

    # فحص القفل
    if st.session_state.get("login_locked_until") and st.session_state["login_locked_until"] > _time.time():
        _remaining = int((st.session_state["login_locked_until"] - _time.time()) / 60) + 1
        st.error(f"🔒 الحساب مقفل مؤقتاً ({_remaining} دقيقة).")
        st.stop()
    
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
        st.session_state["login_attempts"] = st.session_state.get("login_attempts", 0) + 1
        _attempts = st.session_state["login_attempts"]
        _max = 5
        if _attempts >= _max:
            st.session_state["login_locked_until"] = _time.time() + 15 * 60
            st.error(f"🔒 تم قفل الجلسة لمدة 15 دقيقة بعد {_max} محاولات فاشلة.")
        else:
            st.error(f"❌ اسم المستخدم أو كلمة السر خاطئة (المتبقي: {_max - _attempts} محاولات)")
        st.stop()
    elif st.session_state.get("authentication_status") is None:
        st.warning("🔒 يرجى تسجيل الدخول للمتابعة")
        st.stop()
    else:
        st.session_state["login_attempts"] = 0
        st.session_state["login_locked_until"] = None

    # قائمة اللغة العالمية
    _current_lang = st.session_state.get("lang", "ar")
    _lang_options = {"ar": "🇲🇦 العربية", "fr": "🇫🇷 Français", "en": "🇬🇧 English"}
    _selected_lang = st.selectbox(
        "🌍 Language",
        options=["ar", "fr", "en"],
        index=["ar", "fr", "en"].index(_current_lang),
        format_func=lambda x: _lang_options[x],
        key="global_lang_selector",
    )
    if _selected_lang != _current_lang:
        st.session_state["lang"] = _selected_lang
        st.rerun()

        # عرض شريط علوي مع اسم المستخدم وزر خروج
        _col1, _col2 = st.columns([4, 1])
        with _col1:
            st.caption(f"👋 مرحباً **{st.session_state.get('name', 'مستخدم')}**")
        with _col2:
            if st.button("📊 لوحتي", key="goto_dash"):
                st.session_state.page = "dashboard"
                st.rerun()
            if st.button("📁 فواتيري", key="goto_myinv"):
                st.session_state.page = "my_invoices"
                st.rerun()
        with _col2:
            if st.button("⚙️ الإعدادات", key="goto_settings"):
                st.session_state.page = "settings"
                st.rerun()
        _admin_roles = st.session_state.get("roles") or []
        if "admin" in _admin_roles:
            if st.button("📊 إحصائيات", key="goto_stats"):
                st.session_state.page = "stats"
                st.rerun()
            if st.button("👑 المدير", key="goto_admin"):
                st.session_state.page = "admin"
                st.rerun()
        with st.container():
            _authenticator.logout(location="main", key="main_logout")



st.markdown("""
<style>

/* ============================================
   Logo + Brand
   ============================================ */
.brand-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 10px 0 20px 0;
}
.brand-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #00d4ff 0%, #00ff88 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.25);
}
.brand-text {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.brand-tagline {
    text-align: center;
    color: #888;
    font-size: 0.95rem;
    margin-top: -10px;
    margin-bottom: 25px;
}
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


/* ============================================
   Modern Dark Theme v2
   ============================================ */

@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

.stApp {
    background: radial-gradient(ellipse at top, #0f1729 0%, #0a0e1a 50%, #050810 100%);
    font-family: 'Cairo', sans-serif;
}

.brand-text, .main-header {
    background: linear-gradient(135deg, #00d4ff, #00ff88) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 800;
}

.agents-count { color: #00d4ff !important; }

.feature-card, .price-card, .agent-card {
    backdrop-filter: blur(14px);
    background: linear-gradient(135deg, rgba(20, 27, 45, 0.85), rgba(15, 23, 41, 0.7)) !important;
    border: 1px solid rgba(0, 212, 255, 0.15) !important;
    border-top: 3px solid #00d4ff !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.3s ease;
}

.feature-card:hover, .price-card:hover, .agent-card:hover {
    border-color: rgba(0, 212, 255, 0.5) !important;
    box-shadow: 0 12px 40px rgba(0, 212, 255, 0.15) !important;
    transform: translateY(-3px);
}

h1, h2, h3, .feature-title, .agent-name { color: #00d4ff !important; }
.price-amount { color: #00ff88 !important; }

/* الأزرار — بتدرج بنفسجي → سماوي دائماً (نموذج جديد) */
.stButton > button {
    background: linear-gradient(90deg, #c026d3 0%, #7c3aed 40%, #06b6d4 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35),
                0 0 20px rgba(6, 182, 212, 0.15) !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.stButton > button:hover {
    background: linear-gradient(90deg, #d946ef 0%, #8b5cf6 40%, #22d3ee 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 24px rgba(124, 58, 237, 0.55),
                0 0 30px rgba(6, 182, 212, 0.35) !important;
    transform: translateY(-2px);
}

.stButton > button:focus,
.stButton > button:active {
    background: linear-gradient(90deg, #d946ef 0%, #8b5cf6 40%, #22d3ee 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 0 30px rgba(124, 58, 237, 0.7),
                0 0 15px rgba(6, 182, 212, 0.5) !important;
    outline: none !important;
    transform: translateY(-2px);
}

/* الأزرار primary — نفس التصميم لكن أقوى */
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #d946ef 0%, #8b5cf6 40%, #22d3ee 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.45),
                0 0 25px rgba(6, 182, 212, 0.25) !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.7),
                0 0 40px rgba(6, 182, 212, 0.5) !important;
}

/* روابط الأزرار — نفس التدرج */
.stLinkButton a {
    background: linear-gradient(90deg, #c026d3 0%, #7c3aed 40%, #06b6d4 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35) !important;
}

.stLinkButton a:hover {
    background: linear-gradient(90deg, #d946ef 0%, #8b5cf6 40%, #22d3ee 100%) !important;
    box-shadow: 0 6px 24px rgba(124, 58, 237, 0.55) !important;
    transform: translateY(-2px);
}

[data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #8892a8 !important; }

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent);
    margin: 20px 0;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1729 0%, #0a0e1a 100%);
    border-right: 1px solid rgba(0, 212, 255, 0.12);
}

.stAlert {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(124, 58, 237, 0.05)) !important;
    border-left: 4px solid #00d4ff !important;
    border-radius: 10px;
    color: #e8eef5 !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: rgba(20, 27, 45, 0.8) !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-radius: 10px !important;
    color: #e8eef5 !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > div:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.15) !important;
}

[data-testid="stDataFrame"] {
    background: rgba(20, 27, 45, 0.6);
    border-radius: 12px;
    border: 1px solid rgba(0, 212, 255, 0.15);
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #00d4ff, #7c3aed) !important;
}

a { color: #00d4ff !important; text-decoration: none; transition: all 0.2s; }
a:hover { color: #00ff88 !important; text-shadow: 0 0 10px rgba(0, 255, 136, 0.4); }

[data-baseweb="select"] > div {
    background-color: rgba(20, 27, 45, 0.8) !important;
    border-color: rgba(0, 212, 255, 0.2) !important;
}

[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: #ffffff !important;
}

[role="radiogroup"] label[data-checked="true"] { color: #00d4ff !important; }

.stCheckbox [data-baseweb="checkbox"] [aria-checked="true"] {
    background: #00d4ff !important;
    border-color: #00d4ff !important;
}

.stSpinner > div > div { border-top-color: #00d4ff !important; }

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
    message = f"مرحباً، أرغب في الاشتراك في حزمة *{plan_name}* ({price} {t('per_month', _lang)}). هل يمكنكم مساعدتي؟"
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
        if st.button("🧾 فاتورة جديدة", width="stretch", key="dash_inv"):
            st.session_state.page = "invoice"
            st.rerun()
    with c2:
        if st.button("📞 دعم العملاء", width="stretch", key="dash_cs"):
            st.session_state.page = "customer_support"
            st.rerun()
    with c3:
        if st.button("✍️ محتوى جديد", width="stretch", key="dash_cw"):
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
    _feat_lang = st.session_state.get("lang", "ar")
    """صفحة الميزات التفصيلية"""
    st.markdown(f'<div class="main-header">{t("feat_title", _feat_lang)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">12 وكيلاً ذكياً لإدارة أعمالك</div>', unsafe_allow_html=True)

    if st.button(t("back_short", _feat_lang), key="feat_back"):
        st.session_state.page = "landing"
        st.rerun()

    st.divider()
    st.markdown(f"### 🤖 {t('feat_finance', _feat_lang)}")

    features = [
        ("📊 المحاسب الذكي", "يقرأ Excel/CSV، يكشف الأخطاء، يولّد تقارير PDF بـ 3 لغات", "AI"),
        ("💰 المدير المالي (CFO)", "تحليل الربحية، حساب TVA/IS/CNSS، توصيات ذكية", "AI"),
        ("🇲🇦 Moroccan Admin", "TVA، IS، IR، CNSS، Payroll، تقويم ضريبي مغربي", "AI"),
        ("🧾 وكيل الفواتير", "فواتير احترافية مع ICE، TVA تلقائي، PDF بـ 3 لغات", "AI"),
    ]

    for name, desc, badge in features:
        with st.expander(f"{name}"):
            st.markdown(f"{t("feat_desc", _feat_lang)}: {desc}")
            st.markdown(f"{t("feat_tech", _feat_lang)}: {badge}")

    st.divider()
    st.markdown(f"### 📢 {t('feat_marketing', _feat_lang)}")

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
    st.markdown(f"### 👥 {t('feat_admin', _feat_lang)}")

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
    st.markdown(f"### {t('feat_extra', _feat_lang)}")
    st.markdown("""
    - 🌍 **3 لغات:** عربي، فرنسي، إنجليزي
    - 📄 **تقارير PDF** احترافية
    - 🔒 **تسجيل دخول آمن**
    - ⚡ **سريع** (نتائج في ثوانٍ)
    - ☁️ **سحابي** (يعمل من أي جهاز)
    - 💬 **دعم واتساب مباشر**
    """)

    st.divider()
    if st.button("💬 {t('subscribe_now', _lang)}", type="primary", key="feat_subscribe"):
        st.markdown("[اضغط هنا للاشتراك عبر واتساب](https://wa.me/212719082215?text=" + urllib.parse.quote("مرحباً، أرغب في الاشتراك في منصة Yonah Ashkenaz") + ")")


def show_admin():
    """لوحة تحكم المدير — إدارة المستخدمين"""
    # حماية: admin فقط
    roles = st.session_state.get("roles") or []
    if "admin" not in roles:
        st.error("⛔ هذه الصفحة للمدير فقط")
        if st.button("⬅️ رجوع", key="admin_unauth_back"):
            st.session_state.page = "landing"
            st.rerun()
        return

    st.markdown('<div class="main-header">⚙️ لوحة المدير</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">إدارة المستخدمين والاشتراكات</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="admin_back"):
        st.session_state.page = "landing"
        st.rerun()

    # إحصائيات
    s = admin_panel.stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 المجموع", s["total"])
    c2.metric("👑 مدراء", s["admins"])
    c3.metric("👤 عاديون", s["regular"])
    c4.metric("🕐 آخر تحديث", s["updated"].split()[1])

    st.divider()

    # عرض المستخدمين
    st.markdown("### 👥 المستخدمون")
    users = admin_panel.list_users()
    if users:
        import pandas as _pd
        df = _pd.DataFrame(users)
        df.columns = ["اسم المستخدم", "البريد", "الاسم", "الأدوار"]
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("لا يوجد مستخدمون")

    st.divider()

    # إضافة مستخدم
    st.markdown("### ➕ إضافة مستخدم جديد")
    with st.form("add_user_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_username = st.text_input("اسم المستخدم *")
            new_email = st.text_input("البريد الإلكتروني *")
            new_first = st.text_input("الاسم الأول")
        with c2:
            new_last = st.text_input("الاسم الأخير")
            new_password = st.text_input("كلمة السر *", type="password")
            new_role = st.selectbox("الدور", ["user", "admin"])

        submitted = st.form_submit_button("➕ إضافة", type="primary")
        if submitted:
            if not new_username or not new_password:
                st.error("⚠️ اسم المستخدم وكلمة السر مطلوبان")
            else:
                ok, msg = admin_panel.add_user(
                    new_username, new_email, new_first, new_last, new_password, new_role
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    st.divider()

    # حذف مستخدم
    st.markdown("### 🗑️ حذف مستخدم")
    usernames = [u["username"] for u in users]
    if usernames:
        target = st.selectbox("اختر مستخدماً", usernames, key="admin_del_target")
        if st.button(f"🗑️ حذف {target}", key="admin_del_btn"):
            if target == st.session_state.get("username"):
                st.error("⛔ لا يمكنك حذف حسابك الحالي")
            else:
                ok, msg = admin_panel.delete_user(target)
                if ok:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    st.divider()

    # تغيير كلمة السر
    st.markdown("### 🔑 تغيير كلمة السر")
    if usernames:
        target_pwd = st.selectbox("اختر مستخدماً", usernames, key="admin_pwd_target")
        new_pwd = st.text_input("كلمة السر الجديدة", type="password", key="admin_new_pwd")
        if st.button("🔑 تغيير كلمة السر", key="admin_change_pwd"):
            if len(new_pwd) < 6:
                st.error("⚠️ كلمة السر يجب أن تكون 6 أحرف على الأقل")
            else:
                ok, msg = admin_panel.change_password(target_pwd, new_pwd)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")


def show_settings():
    """إعدادات المستخدم"""
    st.markdown('<div class="main-header">⚙️ الإعدادات</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">إدارة حسابك وتفضيلاتك</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="settings_back"):
        st.session_state.page = "landing"
        st.rerun()

    username = st.session_state.get("username", "")
    name = st.session_state.get("name", "")
    roles = st.session_state.get("roles") or []

    # القسم 1: معلومات الحساب
    st.markdown("### 👤 معلومات الحساب")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("اسم المستخدم", value=username, disabled=True, key="set_username")
        st.text_input("الاسم الكامل", value=name, disabled=True, key="set_name")
    with c2:
        st.text_input("الأدوار", value=", ".join(roles), disabled=True, key="set_roles")
        st.text_input(t("ma_status", _ma_lang), value="✅ نشط", disabled=True, key="set_status")

    st.divider()

    # القسم 2: تغيير كلمة السر
    st.markdown("### 🔑 تغيير كلمة السر")
    with st.form("change_pwd_form"):
        current_pwd = st.text_input("كلمة السر الحالية", type="password")
        new_pwd = st.text_input("كلمة السر الجديدة", type="password")
        confirm_pwd = st.text_input("تأكيد كلمة السر الجديدة", type="password")

        submitted = st.form_submit_button("💾 تحديث كلمة السر", type="primary")
        if submitted:
            if not current_pwd or not new_pwd or not confirm_pwd:
                st.error("⚠️ جميع الحقول مطلوبة")
            elif new_pwd != confirm_pwd:
                st.error("⚠️ كلمتا السر غير متطابقتين")
            elif len(new_pwd) < 6:
                st.error("⚠️ كلمة السر يجب أن تكون 6 أحرف على الأقل")
            else:
                ok, msg = admin_panel.change_password(username, new_pwd)
                if ok:
                    st.success(f"✅ {msg} (ستحتاج لإعادة تسجيل الدخول)")
                else:
                    st.error(f"❌ {msg}")

    st.divider()

    # القسم 3: تفضيلات اللغة
    st.markdown("### 🌍 تفضيلات اللغة")
    current_lang = st.session_state.get("lang", "ar")
    lang = st.selectbox(
        "اللغة الافتراضية",
        ["ar", "fr", "en"],
        index=["ar", "fr", "en"].index(current_lang),
        format_func=lambda x: {"ar": "العربية", "fr": "Français", "en": "English"}[x],
        key="set_lang",
    )
    if st.button("💾 حفظ التفضيلات", key="save_settings"):
        st.session_state["lang"] = lang
        st.success(f"✅ تم حفظ اللغة: {lang}")

    st.divider()

    # القسم 4: معلومات الاشتراك
    st.markdown("### 💎 الاشتراك")
    plan = "Business" if "admin" in roles else "Starter"
    c1, c2, c3 = st.columns(3)
    c1.metric("الحزمة الحالية", plan)
    c2.metric("الوكلاء المتاحون", "12")
    c3.metric("الاستخدام", "غير محدود")

    if st.button("💬 ترقية الاشتراك", key="upgrade"):
        st.markdown("[اضغط للتواصل عبر واتساب](https://wa.me/212719082215)")

    st.divider()

    # القسم 5: الحساب الخطير
    st.markdown("### ⚠️ منطقة الخطر")
    st.caption("حذف الحساب لا يمكن التراجع عنه.")
    if st.button("🗑️ حذف حسابي", key="delete_me"):
        st.warning("⚠️ للتواصل مع الإدارة لحذف الحساب: ashkenazyonah@gmail.com")


def show_about():
    _about_lang = st.session_state.get("lang", "ar")
    """صفحة من نحن"""
    st.markdown(f'<div class="main-header">{t("about_title", _about_lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{t("about_subtitle", _about_lang)}</div>', unsafe_allow_html=True)

    if st.button(t("back_short", _about_lang), key="about_back"):
        st.session_state.page = "landing"
        st.rerun()

    st.divider()

    # القصة
    st.markdown("""
    ### 🎯 رؤيتنا
    
    نبني **أدوات ذكية مخصصة للسوق المغربي** — بلغات ثلاثة، بأسعار في متناول الجميع، 
    وبفهم عميق لاحتياجات المقاولات الصغيرة والمتوسطة.
    
    ### 💡 لماذا؟
    
    لاحظنا أن معظم أدوات الذكاء الاصطناعي:
    - 🚫 صُمّمت للسوق الأمريكي/الأوروبي
    - 🚫 باهظة الثمن بالدولار
    - 🚫 لا تفهم TVA/IS/CNSS المغربية
    - 🚫 لا تدعم العربية بشكل احترافي
    
    **قررنا أن نبني البديل المغربي.**
    
    ### 🚀 ما الذي يميزنا؟
    
    - 🇲🇦 **مصمّمة للمغرب:** TVA, IS, IR, CNSS, ICE, OMPIC
    - 🌍 **3 لغات:** عربي، فرنسي، إنجليزي
    - 🤖 **12 وكيلاً ذكياً:** محاسبة، HR، CFO، تسويق، دعم
    - 💰 **أسعار بالدرهم:** تبدأ من 500 {t('per_month', _lang)}
    - ⚡ **سريعة:** نتائج في ثوانٍ
    - 🔒 **آمنة:** تسجيل دخول + حماية متقدمة
    """)

    st.divider()

    # الإحصائيات
    st.markdown(t("about_numbers", _about_lang))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🤖 الوكلاء", "12")
    c2.metric("🌍 اللغات", "3")
    c3.metric("⚡ الذكاء الاصطناعي", "7 وكلاء")
    c4.metric("🇲🇦 مصمّم في", "المغرب")

    st.divider()

    # المؤسس
    st.markdown("""
    ### 👤 المؤسس
    
    **Yonah Ashkenaz**  
    مهندس أنظمة ذكاء اصطناعي — Casablanca, Maroc
    
    شغوف ببناء أدوات تسهّل على المقاولين والمحاسبين المغاربة يومهم.
    
    📧 ashkenazyonah@gmail.com  
    💬 +212719082215
    """)

    st.divider()

    # تواصل
    st.markdown(t("about_contact", _about_lang))
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **البريد الإلكتروني:**  
        📧 ashkenazyonah@gmail.com
        """)
    with c2:
        st.markdown("""
        **واتساب:**  
        💬 +212719082215
        """)

    st.divider()
    st.caption(t("about_copyright", _about_lang))


def show_my_invoices():
    """صفحة فواتيري"""
    st.markdown('<div class="main-header">📁 فواتيري</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">سجل الفواتير المُنشأة</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="myinv_back"):
        st.session_state.page = "landing"
        st.rerun()

    username = st.session_state.get("username", "")
    rows = database.get_invoices(username=username, limit=100)
    stats = database.get_invoices_stats(username=username)

    # إحصائيات
    c1, c2, c3 = st.columns(3)
    c1.metric("📄 عدد الفواتير", stats["count"])
    c2.metric("💰 الإجمالي", f"{stats['total']:,.2f} DH")
    avg = stats["total"] / stats["count"] if stats["count"] > 0 else 0
    c3.metric("📊 المتوسط", f"{avg:,.2f} DH")

    st.divider()

    if not rows:
        st.info("📭 لا توجد فواتير بعد. اذهب إلى وكيل الفواتير وأنشئ واحدة.")
        if st.button("🧾 إنشاء فاتورة", type="primary", key="myinv_create"):
            st.session_state.page = "invoice"
            st.rerun()
        return

    # جدول الفواتير
    st.markdown("### 📋 الفواتير الأخيرة")
    import pandas as _pd
    df = _pd.DataFrame(rows, columns=[t("mn_date", _mn_lang), "رقم الفاتورة", "العميل", "الإجمالي", "TVA", t("hr_language", _hr_lang)])
    df["الإجمالي"] = df["الإجمالي"].apply(lambda x: f"{x:,.2f} DH")
    df["TVA"] = df["TVA"].apply(lambda x: f"{int(x * 100)}%")
    st.dataframe(df, width="stretch", hide_index=True)

    st.divider()

    # تحميل فاتورة بالرقم
    st.markdown("### ⬇️ تحميل فاتورة")
    numbers = [row[1] for row in rows]
    selected = st.selectbox("اختر رقم الفاتورة", numbers, key="myinv_select")
    if st.button("📥 عرض التفاصيل", key="myinv_view"):
        inv = database.get_invoice_by_number(selected)
        if inv:
            st.json(inv)
        else:
            st.error("❌ الفاتورة غير موجودة")


def show_stats():
    """لوحة الإحصائيات — للمدير فقط"""
    roles = st.session_state.get("roles") or []
    if "admin" not in roles:
        st.error("⛔ هذه الصفحة للمدير فقط")
        if st.button("⬅️ رجوع", key="stats_unauth"):
            st.session_state.page = "landing"
            st.rerun()
        return

    st.markdown('<div class="main-header">📊 الإحصائيات</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">نظرة شاملة على نشاط المنصة</div>', unsafe_allow_html=True)

    if st.button("⬅️ رجوع", key="stats_back"):
        st.session_state.page = "landing"
        st.rerun()

    stats = database.get_full_stats()

    st.divider()

    # الإحصائيات الرئيسية
    st.markdown("### 🎯 الأرقام الرئيسية")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 الفواتير", stats["invoices_count"])
    c2.metric("💰 إجمالي TTC", f"{stats['invoices_total']:,.2f} DH")
    c3.metric("💵 إجمالي HT", f"{stats['invoices_subtotal']:,.2f} DH")
    c4.metric("📝 المهمات", stats["tasks_count"])

    st.divider()

    # أعلى الوكلاء
    st.markdown("### 🏆 الوكلاء الأكثر استخداماً")
    if stats["top_agents"]:
        for i, (agent, count) in enumerate(stats["top_agents"], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "▫️"
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"{medal} **{agent}**")
            c2.markdown(f"**{count}** استخدام")
    else:
        st.info("📭 لا توجد مهمات مسجّلة بعد")

    st.divider()

    # آخر الفواتير
    st.markdown("### 🕐 آخر الفواتير")
    if stats["recent_invoices"]:
        import pandas as _pd
        df = _pd.DataFrame(
            stats["recent_invoices"],
            columns=[t("mn_date", _mn_lang), "رقم الفاتورة", "العميل", "الإجمالي (DH)"]
        )
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("📭 لا توجد فواتير")

    st.divider()

    # نشاط المستخدمين
    st.markdown("### 👥 نشاط المستخدمين")
    activity = database.get_user_activity()
    if activity:
        for username, count in activity:
            st.markdown(f"- **{username}**: {count} فاتورة")
    else:
        st.info("📭 لا يوجد نشاط مسجّل")

    st.divider()
    st.caption("📊 يتم التحديث تلقائياً عند كل زيارة")




def show_contact():
    """صفحة تواصل معنا"""
    st.markdown('<div class="main-header">Contact / تواصل معنا</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">For questions, demos, and custom requests</div>', unsafe_allow_html=True)

    if st.button("Back / رجوع", key="contact_back"):
        st.session_state.page = "landing"
        st.rerun()

    st.divider()

    col_info, col_form = st.columns([1, 1.5])

    with col_info:
        st.markdown("### Direct Contact / تواصل مباشر")
        st.markdown("""
        - **Email:** ashkenazyonah@gmail.com
        - **WhatsApp:** +212719082215
        - **Country:** Morocco
        """)
        st.markdown("---")
        st.markdown("### Response Time / سرعة الرد")
        st.markdown("""
        - Within 24 hours
        - خــلال 24 ســاعة
        """)

    with col_form:
        st.markdown("### Send a Message / أرسل رسالة")

        with st.form("contact_form", clear_on_submit=True):
            name = st.text_input("Name / الاسم", key="ct_name")
            email = st.text_input("Email / البريد", key="ct_email")
            phone = st.text_input("Phone / الهاتف (optional)", key="ct_phone")
            message = st.text_area("Message / الرسالة", height=140, key="ct_msg")

            submitted = st.form_submit_button("Send / إرسال", type="primary")

            if submitted:
                if not name.strip() or not message.strip():
                    st.error("Name and message are required / الاسم والرسالة مطلوبان")
                else:
                    try:
                        database.save_message(name, email, phone, message)
                        st.success("Message sent. We will reply soon.")
                        st.info("Sent / تم الإرسال")
                    except Exception as e:
                        st.error("Error: " + str(e)[:100])


def show_landing():
    _lang = st.session_state.get("lang", "ar")
    # الشعار
    st.markdown(f"""
    <div class="brand-logo">
        <div class="brand-icon">🤖</div>
        <div class="brand-text">Yonah Ashkenaz</div>
    </div>
    <div class="brand-tagline">{t('brand_tagline', _lang)}</div>
    """, unsafe_allow_html=True)

    # عدّاد الوكلاء
    st.markdown(
        '<div style="text-align:center; margin: 20px 0; font-size:1.4rem; color:#00d4ff;">'
        '🎯 <strong>12 وكيلاً ذكياً</strong> · '
        '7 مدعومة بالذكاء الاصطناعي · '
        '3 لغات (عربي · فرنسي · إنجليزي)'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div style="text-align:center; padding:3rem 1rem;
        background:linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%);
        border-radius:20px; margin-bottom:2rem;">
        <div style="color:#a8b4c8; font-size:1.2rem; margin-top:1rem;">
            منصة الذكاء الاصطناعي لإدارة الأعمال
        </div>
    </div>
    """, unsafe_allow_html=True)

    # قائمة الوكلاء
    import json as _json
    from agents_ui import render_agents_panel
    with open("agents_data.json", "r", encoding="utf-8") as _f:
        _agents = _json.load(_f)
    render_agents_panel(_agents)

    # أزرار ثانوية
    st.markdown("---")
    _colA, _colB, _colC = st.columns(3)
    with _colA:
        if st.button(f"About / {t('about', _lang)}", width="stretch", key="btn_about2"):
            st.session_state.page = "about"
            st.rerun()
    with _colB:
        if st.button(f"Features / {t('features_short', _lang)}", width="stretch", key="btn_features2"):
            st.session_state.page = "features"
            st.rerun()
    with _colC:
        if st.button(f"Contact / {t('contact_us', _lang)}", width="stretch", key="btn_contact2"):
            st.session_state.page = "contact"
            st.rerun()


    st.markdown("---")
    st.markdown(f"## {t('see_pricing', _lang)}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="price-card">
            <h3>Starter</h3>
            <div class="price-amount">500 <span class="price-currency">{t('per_month', _lang)}</span></div>
            <p>✅ وكيل واحد من اختيارك</p>
            <p>✅ 20 مهمة شهرياً</p>
            <p>✅ دعم واتساب</p>
        <a href="https://wa.me/212719082215?text=%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D9%8B%D8%8C%20%D8%A3%D8%B1%D8%BA%D8%A8%20%D9%81%D9%8A%20%D8%A7%D9%84%D8%A7%D8%B4%D8%AA%D8%B1%D8%A7%D9%83%20%D9%81%D9%8A%20%D8%AD%D8%B2%D9%85%D8%A9%20Starter%20%28500%20%D8%AF%D8%B1%D9%87%D9%85/%D8%B4%D9%87%D8%B1%29." target="_blank" style="display:block; text-align:center; margin-top:15px; background:linear-gradient(90deg,#00d4ff,#00ff88); color:#0f1428; padding:12px; border-radius:10px; text-decoration:none; font-weight:bold;">💬 {t('subscribe_now', _lang)}</a>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="price-card featured">
            <h3>Pro 🔥</h3>
            <div class="price-amount">1,200 <span class="price-currency">{t('per_month', _lang)}</span></div>
            <p>✅ 3 وكلاء</p>
            <p>✅ 100 مهمة شهرياً</p>
            <p>✅ كل الميزات</p>
            <p>✅ دعم أولوية</p>
        <a href="https://wa.me/212719082215?text=%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D9%8B%D8%8C%20%D8%A3%D8%B1%D8%BA%D8%A8%20%D9%81%D9%8A%20%D8%A7%D9%84%D8%A7%D8%B4%D8%AA%D8%B1%D8%A7%D9%83%20%D9%81%D9%8A%20%D8%AD%D8%B2%D9%85%D8%A9%20Pro%20%281200%20%D8%AF%D8%B1%D9%87%D9%85/%D8%B4%D9%87%D8%B1%29." target="_blank" style="display:block; text-align:center; margin-top:15px; background:linear-gradient(90deg,#00d4ff,#00ff88); color:#0f1428; padding:12px; border-radius:10px; text-decoration:none; font-weight:bold;">💬 {t('subscribe_now', _lang)}</a>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="price-card">
            <h3>Business</h3>
            <div class="price-amount">2,500 <span class="price-currency">{t('per_month', _lang)}</span></div>
            <p>✅ كل الوكلاء (8)</p>
            <p>✅ غير محدود</p>
            <p>✅ تخصيص كامل</p>
            <p>✅ دعم 24/7</p>
        <a href="https://wa.me/212719082215?text=%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D9%8B%D8%8C%20%D8%A3%D8%B1%D8%BA%D8%A8%20%D9%81%D9%8A%20%D8%A7%D9%84%D8%A7%D8%B4%D8%AA%D8%B1%D8%A7%D9%83%20%D9%81%D9%8A%20%D8%AD%D8%B2%D9%85%D8%A9%20Business%20%282500%20%D8%AF%D8%B1%D9%87%D9%85/%D8%B4%D9%87%D8%B1%29." target="_blank" style="display:block; text-align:center; margin-top:15px; background:linear-gradient(90deg,#00d4ff,#00ff88); color:#0f1428; padding:12px; border-radius:10px; text-decoration:none; font-weight:bold;">💬 {t('subscribe_now', _lang)}</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center; padding:2rem;">
        <h2>📞 ابدأ اليوم</h2>
        <p>{t('free_trial_7days', _lang)}.</p>
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
    lang = st.session_state.get("lang", "ar")
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button(t("back_short", lang), key="back_acc"):
            st.session_state.page = "landing"
            st.rerun()

    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 📁 {get_text(lang, 'upload_file')}")
        uploaded = st.file_uploader(get_text(lang, "choose_file"), type=['xlsx','xls','csv'])

    st.markdown(f'<div class="main-header">{t("ac_title", lang)}</div>', unsafe_allow_html=True)
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
        width="stretch"
    )

    st.markdown("---")
    st.markdown("### 🎯 أو جرّب المحاسب الذكي")
    if st.button("📊 فتح المحاسب", key="go_acc_from_agents", width="stretch"):
        st.session_state.page = "accountant"
        st.rerun()


# ============================================================
# الصفحة 4: وكيل HR
# ============================================================
def show_hr():
    _hr_lang = st.session_state.get("lang", "ar")
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← الرئيسية", key="back_hr"):
            st.session_state.page = "landing"
            st.rerun()

    st.markdown(f'<div class="main-header">{t("hr_title", _hr_lang)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">فرز CV • إعلانات توظيف • أسئلة مقابلات</div>', unsafe_allow_html=True)

    # التبويبات
    tab1, tab2, tab3 = st.tabs(["🔍 فرز CV", "📢 إعلان توظيف", "❓ أسئلة المقابلة"])

    # === تبويب 1: فرز CV ===
    with tab1:
        st.markdown("### ارفع ملف السير الذاتية (Excel/CSV)")
        st.markdown("يجب أن يحتوي الملف على أعمدة: `Name`, `Email`, `Experience`, `Skills`")

        uploaded = st.file_uploader(t("hr_choose_file", _hr_lang), type=['xlsx', 'xls', 'csv'], key="hr_cv_upload")

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
                    skills_input = st.text_input(t("hr_required_skills", _hr_lang), "Python, Git, SQL")
                with col2:
                    min_exp = st.number_input(t("hr_min_exp", _hr_lang), 0, 20, 2)

                if st.button(t("hr_start_screening", _hr_lang), key="hr_screen_btn", width="stretch"):
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
                    st.markdown(t("hr_report_header", _hr_lang))

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(t("hr_pdf_ar", _hr_lang), key="hr_pdf_ar", width="stretch"):
                            with st.spinner(t("hr_generating", _hr_lang)):
                                pdf_path = generate_hr_report(candidates, stats, lang='ar')
                                with open(pdf_path, "rb") as f:
                                    st.session_state['hr_pdf_ar_bytes'] = f.read()
                                st.session_state['hr_pdf_ar_ready'] = True
                    with col_b:
                        if st.button("📥 Rapport PDF (Français)", key="hr_pdf_fr", width="stretch"):
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
                            width="stretch"
                        )
                    if st.session_state.get('hr_pdf_fr_ready'):
                        st.download_button(
                            "⬇️ Télécharger le rapport",
                            st.session_state['hr_pdf_fr_bytes'],
                            file_name=f"hr_report_fr_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            width="stretch"
                        )

    # === تبويب 2: إعلان توظيف ===
    with tab2:
        st.markdown(t("hr_job_header", _hr_lang))

        col1, col2 = st.columns(2)
        with col1:
            job_type = st.selectbox(t("hr_job_type", _hr_lang),
                options=["developer", "accountant", "sales", "marketing", "hr"],
                format_func=lambda x: {
                    "developer": "💻 مطور برمجيات",
                    "accountant": "📊 محاسب",
                    "sales": "💼 مندوب مبيعات",
                    "marketing": "📢 مسؤول تسويق",
                    "hr": "👥 مسؤول HR"
                }[x])
        with col2:
            company_name = st.text_input(t("hr_company_name", _hr_lang), "Yonah Tech")

        lang_job = st.selectbox(t("hr_language", _hr_lang), ["ar", "fr", "en"],
            format_func=lambda x: {"ar": "🇲🇦 العربية", "fr": "🇫🇷 Français", "en": "🇬🇧 English"}[x])

        if st.button("📢 توليد الإعلان", key="hr_job_btn", width="stretch"):
            hr = HRAgent()
            posting = hr.generate_job_posting(job_type, company_name, lang=lang_job)
            st.markdown("---")
            st.markdown("### 📄 الإعلان الجاهز")
            st.text_area("", posting, height=400)

    # === تبويب 3: أسئلة المقابلة ===
    with tab3:
        st.markdown(t("hr_questions_header", _hr_lang))

        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(t("hr_category", _hr_lang), ["general", "technical"],
                format_func=lambda x: {"general": "📋 عامة", "technical": "💼 تقنية"}[x])
        with col2:
            lang_q = st.selectbox("اللغة ", ["ar", "fr", "en"],
                format_func=lambda x: {"ar": "🇲🇦 العربية", "fr": "🇫🇷 Français", "en": "🇬🇧 English"}[x])

        if st.button(t("hr_generate_questions", _hr_lang), key="hr_q_btn", width="stretch"):
            hr = HRAgent()
            questions = hr.get_interview_questions(category, lang_q)
            st.markdown("---")
            for i, q in enumerate(questions, 1):
                st.markdown(f"**{i}.** {q}")


# ============================================================
# الصفحة 5: وكيل CFO
# ============================================================
def show_cfo():
    _cfo_lang = st.session_state.get("lang", "ar")
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← الرئيسية", key="back_cfo"):
            st.session_state.page = "landing"
            st.rerun()

    st.markdown(f'<div class="main-header">{t("cfo_title", _cfo_lang)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">تحليل الربحية • حساب الضرائب • التدفق النقدي • التوصيات</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### {t('cfo_upload', _cfo_lang)}")
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
    st.markdown(f"### {t('cfo_cashflow', _cfo_lang)}")

    f1, f2 = st.columns(2)
    f1.metric("Cash Flow", f"{summary['cash_flow']:,.2f}")
    f2.metric("معدل الاستهلاك الشهري", f"{summary['monthly_burn']:,.2f}")

    st.markdown("---")
    st.markdown(f"### {t('cfo_insights', _cfo_lang)}")

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
        if st.button(f"📥 {t('cfo_generate_report', _cfo_lang)}", key="cfo_pdf_ar", width="stretch"):
            with st.spinner(t("cfo_generating", _cfo_lang)):
                pdf_path = generate_cfo_report(cfo.summary, cfo.taxes, cfo.insights, lang='ar')
                with open(pdf_path, "rb") as f:
                    st.session_state['cfo_pdf_ar_bytes'] = f.read()
                st.session_state['cfo_pdf_ar_ready'] = True
    with col_b:
        if st.button("📥 Rapport PDF (Français)", key="cfo_pdf_fr", width="stretch"):
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
            width="stretch"
        )
    if st.session_state.get('cfo_pdf_fr_ready'):
        st.download_button(
            "⬇️ Télécharger le rapport",
            st.session_state['cfo_pdf_fr_bytes'],
            file_name=f"cfo_report_fr_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            width="stretch"
        )


# ============================================================
def show_invoice():
    _inv_lang = st.session_state.get("lang", "ar")
    lang = _inv_lang
    st.markdown('<div class="main-header">🧾 Yonah Invoice</div>', unsafe_allow_html=True)
    st.session_state.lang = lang

    # زر تحميل النموذج التجريبي
    demo_path = os.path.join(os.path.dirname(__file__), "demo_invoice.xlsx")
    if os.path.exists(demo_path):
        with open(demo_path, "rb") as f:
            demo_bytes = f.read()
        st.download_button(
            f"{t('inv_download_demo', _inv_lang)}",
            data=demo_bytes,
            file_name="demo_invoice.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="inv_demo_dl",
        )
    if st.button(t("back_short", _inv_lang), key="inv_back"):
        st.session_state.page = "landing"
        st.rerun()
    st.markdown(f"### {t('inv_data_header', _inv_lang)}")
    client_name = st.text_input(f"{t('inv_client_name', _inv_lang)}", key="inv_client")
    client_address = st.text_input(f"{t('inv_client_address', _inv_lang)}", key="inv_addr")
    n_items = st.number_input(f"{t('inv_items_count', _inv_lang)}", min_value=1, max_value=20, value=1, step=1, key="inv_n")
    items = []
    for i in range(int(n_items)):
        st.markdown(f"**{t('inv_item_n', _inv_lang)} {i+1}**")
        desc = st.text_input(f"{t('inv_desc', _inv_lang)}", key=f"inv_desc_{i}")
        qty = st.number_input(f"{t('inv_quantity', _inv_lang)}", min_value=0.01, value=1.0, step=1.0, key=f"inv_qty_{i}")
        price = st.number_input(f"{t('inv_price', _inv_lang)}", min_value=0.0, value=100.0, step=10.0, key=f"inv_price_{i}")
        items.append({"description": desc or f"بند {i+1}", "quantity": qty, "unit_price": price})
    if st.button(f"{t('inv_create_btn', _inv_lang)}", type="primary", key="inv_create"):
        if not client_name.strip():
            st.error(f"{t('inv_error_client', _inv_lang)}")
        else:
            try:
                agent = InvoiceAgent()
                inv = agent.create_invoice(client_name=client_name, client_address=client_address or "-", items=items, tax_rate=0.20)
                st.session_state["inv_dict"] = inv
                # حفظ في قاعدة البيانات
                try:
                    database.save_invoice(
                        inv,
                        username=st.session_state.get("username"),
                        lang=lang,
                    )
                except Exception:
                    pass
                st.success(f"✅ تم إنشاء الفاتورة {inv['number']}")
            except Exception as e:
                st.error(f"خطأ: {e}")
    if "inv_dict" in st.session_state:
        inv = st.session_state["inv_dict"]
        st.divider()
        st.markdown(f"### {t('inv_preview', _inv_lang)}")
        st.markdown(f"**رقم الفاتورة:** {inv['number']} | **التاريخ:** {inv['date']}")
        st.markdown(f"**العميل:** {inv['client_name']}")
        items_display = [{f"{t('inv_desc', _inv_lang)}": it["description"], f"{t('inv_quantity', _inv_lang)}": it["quantity"], "السعر": f"{it['unit_price']:.2f}", "المجموع": f"{it['quantity'] * it['unit_price']:.2f}"} for it in inv["items"]]
        st.dataframe(items_display, width="stretch", hide_index=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("المجموع HT", f"{inv['subtotal']:.2f} DH")
        c2.metric(f"TVA {int(inv['tax_rate'] * 100)}%", f"{inv['tax']:.2f} DH")
        c3.metric("المجموع TTC", f"{inv['total']:.2f} DH")
        if st.button(f"{t('inv_generate_pdf', _inv_lang)}", type="primary", key="inv_pdf"):
            try:
                with st.spinner(t("inv_generating", _inv_lang)):
                    agent = InvoiceAgent()
                    pdf_path = agent.generate_pdf(inv, lang=lang)
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.session_state["inv_pdf_bytes"] = pdf_bytes
                    st.session_state["inv_pdf_name"] = pdf_path
                    st.success(f"{t('inv_pdf_success', _inv_lang)}")
                else:
                    st.error(f"❌ لم يُنشأ الملف: {pdf_path}")
            except Exception as e:
                st.error(f"خطأ: {e}")
        if st.session_state.get("inv_pdf_bytes"):
            st.download_button(f"{t('inv_download_pdf', _inv_lang)}", data=st.session_state["inv_pdf_bytes"], file_name=os.path.basename(st.session_state["inv_pdf_name"]), mime="application/pdf", width="stretch", key="inv_dl")
        if st.button(f"{t('inv_clear', _inv_lang)}", key="inv_clear"):
            for k in ["inv_dict", "inv_pdf_bytes", "inv_pdf_name"]:
                st.session_state.pop(k, None)
            st.rerun()


# Router
# ============================================================
def show_moroccan_admin():
    _ma_lang = st.session_state.get("lang", "ar")
    st.markdown('<div class="main-header">🇲🇦 Moroccan Admin</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">TVA · IS · IR · CNSS · Payroll</div>', unsafe_allow_html=True)
    if st.button(t("back_short", _ma_lang), key="ma_back"):
        st.session_state.page = "landing"
        st.rerun()

    admin = MoroccanAdmin()
    tab1, tab2, tab3, tab4 = st.tabs([t("ma_tab_tva", _ma_lang), t("ma_tab_is", _ma_lang), t("ma_tab_payroll", _ma_lang), t("ma_tab_calendar", _ma_lang)])

    with tab1:
        st.markdown(t("ma_calc_tva", _ma_lang))
        c1, c2 = st.columns(2)
        with c1:
            sales = st.number_input(t("ma_sales_ht", _ma_lang), min_value=0.0, value=100000.0, step=1000.0, key="ma_sales")
        with c2:
            purchases = st.number_input(t("ma_purchases_ht", _ma_lang), min_value=0.0, value=40000.0, step=1000.0, key="ma_purch")
        rate = st.selectbox(t("ma_rate", _ma_lang), ["standard", "reduced1", "reduced2", "reduced3", "exempt"],
                            format_func=lambda x: {"standard":"20%","reduced1":"14%","reduced2":"10%","reduced3":"7%","exempt":"معفى"}[x],
                            key="ma_rate")
        if st.button("احسب TVA", type="primary", key="ma_calc_tva"):
            r = admin.calculate_tva(sales, purchases, rate)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t("ma_tva_collected", _ma_lang), f"{r['tva_collected']:,.2f} DH")
            c2.metric(t("ma_tva_deductible", _ma_lang), f"{r['tva_deductible']:,.2f} DH")
            c3.metric(t("ma_tva_due", _ma_lang), f"{r['tva_due']:,.2f} DH")
            c4.metric(t("ma_status", _ma_lang), r["status"])

    with tab2:
        st.markdown(t("ma_calc_is", _ma_lang))
        c1, c2 = st.columns(2)
        with c1:
            revenue = st.number_input(t("ma_revenue_annual", _ma_lang), min_value=0.0, value=500000.0, step=10000.0, key="ma_rev")
        with c2:
            expenses = st.number_input(t("ma_expenses_annual", _ma_lang), min_value=0.0, value=300000.0, step=10000.0, key="ma_exp")
        if st.button("احسب IS", type="primary", key="ma_calc_is"):
            r = admin.calculate_is(revenue, expenses)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t("ma_profit", _ma_lang), f"{r['profit']:,.2f} DH")
            c2.metric("IS", f"{r['is_due']:,.2f} DH")
            c3.metric(t("ma_effective_rate", _ma_lang), f"{r['effective_rate']}%")
            c4.metric(t("ma_status", _ma_lang), r["status"])

    with tab3:
        st.markdown(t("ma_calc_payroll", _ma_lang))
        salary = st.number_input(t("ma_salary_brut", _ma_lang), min_value=0.0, value=8000.0, step=500.0, key="ma_sal")
        if st.button("احسب Payroll", type="primary", key="ma_calc_pay"):
            r = admin.calculate_payroll(salary)
            st.markdown(t("ma_employee_deductions", _ma_lang))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("CNSS", f"{r['cnss_employee']} DH")
            c2.metric("AMO", f"{r['amo_employee']} DH")
            c3.metric("IR", f"{r['ir_monthly']} DH")
            c4.metric(t("ma_net_salary", _ma_lang), f"{r['net_salary']:,.2f} DH")
            st.markdown(t("ma_employer_costs", _ma_lang))
            c1, c2 = st.columns(2)
            c1.metric(t("ma_employer_cnss", _ma_lang), f"{r['cnss_employer']} DH")
            c2.metric(t("ma_total_cost", _ma_lang), f"{r['total_cost_employer']:,.2f} DH")

    with tab4:
        st.markdown(t("ma_tax_calendar", _ma_lang))
        days = st.slider(t("ma_days_ahead", _ma_lang), 7, 90, 30, key="ma_days")
        deadlines = admin.get_upcoming_deadlines(days)
        if deadlines:
            for d in deadlines:
                st.markdown(f"{d['urgency']} **{d['date']}** — {d['obligation']} *({d['days_left']} يوم)*")
        else:
            st.info(f"لا مواعيد خلال {days} يوماً")


def show_customer_support():
    _cs_lang = st.session_state.get("lang", "ar")
    st.markdown(f'<div class="main-header">{t("cs_title", _cs_lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{t("cs_subtitle", _cs_lang)}</div>', unsafe_allow_html=True)

    if st.button(t("back_short", _cs_lang), key="cs_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = CustomerSupportAgent()

    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox(t("cs_lang", _cs_lang), ["ar", "fr", "en"], format_func=lambda x: {"ar": "العربية", "fr": "Français", "en": "English"}[x], key="cs_lang")
    with c2:
        tone = st.selectbox(t("cs_tone", _cs_lang), ["formal", "friendly", "apologetic"],
                            format_func=lambda x: {"formal":"رسمي","friendly":"ودي","apologetic":"اعتذاري"}[x],
                            key="cs_tone")
    with c3:
        client_name = st.text_input(t("cs_client_name", _cs_lang), key="cs_name")

    text = st.text_area(t("cs_ticket_text", _cs_lang), height=150, key="cs_text",
                        placeholder=t("cs_placeholder", _cs_lang))

    if st.button(t("cs_analyze_btn", _cs_lang), type="primary", key="cs_analyze"):
        if not text.strip():
            st.error(t("cs_enter_ticket", _cs_lang))
        else:
            result = agent.classify_ticket(text, lang=lang)
            result["client_name"] = client_name

            st.divider()
            st.markdown(t("cs_classification", _cs_lang))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t("cs_type", _cs_lang), f"{result['type_icon']} {result['type_label']}")
            c2.metric(t("cs_priority", _cs_lang), f"{result['priority_icon']} {result['priority_label']}")
            c3.metric(t("cs_sentiment", _cs_lang), f"{result['sentiment_emoji']} {result['sentiment_label']}")
            c4.metric(t("cs_escalation", _cs_lang), "⚠️ نعم" if result['needs_escalation'] else "✅ لا")
            if result['needs_escalation']:
                st.warning(f"⚠️ يحتاج تصعيد: {result['escalation_reason']}")

            st.divider()
            st.markdown(t("cs_response", _cs_lang))
            with st.spinner(t("cs_generating", _cs_lang)):
                resp = agent.generate_response(result, tone=tone, lang=lang)
            st.info(f"المصدر: {resp['source']}")
            st.text_area("الرد", value=resp["text"], height=200, key="cs_response")
            st.download_button(t("cs_download_response", _cs_lang), data=resp["text"],
                               file_name=f"response_{lang}.txt", mime="text/plain",
                               key="cs_dl")

            st.divider()
            st.markdown(t("cs_actions", _cs_lang))
            for action in agent.suggest_actions(result, lang=lang):
                st.markdown(f"- {action}")

    with st.expander(t("cs_faq", _cs_lang)):
        faqs = agent.get_faq(lang=lang)
        for faq in faqs:
            st.markdown(f"**{faq['q']}**")
            st.caption(faq["a"])


def show_content_writer():
    _cw_lang = st.session_state.get("lang", "ar")
    st.markdown(f'<div class="main-header">{t("cw_title", _cw_lang)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">مقالات · وصف منتجات · سوشيال ميديا · إعلانات</div>', unsafe_allow_html=True)

    if st.button(t("back_short", _cw_lang), key="cw_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = ContentWriterAgent()

    # الإعدادات
    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox(t("cw_lang", _cw_lang), ["ar", "fr", "en"], format_func=lambda x: {"ar": "العربية", "fr": "Français", "en": "English"}[x], key="cw_lang")
    with c2:
        tone = st.selectbox(t("cw_tone", _cw_lang), list(agent.TONES.keys()),
                            format_func=lambda x: agent.TONES[x][lang],
                            key="cw_tone")
    with c3:
        length = st.selectbox(t("cw_length", _cw_lang), list(agent.LENGTHS.keys()),
                              format_func=lambda x: agent.LENGTHS[x][lang],
                              key="cw_length")

    c1, c2 = st.columns(2)
    with c1:
        content_type = st.selectbox(t("cw_type", _cw_lang), list(agent.CONTENT_TYPES.keys()),
                                    format_func=lambda x: f"{agent.CONTENT_TYPES[x]['icon']} {agent.CONTENT_TYPES[x][lang]}",
                                    key="cw_type")
    with c2:
        topic = st.text_input(t("cw_topic", _cw_lang), key="cw_topic", placeholder=t("cw_topic_placeholder", _cw_lang))

    c1, c2 = st.columns(2)
    with c1:
        audience = st.text_input(t("cw_audience", _cw_lang), key="cw_aud")
    with c2:
        keywords = st.text_input(t("cw_keywords", _cw_lang), key="cw_kw")

    if st.button(t("cw_generate_btn", _cw_lang), type="primary", key="cw_generate"):
        if not topic.strip():
            st.error(t("cw_enter_topic", _cw_lang))
        else:
            with st.spinner(t("cw_generating", _cw_lang)):
                result = agent.generate(content_type, topic, tone, length, lang, audience, keywords)

            st.divider()
            st.info(f"المصدر: {result['source']} | النوع: {result['type_label']} | النبرة: {result['tone']}")

            st.text_area("المحتوى", value=result["content"], height=400, key="cw_output")

            # أزرار التحميل
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    t("cw_download_txt", _cw_lang),
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
                st.markdown(t("cw_hashtags", _cw_lang))
                hashtags = agent.suggest_hashtags(topic, lang=lang)
                st.code(" ".join(hashtags))

            # عناوين مقترحة
            if content_type in ["article", "email"]:
                st.markdown(t("cw_titles", _cw_lang))
                for __title in agent.suggest_titles(topic, lang=lang):
                    st.markdown(f"- {__title}")


def show_email_agent():
    _em_lang = st.session_state.get("lang", "ar")
    st.markdown(f'<div class="main-header">{t("em_title", _em_lang)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">ردود · حملات · متابعة · دعوات</div>', unsafe_allow_html=True)

    if st.button(t("back_short", _em_lang), key="em_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = EmailAgent()

    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox(t("em_lang", _em_lang), ["ar", "fr", "en"], format_func=lambda x: {"ar": "العربية", "fr": "Français", "en": "English"}[x], key="em_lang")
    with c2:
        tone = st.selectbox(t("em_tone", _em_lang), list(agent.TONES.keys()),
                            format_func=lambda x: agent.TONES[x][lang],
                            key="em_tone")
    with c3:
        email_type = st.selectbox(t("em_type", _em_lang), list(agent.EMAIL_TYPES.keys()),
                                  format_func=lambda x: f"{agent.EMAIL_TYPES[x]['icon']} {agent.EMAIL_TYPES[x][lang]}",
                                  key="em_type")

    subject = st.text_input(t("em_topic", _em_lang), key="em_subject", placeholder=t("em_subject_placeholder", _em_lang))

    c1, c2 = st.columns(2)
    with c1:
        recipient = st.text_input(t("em_recipient", _em_lang), key="em_recip")
    with c2:
        sender = st.text_input(t("em_sender", _em_lang), key="em_sender")

    context = st.text_area(t("em_context", _em_lang), height=100, key="em_context",
                           placeholder=t("em_context_placeholder", _em_lang))

    if st.button(t("em_generate_btn", _em_lang), type="primary", key="em_generate"):
        if not subject.strip():
            st.error(t("em_enter_topic", _em_lang))
        else:
            with st.spinner(t("em_generating", _em_lang)):
                result = agent.generate(email_type, subject, context, tone, lang, recipient, sender)

            st.divider()
            st.info(f"المصدر: {result['source']} | النوع: {result['type_label']} | النبرة: {result['tone']}")
            st.text_area("البريد", value=result["content"], height=400, key="em_output")
            st.download_button(
                t("em_download_txt", _em_lang),
                data=result["content"],
                file_name=f"email_{email_type}_{lang}.txt",
                mime="text/plain",
                key="em_dl"
            )

            st.divider()
            st.markdown(t("em_suggested_subjects", _em_lang))
            for s in agent.suggest_subjects(subject, lang=lang):
                st.markdown(f"- {s}")


def show_social_media():
    _sm_lang = st.session_state.get("lang", "ar")
    st.markdown('<div class="main-header">📱 Social Media Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">منشورات جاهزة · 6 منصات · 3 لغات</div>', unsafe_allow_html=True)

    if st.button(t("back_short", _sm_lang), key="sm_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = SocialMediaAgent()

    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox(t("sm_lang", _sm_lang), ["ar", "fr", "en"], format_func=lambda x: {"ar": "العربية", "fr": "Français", "en": "English"}[x], key="sm_lang")
    with c2:
        platform = st.selectbox(t("sm_platform", _sm_lang), list(agent.PLATFORMS.keys()),
                                format_func=lambda x: f"{agent.PLATFORMS[x]['icon']} {agent.PLATFORMS[x][lang]}",
                                key="sm_platform")
    with c3:
        post_type = st.selectbox(t("sm_post_type", _sm_lang), list(agent.POST_TYPES.keys()),
                                 format_func=lambda x: f"{agent.POST_TYPES[x]['icon']} {agent.POST_TYPES[x][lang]}",
                                 key="sm_type")

    c1, c2 = st.columns(2)
    with c1:
        tone = st.selectbox(t("sm_tone", _sm_lang), list(agent.TONES.keys()),
                            format_func=lambda x: agent.TONES[x][lang],
                            key="sm_tone")
    with c2:
        audience = st.text_input(t("sm_audience", _sm_lang), key="sm_aud")

    topic = st.text_input(t("sm_topic", _sm_lang), key="sm_topic", placeholder=t("sm_topic_placeholder", _sm_lang))

    if st.button(t("sm_generate_btn", _sm_lang), type="primary", key="sm_generate"):
        if not topic.strip():
            st.error(t("sm_enter_topic", _sm_lang))
        else:
            with st.spinner(t("sm_generating", _sm_lang)):
                r = agent.generate_post(platform, post_type, topic, tone, lang, audience)

            st.divider()
            best = r['best_chars']
            status = "✅ ممتاز" if r['char_count'] <= best else "⚠️ طويل قليلاً"
            st.info(f"المصدر: {r['source']} | {r['platform_icon']} {r['platform_label']} | الأحرف: {r['char_count']}/{best} {status}")

            st.text_area("المنشور", value=r["content"], height=300, key="sm_output")
            st.download_button(t("sm_download_txt", _sm_lang), data=r["content"],
                               file_name=f"post_{platform}_{lang}.txt", mime="text/plain",
                               key="sm_dl")

            st.markdown(t("sm_hashtags", _sm_lang))
            st.code(" ".join(agent.suggest_hashtags(topic, platform, lang)))


def show_meeting_notes():
    _mn_lang = st.session_state.get("lang", "ar")
    st.markdown(f'<div class="main-header">{t("mn_title", _mn_lang)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">محاضر اجتماعات · مهام · قرارات</div>', unsafe_allow_html=True)

    if st.button(t("back_short", _mn_lang), key="mn_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = MeetingNotesAgent()

    c1, c2, c3 = st.columns(3)
    with c1:
        lang = st.selectbox(t("mn_lang", _mn_lang), ["ar", "fr", "en"], format_func=lambda x: {"ar": "العربية", "fr": "Français", "en": "English"}[x], key="mn_lang")
    with c2:
        mtype = st.selectbox(t("mn_type", _mn_lang), list(agent.MEETING_TYPES.keys()),
                             format_func=lambda x: f"{agent.MEETING_TYPES[x]['icon']} {agent.MEETING_TYPES[x][lang]}",
                             key="mn_type")
    with c3:
        date = st.text_input(t("mn_date", _mn_lang), value=datetime.now().strftime("%Y-%m-%d"), key="mn_date")

    title = st.text_input(t("mn_title_input", _mn_lang), key="mn_title", placeholder=t("mn_title_placeholder", _mn_lang))
    transcript = st.text_area(t("mn_transcript", _mn_lang), height=250, key="mn_text",
                              placeholder=t("mn_transcript_placeholder", _mn_lang))

    if st.button(t("mn_generate_btn", _mn_lang), type="primary", key="mn_generate"):
        if not transcript.strip():
            st.error(t("mn_enter_text", _mn_lang))
        else:
            with st.spinner(t("mn_generating", _mn_lang)):
                r = agent.generate_minutes(transcript, mtype, lang, title, date)

            st.divider()
            st.info(f"المصدر: {r['source']} | النوع: {r['type_label']}")
            st.markdown(r["minutes"])
            st.download_button(t("mn_download_md", _mn_lang), data=r["minutes"],
                               file_name=f"meeting_{date}.md", mime="text/markdown",
                               key="mn_dl")


def show_supplier():
    _sp_lang = st.session_state.get("lang", "ar")
    st.markdown(f'<div class="main-header">{t("sp_title", _sp_lang)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">طلبات · تفاوض · مقارنة الموردين</div>', unsafe_allow_html=True)

    if st.button(t("back_short", _sp_lang), key="sp_back"):
        st.session_state.page = "landing"
        st.rerun()

    agent = SupplierAgent()

    c1, c2 = st.columns(2)
    with c1:
        lang = st.selectbox(t("sp_lang", _sp_lang), ["ar", "fr", "en"], format_func=lambda x: {"ar": "العربية", "fr": "Français", "en": "English"}[x], key="sp_lang")
    with c2:
        rtype = st.selectbox(t("sp_request_type", _sp_lang), list(agent.REQUEST_TYPES.keys()),
                             format_func=lambda x: f"{agent.REQUEST_TYPES[x]['icon']} {agent.REQUEST_TYPES[x][lang]}",
                             key="sp_type")

    c1, c2 = st.columns(2)
    with c1:
        supplier = st.text_input(t("sp_supplier", _sp_lang), key="sp_sup")
    with c2:
        sender = st.text_input(t("sp_sender", _sp_lang), key="sp_sender")

    context = st.text_area(t("sp_context", _sp_lang), height=120, key="sp_ctx",
                           placeholder="مثال: توريد 100 وحدة، ميزانية محددة، شروط...")

    if st.button(t("sp_generate_btn", _sp_lang), type="primary", key="sp_gen"):
        if not context.strip():
            st.error(t("sp_enter_context", _sp_lang))
        else:
            with st.spinner(t("sp_generating", _sp_lang)):
                r = agent.generate_request(rtype, supplier, context, lang, sender)
            st.divider()
            st.info(f"المصدر: {r['source']} | النوع: {r['type_label']}")
            st.text_area("الرسالة", value=r["content"], height=300, key="sp_out")
            st.download_button("⬇️ تحميل", data=r["content"],
                               file_name=f"supplier_{rtype}_{lang}.txt",
                               mime="text/plain", key="sp_dl")


if st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "agents_full":
    if show_agents_full:
        show_agents_full()
    else:
        st.error("⚠️ تطبيق الوكلاء غير متاح حالياً")
elif st.session_state.page == "stats":
    show_stats()
elif st.session_state.page == "my_invoices":
    show_my_invoices()
elif st.session_state.page == "contact":
    show_contact()
elif st.session_state.page == "about":
    show_about()
elif st.session_state.page == "settings":
    show_settings()
elif st.session_state.page == "admin":
    show_admin()
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
