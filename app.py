import os
import io
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from contextlib import redirect_stdout
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import operator
from tavily import TavilyClient
from datetime import datetime
from database import init_db, save_task, get_tasks, get_stats
from pdf_report import generate_pdf

load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except:
        return os.getenv(key)


st.set_page_config(page_title="Yonah Ashkenaz Agentic OS", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp {background-color: #0a0e1a;}
    .main-header {font-size: 3rem; font-weight: bold; text-align: center; color: #00d4ff; text-shadow: 0 0 20px #00d4ff88; margin-bottom: 0.2rem;}
    .sub-header {text-align: center; color: #6b7a99; margin-bottom: 2rem; font-size: 1rem;}
    .stat-card {background: linear-gradient(135deg, #1a1f35 0%, #0f1422 100%); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #00d4ff33;}
    .stat-number {font-size: 2rem; font-weight: bold; color: #00d4ff;}
    .stat-label {color: #6b7a99; font-size: 0.85rem; margin-top: 5px;}
    .agent-card {background: linear-gradient(135deg, #1a1f35 0%, #0f1422 100%); border-radius: 10px; padding: 12px; margin: 6px 0; border-left: 4px solid #00d4ff;}
    .agent-name {font-weight: bold; color: #00d4ff; font-size: 0.95rem;}
    .agent-role {color: #6b7a99; font-size: 0.8rem; margin-top: 2px;}
    .status-bar {background: #1a1f35; border-radius: 10px; padding: 12px 20px; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; border: 1px solid #00d4ff33;}
    .status-dot {display: inline-block; width: 10px; height: 10px; background: #00ff88; border-radius: 50%; margin-left: 8px; box-shadow: 0 0 10px #00ff88;}
    .data-badge {background: #00ff8833; color: #00ff88; padding: 4px 10px; border-radius: 10px; font-size: 0.75rem;}
</style>
""", unsafe_allow_html=True)

class AgentState(TypedDict):
    task: str
    next_agent: str
    result: str
    history: Annotated[list, operator.add]

llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    temperature=0.3,
    base_url="https://api.groq.com/openai/v1",
    api_key=get_secret("GROQ_API_KEY")
)

tavily = TavilyClient(api_key=get_secret("TAVILY_API_KEY"))

IDENTITY = """أنت وكيل ذكاء اصطناعي في نظام 'Yonah Ashkenaz'، وهو نظام وكلاء ذكاء اصطناعي لإدارة الشركة.
مؤسس النظام ومالكه هو Yonah Ashkenaz.
لا تذكر أبداً أنك ChatGPT أو OpenAI أو أي شركة أخرى.
إذا سُئلت عن هويتك، قل: 'أنا وكيل ذكاء اصطناعي في نظام Yonah Ashkenaz'.

"""

def ceo_orchestrator(state: AgentState):
    history = state.get("history", [])
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-5:]]) if history else "لا يوجد سياق سابق"
    prompt = IDENTITY + f"""أنت الرئيس التنفيذي (CEO) لنظام وكلاء. 
    الوكلاء المتاحون:
    - 'Researcher': للبحث في الإنترنت والأخبار الحديثة
    - 'CMO': للتسويق والمحتوى
    - 'SalesRep': للمبيعات والعملاء
    - 'Dev': للتطوير التقني وكتابة وتنفيذ أكواد Python
    - 'DataAnalyst': لتحليل البيانات وقراءة ملفات CSV/Excel
    - 'Assistant': للأسئلة العامة والمحادثات
    السياق السابق: {history_text}
    الطلب: {state['task']}
    أجب بكلمة واحدة فقط هي اسم الوكيل المناسب."""
    response = llm.invoke([SystemMessage(content=prompt)])
    next_agent = response.content.strip()
    if next_agent not in ["Researcher", "CMO", "SalesRep", "Dev", "DataAnalyst", "Assistant"]:
        next_agent = "Assistant"
    return {"next_agent": next_agent}

def researcher_agent(state: AgentState):
    try:
        search_result = tavily.search(query=state['task'], max_results=5)
        sources_text = ""
        for i, result in enumerate(search_result.get("results", []), 1):
            sources_text += f"\n\n{i}. {result['title']}\n{result['content'][:400]}...\n🔗 {result['url']}"
        prompt = IDENTITY + f"""أنت باحث خبير. لخص نتائج البحث عن: "{state['task']}"
        النتائج: {sources_text}
        قدم تقريراً منظماً بالعربية مع المصادر."""
        response = llm.invoke([SystemMessage(content=prompt)])
        return {"result": f"🔍 **Researcher** - بحث حقيقي من الإنترنت\n\n{response.content}"}
    except Exception as e:
        return {"result": f"🔍 **Researcher**\n\nحدث خطأ: {str(e)}"}

def cmo_agent(state: AgentState):
    prompt = IDENTITY + f"أنت مدير التسويق (CMO). اكتب خطة تسويقية احترافية للمهمة: {state['task']}"
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"result": f"📢 **CMO**\n\n{response.content}"}

def salesrep_agent(state: AgentState):
    prompt = IDENTITY + f"أنت مندوب مبيعات محترف. اكتب رسالة أو خطة مبيعات للمهمة: {state['task']}"
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"result": f"💼 **SalesRep**\n\n{response.content}"}

def dev_agent(state: AgentState):
    prompt = IDENTITY + f"""أنت مطور Python خبير. اكتب كود Python لحل المهمة التالية:
    {state['task']}
    
    قواعد مهمة:
    - أجب بالكود فقط، بدون شرح.
    - ضع الكود داخل ```python ... ```
    - استخدم print() لعرض النتائج.
    - إذا احتجت مكتبات، استخدم pandas، numpy، أو المكتبات القياسية فقط."""
    response = llm.invoke([SystemMessage(content=prompt)])
    code = response.content.replace("```python", "").replace("```", "").strip()
    
    try:
        output = io.StringIO()
        exec_globals = {"pd": pd, "print": print}
        with redirect_stdout(output):
            exec(code, exec_globals)
        result_text = output.getvalue()
        if not result_text:
            result_text = "(تم التنفيذ بدون مخرجات)"
        return {"result": f"💻 **Dev** - تم توليد الكود وتنفيذه\n\n**الكود:**\n```python\n{code}\n```\n\n**النتيجة:**\n```\n{result_text}\n```"}
    except Exception as e:
        return {"result": f"💻 **Dev**\n\n**الكود:**\n```python\n{code}\n```\n\n⚠️ خطأ في التنفيذ: {str(e)}"}

def dataanalyst_agent(state: AgentState):
    task = state['task']
    df = st.session_state.get("uploaded_data")
    
    if df is not None:
        info = f"""البيانات المتاحة:
- عدد الصفوف: {df.shape[0]}
- عدد الأعمدة: {df.shape[1]}
- أسماء الأعمدة: {list(df.columns)}
- أنواع البيانات:
{df.dtypes.to_string()}

- أول 5 صفوف:
{df.head().to_string()}

- الإحصائيات الوصفية:
{df.describe().to_string()}
"""
        prompt = IDENTITY + f"""أنت محلل بيانات خبير. لديك البيانات التالية:
{info}

المهمة: {task}

قدم تحليلاً مفصلاً ومنظماً بالعربية مع أرقام حقيقية من البيانات."""
    else:
        prompt = IDENTITY + f"""أنت محلل بيانات خبير. حلل المهمة: {task}
        
ملاحظة: لم يتم رفع أي بيانات. قدم تحليلاً عاماً أو اقترح على المستخدم رفع ملف CSV/Excel."""
    
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"result": f"📊 **DataAnalyst**\n\n{response.content}"}

def assistant_agent(state: AgentState):
    history = state.get("history", [])
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-10:]]) if history else ""
    prompt = IDENTITY + f"""أنت مساعد ذكاء اصطناعي عام. أجب بشكل واضح ومفيد.
    السياق: {history_text}
    السؤال: {state['task']}"""
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"result": f"🤖 **Assistant**\n\n{response.content}"}

workflow = StateGraph(AgentState)
workflow.add_node("CEO", ceo_orchestrator)
workflow.add_node("Researcher", researcher_agent)
workflow.add_node("CMO", cmo_agent)
workflow.add_node("SalesRep", salesrep_agent)
workflow.add_node("Dev", dev_agent)
workflow.add_node("DataAnalyst", dataanalyst_agent)
workflow.add_node("Assistant", assistant_agent)
workflow.set_entry_point("CEO")
workflow.add_conditional_edges("CEO", lambda state: state["next_agent"], {
    "Researcher": "Researcher", "CMO": "CMO", "SalesRep": "SalesRep",
    "Dev": "Dev", "DataAnalyst": "DataAnalyst", "Assistant": "Assistant"
})
for agent in ["Researcher", "CMO", "SalesRep", "Dev", "DataAnalyst", "Assistant"]:
    workflow.add_edge(agent, END)

memory = MemorySaver()
init_db()
app = workflow.compile(checkpointer=memory)

# ===== الترويسة =====
st.markdown('<div class="main-header">🤖 Yonah Ashkenaz Agentic OS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">نظام وكلاء الذكاء الاصطناعي لإدارة الشركة</div>', unsafe_allow_html=True)

# ===== شريط الحالة =====
st.markdown(f"""
<div class="status-bar">
    <div><b style="color:#00d4ff;">System Status:</b> Operational <span class="status-dot"></span></div>
    <div style="color:#6b7a99; font-size:0.85rem;">⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)

# ===== الإحصائيات =====
if "total_tasks" not in st.session_state:
    st.session_state.total_tasks = 0
if "agents_used" not in st.session_state:
    st.session_state.agents_used = {"Researcher": 0, "CMO": 0, "SalesRep": 0, "Dev": 0, "DataAnalyst": 0, "Assistant": 0}

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{st.session_state.total_tasks}</div><div class="stat-label">📋 المهام المنفذة</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">7</div><div class="stat-label">🤖 الوكلاء النشطون</div></div>', unsafe_allow_html=True)
with col3:
    has_data = "✅" if st.session_state.get("uploaded_data") is not None else "—"
    st.markdown(f'<div class="stat-card"><div class="stat-number">{has_data}</div><div class="stat-label">📁 البيانات المرفوعة</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">🌐</div><div class="stat-label">Tavily: متصل</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===== شبكة الوكلاء + الحالة =====
col_net, col_status = st.columns([2, 1])

with col_net:
    st.markdown("### 🕸️ شبكة الوكلاء")
    agents = ["CEO", "Assistant", "Researcher", "CMO", "SalesRep", "Dev", "DataAnalyst"]
    labels = ["👑 CEO", "🤖 Assistant", "🔍 Researcher", "📢 CMO", "💼 SalesRep", "💻 Dev", "📊 DataAnalyst"]
    x_pos = [0.5, 0.1, 0.25, 0.42, 0.58, 0.75, 0.9]
    y_pos = [1.0, 0.4, 0.1, 0.1, 0.1, 0.1, 0.1]
    
    edge_x, edge_y = [], []
    for i in range(1, len(agents)):
        edge_x.extend([0.5, x_pos[i], None])
        edge_y.extend([1.0, y_pos[i], None])
    
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1.5, color='#00d4ff44'), hoverinfo='none', mode='lines')
    node_colors = ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d', '#a78bfa', '#4ade80', '#fb923c']
    node_trace = go.Scatter(
        x=x_pos, y=y_pos, mode='markers+text', text=labels,
        textposition="bottom center",
        textfont=dict(size=13, color='#ffffff', family='Arial'),
        marker=dict(size=45, color=node_colors, line=dict(width=2, color='#ffffff')),
        hoverinfo='text',
        hovertext=[f"{a}<br>المهام: {st.session_state.agents_used.get(a, 0)}" for a in agents]
    )
    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        showlegend=False, hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.15, 1.1]),
        plot_bgcolor='#0a0e1a', paper_bgcolor='#0a0e1a', height=400,
    ))
    st.plotly_chart(fig, use_container_width=True)

with col_status:
    st.markdown("### 📊 حالة الوكلاء")
    agents_info = [
        ("👑 CEO", "المنسق الرئيسي"),
        ("🤖 Assistant", "الأسئلة العامة"),
        ("🔍 Researcher", "بحث في الإنترنت"),
        ("📢 CMO", "التسويق والمحتوى"),
        ("💼 SalesRep", "المبيعات والعملاء"),
        ("💻 Dev", "توليد وتنفيذ الأكواد"),
        ("📊 DataAnalyst", "تحليل CSV/Excel"),
    ]
    for name, role in agents_info:
        st.markdown(f'<div class="agent-card"><div class="agent-name">{name}</div><div class="agent-role">{role}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ===== جلسة الذاكرة =====
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"user_{os.urandom(4).hex()}"
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== منطقة المحادثة =====
st.markdown("### 💬 المحادثة")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("ما هي المهمة التي تريدها؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("⏳ الوكلاء يعملون..."):
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            final_state = app.invoke({"task": prompt, "history": history}, config=config)
            result = final_state.get("result", "لا توجد نتيجة")
            next_agent = final_state.get("next_agent", "")
            st.markdown(result)
    
    st.session_state.messages.append({"role": "assistant", "content": result})
    save_task(prompt, next_agent, result)
    st.session_state.total_tasks += 1
    if next_agent in st.session_state.agents_used:
        st.session_state.agents_used[next_agent] += 1
    st.rerun()

# ===== الشريط الجانبي =====
with st.sidebar:
    st.markdown("### 📁 رفع البيانات")
    uploaded_file = st.file_uploader("ارفع ملف CSV أو Excel للتحليل", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.uploaded_data = df
            st.success(f"✅ تم تحميل: {df.shape[0]} صف × {df.shape[1]} عمود")
            with st.expander("👁️ معاينة البيانات"):
                st.dataframe(df.head(10))
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {str(e)}")
    else:
        if st.session_state.get("uploaded_data") is not None:
            df = st.session_state.uploaded_data
            st.markdown(f'<div class="data-badge">📊 {df.shape[0]} صف × {df.shape[1]} عمود</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📜 السجل")
    total, by_agent = get_stats()
    st.markdown(f"**إجمالي المهام:** {total}")
    if by_agent:
        for agent_name, count in by_agent:
            st.markdown(f"- **{agent_name}**: {count} مهمة")
    with st.expander("📋 عرض آخر 10 مهام"):
        tasks = get_tasks(limit=10)
        if tasks:
            for ts, user_in, agent, resp in tasks:
                st.markdown(f"**{ts}** | `{agent}`")
                st.caption(f"👤 {user_in[:80]}")
                st.markdown("---")
        else:
            st.info("لا توجد مهام مسجلة بعد.")
    st.markdown("---")
    st.markdown("### ⚙️ التحكم")
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.session_state.thread_id = f"user_{os.urandom(4).hex()}"
        st.rerun()
    if st.button("🔄 إعادة تعيين الإحصائيات"):
        st.session_state.total_tasks = 0
        st.session_state.agents_used = {"Researcher": 0, "CMO": 0, "SalesRep": 0, "Dev": 0, "DataAnalyst": 0, "Assistant": 0}
        st.rerun()
    if st.button("🗑️ حذف البيانات المرفوعة"):
        st.session_state.uploaded_data = None
        st.rerun()
    if st.button("📄 توليد تقرير PDF"):
        if st.session_state.get("messages"):
            try:
                pdf_path = generate_pdf(st.session_state.messages)
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ تحميل التقرير", f, file_name="sureflow_report.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"خطأ: {str(e)}")
        else:
            st.warning("لا توجد محادثة لتوليد تقرير")
