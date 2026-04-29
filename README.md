# LangGraph Multi-Agent Research System

A file-based multi-agent research system built with **LangGraph**, **OpenRouter**, **Tavily Search**, and **Langfuse**.

The system is designed around an explicit orchestrator-worker architecture:

```text
User Request
    ↓
Orchestrator
    ↓
Researcher Subgraph
    ↓
Analyst Subgraph
    ↓
Writer Subgraph
    ↓
Memory Update
```

Each run creates its own folder, saves artifacts to disk, and passes **file paths** between workers instead of sending large raw data through the orchestrator. This keeps the orchestrator lightweight and reduces context bottlenecks.

---

## Why this project is useful

This project demonstrates a practical multi-agent architecture for research tasks where different responsibilities are separated into specialized workers:

- **Orchestrator**: creates a realistic execution plan and coordinates workers.
- **Researcher**: generates search queries, calls Tavily, and saves raw research plus a summary.
- **Analyst**: reads the research summary and produces structured analysis.
- **Writer**: reads the analysis and produces the final Markdown report.
- **Memory updater**: updates `AGENTS.md` with reusable lessons that can improve future runs.

The main design goal is to avoid overloading the orchestrator. Large intermediate outputs are saved as artifacts, and only paths like `research_summary_path`, `analysis_path`, and `report_path` move through the parent graph.

---

## Key Features

- Explicit LangGraph workflow with visible nodes
- Worker subgraphs for researcher, analyst, and writer
- OpenRouter LLM support
- Tavily web search integration
- Langfuse tracing support
- Dynamic `AGENTS.md` memory updates
- Separate run folder per user question
- Artifact-based communication to avoid context bottlenecks
- Markdown reports saved automatically

---

## Repository Structure

Recommended structure:

```text
.
├── main.py
├── AGENTS.md
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
└── runs/
    └── <timestamp_question-summary>/
        ├── metadata.json
        ├── plan.md
        ├── research_raw.json
        ├── research_summary.md
        ├── analysis.md
        └── final_report.md
```

Do **not** commit your real `.env` file or generated run artifacts unless you intentionally want to share examples.

---

## Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_key
TAVILY_API_KEY=your_tavily_key

LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=http://localhost:3000
```

If you run Langfuse with Docker locally, `LANGFUSE_HOST` is usually:

```env
LANGFUSE_HOST=http://localhost:3000
```

---

## Running

```bash
python main.py
```

Example task:

```text
Research and compare the top frameworks for building AI agents and multi-agent systems in 2026.

Focus on:
- LangChain
- LangGraph
- Deep Agents
- AutoGen
- CrewAI
- Semantic Kernel

Compare architecture, ease of use, flexibility, memory/state handling, multi-agent support, production readiness, and scalability.

Save the final report as ai_agent_frameworks_comparison_2026.md.
```

Each run creates a new folder under `runs/`.

---

## How the System Works

### 1. Orchestrator

The orchestrator creates a realistic `plan.md` for the exact workers available in the graph. It should not invent tools, workers, APIs, or steps that do not exist.

It coordinates the graph, but it does not carry raw research data.

### 2. Researcher Subgraph

The researcher subgraph:

1. Converts the user request into search queries.
2. Calls Tavily Search.
3. Saves raw results to `research_raw.json`.
4. Summarizes findings into `research_summary.md`.

It returns only file paths to the parent graph.

### 3. Analyst Subgraph

The analyst subgraph reads `research_summary.md` and produces `analysis.md`.

It focuses on reasoning, comparison, gaps, strengths, weaknesses, risks, and recommendations.

### 4. Writer Subgraph

The writer subgraph reads `analysis.md` and creates the final Markdown report.

The final report is saved inside the run folder.

### 5. Memory Update

The memory updater decides whether anything from the run should be added to `AGENTS.md`.

It should store reusable lessons only, such as:

- better search strategies
- common workflow improvements
- user preferences
- formatting preferences
- mistakes to avoid in future runs

It should not store raw research or full reports.

---

## Why artifact-based communication?

A common problem in multi-agent systems is that the orchestrator becomes a bottleneck.

Bad pattern:

```text
Researcher returns huge raw data
    ↓
Orchestrator context becomes huge
    ↓
Analyst receives bloated context
    ↓
Writer receives even more bloated context
```

This project avoids that by using artifact paths:

```text
Researcher writes research_summary.md
    ↓
Orchestrator receives only research_summary_path
    ↓
Analyst reads the file directly
    ↓
Analyst writes analysis.md
    ↓
Writer reads analysis.md
```

This reduces token usage, latency, and context overflow risk.

---

## Trade-off: Full Agentic Style vs Workflow

> "Also you need to show in the repo README the trade-off of using this full agentic style and using a workflow since the research task is predictable."

This means:

Because the research task has a predictable structure, we should explain whether we really need a fully autonomous agentic system, or whether a fixed workflow is better.

### Full Agentic Style

A full agentic system gives the LLM more freedom. It can decide:

- which worker to call
- when to search
- when to analyze
- when to write
- when to revise
- whether to update memory

#### Pros

- Flexible for unknown or changing tasks
- Can adapt when the user request is ambiguous
- Can decide extra steps when needed
- Useful for open-ended research

#### Cons

- More expensive
- Harder to debug
- More likely to take unnecessary steps
- More variable output quality
- Higher risk of context bloat
- Harder to guarantee exact execution order

### Workflow Style

A workflow is more fixed and predictable:

```text
orchestrator → researcher → analyst → writer → memory_update
```

The system always follows known steps.

#### Pros

- Easier to debug
- Cheaper and faster
- More reliable
- Easier to trace in Langfuse
- Better for predictable tasks
- Easier to prevent orchestrator bottlenecks

#### Cons

- Less flexible
- May run unnecessary steps for simple questions
- Needs explicit routing logic if you want dynamic behavior

### Why this project uses a workflow-first multi-agent design

The research task is mostly predictable:

```text
search → summarize → analyze → write
```

So a fixed LangGraph workflow is a good fit.

However, the system still uses agent-like workers inside the workflow. This gives a useful balance:

- The graph controls the overall execution.
- The workers use LLM reasoning inside each stage.
- Artifacts prevent context bottlenecks.
- Langfuse makes the execution trace clear.

In short:

```text
Use workflow for control.
Use agents inside nodes for reasoning.
Use files for large data.
```

This hybrid approach is more production-friendly than a fully free-form agent loop for predictable research tasks.

---

## What to commit to GitHub

Commit:

```text
main.py
README.md
requirements.txt
.env.example
.gitignore
AGENTS.md
```

Do not commit:

```text
.env
runs/
artifacts/
output/
__pycache__/
*.pyc
```

Generated reports can be committed only if you want to show examples.

---

## Example `.gitignore`

```gitignore
.env
__pycache__/
*.pyc
.venv/
venv/
runs/
artifacts/
output/
.DS_Store
```

---

## Possible Improvements

- Add a reviewer node after writer
- Add quality gates after each worker
- Add retry logic for Tavily failures
- Add citation validation
- Add routing so simple questions skip unnecessary workers
- Add caching for repeated Tavily searches
- Add metadata status updates per node
- Add human approval before memory updates
- Add automatic cleanup or deduplication for `AGENTS.md`

---

## License

MIT
