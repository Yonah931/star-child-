"""واجهة الوكلاء: بطاقتان بارزتان + صفوف، والصف المحدد بتدرج ماجنتا → سماوي.
النقر ينتقل مباشرة إلى الصفحة (st.session_state.page)."""
import streamlit as st

_ICONS = {
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/><circle cx="17" cy="9" r="2.4"/><path d="M17 14.5c2.5 0 4 1.7 4 4.5"/>',
    "money": '<path d="M9 3h6l-1.5 3h-3z"/><path d="M8.5 6C5 9 4 12 4 15c0 3.3 2.7 6 8 6s8-2.7 8-6c0-3-1-6-4.5-9"/><path d="M12 10v8M14.2 11.5c-.4-.8-1.2-1.2-2.2-1.2-1.3 0-2.2.7-2.2 1.7 0 2.1 4.4 1.2 4.4 3.4 0 1-1 1.8-2.3 1.8-1.1 0-2-.5-2.4-1.4"/>',
    "spark": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>',
    "chart": '<path d="M4 20V4M4 20h16"/><path d="M8 16v-5M12 16V8M16 16v-3"/>',
    "pen": '<path d="M4 20l1-4L16.5 4.5a2 2 0 0 1 3 3L8 19z"/><path d="M14 7l3 3"/>',
    "doc": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8M8 17h5"/>',
    "flag": '<path d="M4 21V4M4 4h13l-2 4 2 4H4"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-8 8H7l-4 3 1.2-4.5A8 8 0 1 1 21 12z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "phone": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "truck": '<rect x="1" y="6" width="14" height="10" rx="1"/><path d="M15 9h4l3 3v4h-7z"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a13 13 0 0 1 0 18M12 3a13 13 0 0 0 0 18"/>',
    "note": '<path d="M4 4h16v16H4z"/><path d="M8 9h8M8 13h8M8 17h5"/>',
}

_GRAD = "linear-gradient(90deg, #e040fb 0%, #22e5ff 100%)"

_BASE_CSS = """
<style>
.agp-card {
    direction: rtl; text-align: right;
    background-image: linear-gradient(#0d0c18, #0d0c18), linear-gradient(135deg, #22e5ff, #e040fb);
    background-origin: border-box; background-clip: padding-box, border-box;
    border: 1.5px solid transparent; border-radius: 14px;
    padding: 18px 16px 16px; min-height: 150px;
    box-shadow: 0 0 18px rgba(34,229,255,.18), 0 0 26px rgba(224,64,251,.12);
    transition: box-shadow .3s;
}
.agp-card svg { width: 38px; height: 38px; color: #22e5ff; display: block; margin-bottom: 8px;
    filter: drop-shadow(0 0 6px rgba(34,229,255,.7)); }
.agp-card h3 { margin: 0 0 6px 0; font-size: 1.05rem; font-weight: 600; color: #ecebf7; }
.agp-card p  { margin: 0; font-size: .82rem; line-height: 1.6; color: #8d89a9; }
.agp-card.sel { box-shadow: 0 0 24px rgba(34,229,255,.45), 0 0 36px rgba(224,64,251,.3); }

/* الأزرار الافتراضية: داكنة هادئة */
[class*="st-key-agrow_"],
[class*="st-key-agrow_"] button {
    background: #0b0a14 !important; color: #ecebf7 !important;
    border: 1px solid #2a2840 !important; border-radius: 10px !important;
    box-shadow: none !important; transform: none !important; text-shadow: none !important;
    font-weight: 500 !important; min-height: 44px;
    transition: all .25s ease;
}
[class*="st-key-agrow_"] button:hover {
    border-color: #22e5ff !important; color: #22e5ff !important;
    background: #0b0a14 !important; box-shadow: 0 0 14px rgba(34,229,255,.2) !important;
}
</style>
"""


def _navigate(page):
    st.session_state.page = page


def render_agents_panel(agents):
    """يرسم الواجهة. النقر ينتقل مباشرة للصفحة المحددة في حقل page."""
    st.markdown(_BASE_CSS, unsafe_allow_html=True)

    # 2 بطاقات بارزة
    cols = st.columns(2, gap="medium")
    for col, a in zip(cols, agents[:2]):
        with col:
            icon = _ICONS.get(a.get("icon", "spark"), _ICONS["spark"])
            st.markdown(
                f'<div class="agp-card"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{icon}</svg>'
                f'<h3>{a["name"]}</h3><p>{a.get("desc", "")}</p></div>',
                unsafe_allow_html=True,
            )
            st.button(
                "▶ جرّب",
                key=f"agtry_{a['id']}",
                use_container_width=True,
                on_click=_navigate,
                args=(a["page"],),
            )

    # الصفوف المتبقية
    for a in agents[2:]:
        st.button(
            a["name"],
            key=f"agrow_{a['id']}",
            use_container_width=True,
            on_click=_navigate,
            args=(a["page"],),
        )
