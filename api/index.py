import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import operator
from tavily import TavilyClient

load_dotenv()

app = FastAPI(title="Yonah Ashkenaz API")

# CORS - السماح لـ React بالاتصال
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yonah-frontend.vercel.app", "https://star-child-three.vercel.app", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentState(TypedDict):
    task: str
    next_agent: str
    result: str
    history: Annotated[list, operator.add]

llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    temperature=0.3,
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

IDENTITY = """أنت وكيل ذكاء اصطناعي في نظام 'Yonah Ashkenaz'.
مؤسس النظام ومالكه هو Yonah Ashkenaz.
لا تذكر أبداً أنك ChatGPT أو OpenAI.
"""

def ceo(state: AgentState):
    prompt = IDENTITY + f"""أنت الرئيس التنفيذي. الوكلاء: Researcher, CMO, SalesRep, Dev, DataAnalyst, Assistant.
    الطلب: {state['task']}
    أجب بكلمة واحدة فقط هي اسم الوكيل."""
    r = llm.invoke([SystemMessage(content=prompt)])
    n = r.content.strip()
    if n not in ["Researcher","CMO","SalesRep","Dev","DataAnalyst","Assistant"]:
        n = "Assistant"
    return {"next_agent": n}

def researcher(state: AgentState):
    try:
        sr = tavily.search(query=state['task'], max_results=3)
        txt = ""
        for i, r in enumerate(sr.get("results", []), 1):
            txt += f"\n\n{i}. {r['title']}\n{r['content'][:300]}...\n🔗 {r['url']}"
        prompt = IDENTITY + f"لخص نتائج البحث عن: {state['task']}\n{txt}"
        resp = llm.invoke([SystemMessage(content=prompt)])
        return {"result": resp.content}
    except Exception as e:
        return {"result": f"خطأ: {str(e)}"}

def cmo(state: AgentState):
    r = llm.invoke([SystemMessage(content=IDENTITY + f"أنت CMO. اكتب خطة تسويقية: {state['task']}")])
    return {"result": r.content}

def salesrep(state: AgentState):
    r = llm.invoke([SystemMessage(content=IDENTITY + f"أنت SalesRep. اكتب خطة مبيعات: {state['task']}")])
    return {"result": r.content}

def dev(state: AgentState):
    r = llm.invoke([SystemMessage(content=IDENTITY + f"أنت Dev. اكتب كود Python: {state['task']}")])
    return {"result": r.content}

def dataanalyst(state: AgentState):
    r = llm.invoke([SystemMessage(content=IDENTITY + f"أنت DataAnalyst. حلل: {state['task']}")])
    return {"result": r.content}

def assistant(state: AgentState):
    r = llm.invoke([SystemMessage(content=IDENTITY + f"أنت مساعد. أجب: {state['task']}")])
    return {"result": r.content}

wf = StateGraph(AgentState)
wf.add_node("CEO", ceo)
wf.add_node("Researcher", researcher)
wf.add_node("CMO", cmo)
wf.add_node("SalesRep", salesrep)
wf.add_node("Dev", dev)
wf.add_node("DataAnalyst", dataanalyst)
wf.add_node("Assistant", assistant)
wf.set_entry_point("CEO")
wf.add_conditional_edges("CEO", lambda s: s["next_agent"], {
    "Researcher": "Researcher", "CMO": "CMO", "SalesRep": "SalesRep",
    "Dev": "Dev", "DataAnalyst": "DataAnalyst", "Assistant": "Assistant"
})
for a in ["Researcher","CMO","SalesRep","Dev","DataAnalyst","Assistant"]:
    wf.add_edge(a, END)
graph = wf.compile()

class Task(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {"status": "Yonah Ashkenaz API", "version": "1.0"}

@app.post("/ask")
def ask(task: Task):
    result = graph.invoke({"task": task.prompt, "history": []})
    return {
        "agent": result.get("next_agent"),
        "response": result.get("result", "لا توجد نتيجة")
    }
from fastapi import Request
from fastapi.responses import Response

import traceback
from fastapi.responses import JSONResponse

@app.post("/ask")
def ask(task: Task):
    try:
        out = graph.invoke(
            {"task": task.prompt, "next_agent": "", "result": ""},
            config={"recursion_limit": 40},
        )
        return {"agent": out.get("next_agent", ""), "response": out.get("result", "")}
    except Exception as e:
        return JSONResponse(
            {"error": repr(e), "trace": traceback.format_exc()[-1500:]},
            status_code=500,
        )
