# 08_agent_creation_platforms.md
# Agent Creation & Orchestration Platforms (v1)

## Goal
Select a platform to run multi-agent workflows with tool access, state, and reproducibility.

---

## Option A: Claude Agent SDK
**Best for:** Code-first, Anthropic-centric workflows

**Pros**
- Native agent + tool abstractions
- Streaming tool calls
- Strong text reasoning

**Cons**
- Smaller ecosystem than LangChain
- You write more glue code

**Fit**
- Excellent if you prefer tight control and minimal abstractions

---

## Option B: OpenAI Responses API + Agents SDK
**Best for:** Unified agent loops with built-in tools

**Pros**
- Single API for multi-step reasoning + tools
- Native image/video generation options
- Large ecosystem

**Cons**
- Less explicit graph modeling
- Requires discipline to avoid monolithic prompts

**Fit**
- Good if you want fewer moving parts

---

## Option C: LangGraph (LangChain)
**Best for:** Explicit state machines and complex pipelines

**Pros**
- Clear node/edge modeling
- Durable workflows
- Easy to visualize execution

**Cons**
- More setup
- Overkill for early experimentation

**Fit**
- Ideal once the pipeline stabilizes

---

## Recommendation (Phased)
- Phase 1: OpenAI Responses API or Claude Agent SDK (simple loops)
- Phase 2: Migrate to LangGraph once roles/prompts stabilize

---

## Non-Goals
- Full autonomy
- Self-modifying agents
- Closed-loop optimization

Human (you + Stephanie) remain the authority.

---
