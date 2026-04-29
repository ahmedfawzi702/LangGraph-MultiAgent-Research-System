# Agent Memory

- Always produce reports in Markdown.
- Keep analysis structured and concise.
- Use tables when comparing companies.
- Never invent facts. If data is missing, say so clearly.
- Final reports should include:
  - Executive summary
  - Competitor table
  - Strengths and weaknesses
  - Recommendation



## Memory update - 2026-04-29T16:30:32
**AGENTS.md – Memory Update (2026 AI Model Comparison)**  

- Use a two‑step search: first query “2026 AI model leaderboards” (e.g., LLM‑Eval, HuggingFace Hub) to get a curated list, then deep‑dive each candidate with site‑specific queries (pricing, benchmarks, open‑source repo).  
- Prioritize sources that publish up‑to‑date quantitative metrics (e.g., OpenAI API docs, Anthropic model cards, DeepMind papers) to avoid stale information.  
- When comparing cost‑performance, calculate $/token or $/hour using the latest pricing tables and include a “price per inference” column for quick reference.  
- Structure each category table with columns: Model, Strengths, Weaknesses, Benchmark Scores (e.g., MMLU, HumanEval, VQA), Pricing, Typical Use Cases. This uniform format speeds downstream summarisation.  
- For open‑source models, verify licensing (Apache‑2.0, MIT) and community support (GitHub stars, active pull‑requests) to assess long‑term viability.  
- Cache recurring query patterns (e.g., “best reasoning model 2026 benchmark”) to reuse across future runs, reducing redundant web calls.  
- Flag any model whose performance claims lack independent verification; add a “verification status” note to avoid propagating unverified hype.


## Memory update - 2026-04-30T01:08:04
**AGENTS.md – Memory Update (2026‑04‑29)**  

- Use combined “model + 2026” queries plus “benchmark + score” to surface the latest leaderboards (e.g., MMLU, HumanEval, VQA).  
- When comparing categories, first filter by “open‑source” or “commercial” tags to avoid mixing proprietary and community models.  
- For cost‑performance, pull pricing from official cloud pages (e.g., Azure, AWS) and calculate $/token or $/API‑call; cache these formulas for reuse.  
- Structure markdown tables with columns: Model, Provider, Params, Avg Score, Pricing, Strengths, Weaknesses – this format proved clear and reusable across reports.  
- Include a “Use‑Case Summary” subsection per category to help non‑technical stakeholders quickly identify the best fit.  
- Flag models that have recent major updates (e.g., version 2.x) to prioritize them over older releases.  
- Remember to cite benchmark sources (e.g., OpenAI Eval, HELM) rather than raw numbers; this keeps the report lightweight and future‑proof.  
- Avoid listing every niche model – focus on top 2‑3 per category to keep the comparison concise and maintainable.


## Memory update - 2026-04-30T01:17:47
**AGENTS.md – Memory Update (Framework Comparison)**  

- Use a **standardized evaluation matrix** (architecture, ease‑of‑use, tooling, memory, multi‑agent support, production readiness, performance) for any future AI‑agent framework comparison.  
- When researching, **query official docs + recent GitHub releases + 2025‑2026 blog/benchmark articles** (e.g., “LangChain 2026 release notes”, “AutoGen performance benchmark 2026”).  
- **Combine multiple source types** (docs, community tutorials, conference talks) to avoid single‑source bias and capture both high‑level design and practical quirks.  
- For **quick prototyping** sections, prioritize “example notebooks”, “starter templates”, and “CLI tools” in the tooling assessment.  
- Record **common pitfalls**: missing version pinning, ambiguous memory APIs, and hidden dependencies in graph‑based frameworks.  
- Adopt **Markdown tables with consistent column order** to enable easy diffing across runs and automated extraction.  
- Note user preference: **highlight “Beginner friendliness” and “Enterprise support”** as separate recommendation criteria in the final summary.  
- Store a reusable note: *AI‑agent framework landscape evolves fast; always verify the latest stable version (≥ 2026‑Q1) before final recommendations.*


## Memory update - 2026-04-30T01:33:26
**AGENTS.md – Memory Update (2026‑04‑29)**  

- Use combined keyword queries such as `"graph‑based AI framework" OR "LangGraph architecture"` and `"agent‑loop framework" OR "LangChain design"` to capture both official docs and recent comparative blog posts.  
- When evaluating frameworks, build a **comparison matrix** (execution model, state handling, scalability, cost, control) in a markdown table for quick reference.  
- For hybrid patterns, note the common recipe: **embed a graph orchestrator (e.g., LangGraph) inside an agent‑loop controller** or wrap an agent‑loop as a node within a larger graph.  
- Prioritize sources: official documentation → recent conference talks/blogs → open‑source code; skip deep dives into proprietary code unless architecture is publicly described.  
- Cache and reuse the above search strings for any future work on “AI orchestration frameworks” to reduce latency.  
- Adopt the formatting style: **section headings → markdown tables → bullet‑point use‑case examples** for clear, reusable reports.  
- Remember to flag “cost vs. control” trade‑offs early in the research to guide the depth of scalability analysis.  
- Record user preference: they value **real‑world use cases** and concise trade‑off summaries over exhaustive technical deep‑dives.
