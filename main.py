
from langfuse.langchain import CallbackHandler
from langchain_openai import AzureChatOpenAI
from deepagents import create_deep_agent
import os
import json
from datetime import datetime
from typing import TypedDict, Optional
import re
from datetime import datetime

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openrouter import ChatOpenRouter
from langchain_tavily import TavilySearch
from langfuse.langchain import CallbackHandler


MEMORY_PATH = "AGENTS.md"



load_dotenv()


llm = ChatOpenRouter(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
langfuse_handler = CallbackHandler()


tavily = TavilySearch(
    max_results=5,
    topic="general",
)





def read_memory(max_chars: int = 4000) -> str:
    if not os.path.exists(MEMORY_PATH):
        return ""
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        data = f.read()
    return data[-max_chars:]


def append_memory(content: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n\n## Memory update - {timestamp}\n{content.strip()}\n")


def write_text(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def read_text(path: str, max_chars: int = 12000) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    return data[:max_chars]


def write_json(path: str, data) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path
BASE_RUNS_DIR = "runs"

def slugify_question(question: str, max_words: int = 8) -> str:
    text = question.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    words = text.split()[:max_words]
    slug = "-".join(words)
    return slug or "untitled-run"


def create_run_dir(question: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify_question(question)
    run_dir = os.path.join(BASE_RUNS_DIR, f"{timestamp}_{slug}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


class GraphState(TypedDict, total=False):
    user_request: str
    run_dir: str

    plan_path: str
    research_raw_path: str
    research_summary_path: str
    analysis_path: str
    report_path: str

    final_preview: str
    memory_update: str

class ResearchState(TypedDict, total=False):
    user_request: str
    memory_context: str
    research_raw_path: str
    research_summary_path: str
    run_dir: str

def research_search_node(state: ResearchState) -> ResearchState:
    request = state["user_request"]

    queries_prompt = f"""
You are a web research planner.

Create 3 focused web search queries for the user's task.
The task can be about any topic: companies, technology, news, people, products, papers, tutorials, or general research.

Rules:
- Do not assume the topic is about competitors unless the user asks that.
- Make queries specific and useful.
- Return only a JSON array of strings.

User task:
{request}
"""


    msg = llm.invoke(queries_prompt)
    raw = msg.content.strip()

    try:
        queries = json.loads(raw)
        if not isinstance(queries, list):
            raise ValueError()
    except Exception:
        queries = [
            f"{request} competitors",
            f"{request} pricing",
            f"{request} alternatives comparison",
        ]

    all_results = []

    for q in queries[:3]:
        result = tavily.invoke({"query": q})
        all_results.append({
            "query": q,
            "results": result,
        })

    raw_path = os.path.join(state["run_dir"], "research_raw.json")
    write_json(raw_path, all_results)

    return {"research_raw_path": raw_path}


def research_summarize_node(state: ResearchState) -> ResearchState:
    raw_path = state["research_raw_path"]
    raw_data = read_text(raw_path, max_chars=20000)

    prompt = f"""
You are the researcher worker.

Summarize the web research for the user's actual task.
Do not force the answer into competitor analysis unless the user asked for that.

User task:
{state["user_request"]}

Memory context:
{state.get("memory_context", "")}

Raw research data:
{raw_data}

Output:
- Key findings
- Important facts
- Useful source URLs
- Uncertainties or missing info
- Suggested next analysis steps
"""

    msg = llm.invoke(prompt)

    summary_path = os.path.join(state["run_dir"], "research_summary.md")
    write_text(summary_path, msg.content)

    return {"research_summary_path": summary_path}


research_builder = StateGraph(ResearchState)
research_builder.add_node("research_search", research_search_node)
research_builder.add_node("research_summarize", research_summarize_node)
research_builder.add_edge(START, "research_search")
research_builder.add_edge("research_search", "research_summarize")
research_builder.add_edge("research_summarize", END)
research_graph = research_builder.compile()


# =========================
# Analyst Subgraph
# =========================

class AnalystState(TypedDict, total=False):
    user_request: str
    memory_context: str
    research_summary_path: str
    analysis_path: str
    run_dir: str


def analyst_node(state: AnalystState) -> AnalystState:
    research_summary = read_text(state["research_summary_path"], max_chars=16000)

    prompt = f"""
You are the analyst worker.

Analyze the research summary.
Do NOT write the final polished report.
Save your output as structured analysis.

User task:
{state["user_request"]}

Memory context:
{state.get("memory_context", "")}

Research summary:
{research_summary}

Output:
- competitor comparison
- strengths
- weaknesses
- pricing patterns
- target user segments
- market gaps
- recommendation angles
"""

    msg = llm.invoke(prompt)

    analysis_path = os.path.join(state["run_dir"], "analysis.md")
    write_text(analysis_path, msg.content)

    return {"analysis_path": analysis_path}


analyst_builder = StateGraph(AnalystState)
analyst_builder.add_node("analyst", analyst_node)
analyst_builder.add_edge(START, "analyst")
analyst_builder.add_edge("analyst", END)
analyst_graph = analyst_builder.compile()


# =========================
# Writer Subgraph
# =========================

class WriterState(TypedDict, total=False):
    user_request: str
    memory_context: str
    analysis_path: str
    report_path: str
    final_preview: str
    run_dir: str


def writer_node(state: WriterState) -> WriterState:
    analysis = read_text(state["analysis_path"], max_chars=16000)

    prompt = f"""
You are the writer worker.

Write a polished Markdown report based on the analysis.
The report must match the user's actual task.
Do not force competitor sections unless the user asked for competitor comparison.
Do not invent facts beyond the analysis.
If data is uncertain, say so.

User task:
{state["user_request"]}

Memory context:
{state.get("memory_context", "")}

Analysis:
{analysis}

Output a clear Markdown report with sections appropriate to the task.
"""

    msg = llm.invoke(prompt)

    report_path = os.path.join(state["run_dir"], "final_report.md")
    write_text(report_path, msg.content)

    preview = msg.content[:1200]

    return {
        "report_path": report_path,
        "final_preview": preview,
    }


writer_builder = StateGraph(WriterState)
writer_builder.add_node("writer", writer_node)
writer_builder.add_edge(START, "writer")
writer_builder.add_edge("writer", END)
writer_graph = writer_builder.compile()


def init_run_node(state: GraphState) -> GraphState:
    run_dir = create_run_dir(state["user_request"])

    metadata_path = os.path.join(run_dir, "metadata.json")
    metadata = {
        "user_request": state["user_request"],
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": "started",
    }

    write_json(metadata_path, metadata)

    return {"run_dir": run_dir}


# =========================
# Parent Orchestrator Nodes
# =========================

def orchestrator_node(state: GraphState) -> GraphState:
    memory = read_memory()

    prompt = f"""
You are the orchestrator for a fixed LangGraph multi-agent system.

Available workers ONLY:
1. researcher_subgraph
   - Creates search queries
   - Uses Tavily web search
   - Saves raw research and research summary files

2. analyst_subgraph
   - Reads the research summary file
   - Analyzes the findings
   - Saves analysis.md

3. writer_subgraph
   - Reads analysis.md
   - Writes the final Markdown report

4. memory_update
   - Updates AGENTS.md with reusable lessons only

Important:
- Do NOT mention workers, APIs, tools, or steps that do not exist.
- Do NOT claim browsing happens outside Tavily.
- Do NOT put raw data in the parent state.
- Workers communicate using file paths.

User request:
{state["user_request"]}

Current memory:
{memory}

Write a realistic execution plan that this exact graph will follow.
Include:
- Goal
- Steps
- Which worker handles each step
- Expected output artifact for each step
"""

    msg = llm.invoke(prompt)

    plan_path = os.path.join(state["run_dir"], "plan.md")
    write_text(plan_path, msg.content)

    return {"plan_path": plan_path}


def run_research_subgraph(state: GraphState) -> GraphState:
    memory = read_memory()

    result = research_graph.invoke({
        "user_request": state["user_request"],
        "memory_context": memory,
        "run_dir": state["run_dir"],
    })

    return {
        "research_raw_path": result["research_raw_path"],
        "research_summary_path": result["research_summary_path"],
    }


def run_analyst_subgraph(state: GraphState) -> GraphState:
    memory = read_memory()

    result = analyst_graph.invoke({
        "user_request": state["user_request"],
        "memory_context": memory,
        "research_summary_path": state["research_summary_path"],
        "run_dir": state["run_dir"],
    })

    return {
        "analysis_path": result["analysis_path"],
    }


def run_writer_subgraph(state: GraphState) -> GraphState:
    memory = read_memory()

    result = writer_graph.invoke({
        "user_request": state["user_request"],
        "memory_context": memory,
        "analysis_path": state["analysis_path"],
        "run_dir": state["run_dir"],
    })

    return {
        "report_path": result["report_path"],
        "final_preview": result["final_preview"],
    }


def memory_update_node(state: GraphState) -> GraphState:
    prompt = f"""
You are the orchestrator memory manager.

Your job is to improve future runs of this multi-agent research system.

Do NOT store:
- Raw research data
- Full reports
- One-time facts that are only useful for this exact task
- Large summaries
- URLs unless they are generally reusable

Store ONLY reusable lessons such as:
- Better search strategies
- Better query patterns
- User preferences
- Workflow improvements
- Common mistakes to avoid
- Useful formatting preferences
- Domain-independent improvements
- If the user topic suggests a recurring domain, store a short reusable note

User request:
{state["user_request"]}

Artifacts created:
- plan: {state.get("plan_path")}
- research summary: {state.get("research_summary_path")}
- analysis: {state.get("analysis_path")}
- report: {state.get("report_path")}

Based on this run, return either:

NO_UPDATE

or a short AGENTS.md memory update that will help future searches.
Keep it under 8 bullet points.
"""

    msg = llm.invoke(prompt)
    memory_note = msg.content.strip()

    if memory_note and memory_note != "NO_UPDATE":
        append_memory(memory_note)

    return {"memory_update": memory_note}


# =========================
# Parent Graph
# =========================

builder = StateGraph(GraphState)
builder.add_node("init_run", init_run_node)
builder.add_node("orchestrator", orchestrator_node)
builder.add_node("researcher_subgraph", run_research_subgraph)
builder.add_node("analyst_subgraph", run_analyst_subgraph)
builder.add_node("writer_subgraph", run_writer_subgraph)
builder.add_node("memory_update", memory_update_node)

builder.add_edge(START, "init_run")
builder.add_edge("init_run", "orchestrator")
builder.add_edge("orchestrator", "researcher_subgraph")
builder.add_edge("researcher_subgraph", "analyst_subgraph")
builder.add_edge("analyst_subgraph", "writer_subgraph")
builder.add_edge("writer_subgraph", "memory_update")
builder.add_edge("memory_update", END)

app = builder.compile()


# =========================
# Run
# =========================

if __name__ == "__main__":
    result = app.invoke(
        {
            "user_request": """
Research the architecture differences between graph-based and agent-based AI frameworks.

Explain when to use:
- LangGraph-style systems
- Agent-loop systems (LangChain, AutoGen)
- Hybrid systems

Include real-world use cases and trade-offs in scalability, cost, and control.

Save as ai_agent_architecture_patterns.md.
"""
        },
        config={
            "callbacks": [langfuse_handler],
            "run_name": "langgraph-multi-agent-research",
            "tags": ["langgraph", "openrouter", "tavily", "multi-agent"],
            "metadata": {
                "project": "langgraph-openrouter-research",
                "architecture": "orchestrator-workers-subgraphs",
                "anti_bottleneck": "artifact-paths-not-raw-data",
            },
        },
    )

    print("\n=== DONE ===")
    print("Plan:", result.get("plan_path"))
    print("Research raw:", result.get("research_raw_path"))
    print("Research summary:", result.get("research_summary_path"))
    print("Analysis:", result.get("analysis_path"))
    print("Report:", result.get("report_path"))

    print("\n=== REPORT PREVIEW ===\n")
    print(result.get("final_preview", "No preview"))




