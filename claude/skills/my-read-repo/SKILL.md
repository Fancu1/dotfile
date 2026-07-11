---
name: my-read-repo
description: Use when the user wants to deeply learn or understand an unfamiliar codebase, before any code reading begins. Use when user says "read this repo", "learn this project", "explain this codebase", or wants to understand a project as if they wrote it.
---

# My Read Repo

## Overview

Teach a codebase to the user through progressive discovery, not information dumping. The user should feel like they're building the project from scratch in their head.

**Core principle:** At every step, the user's mental model must be complete and runnable — just simplified. Never leave them with a broken half-picture.

**This skill produces a written document (or series of documents), not a conversation.** The output is a standalone guide that the user reads offline.

## The Iron Law

```
NEVER TELL THE USER A CONCLUSION. MAKE THEM DISCOVER IT.
```

Each layer presents a working system, then reveals its flaw. The user should think "oh, that won't work because..." BEFORE you explain the solution.

## Process

### Phase 1: Research (Silent, No Output to User)

**You MUST complete ALL research before writing anything.**

Context windows compress during long conversations. If you write layer 1 then research layer 5, you may have lost the details from layer 1. Research everything first, write everything at the end.

```
1. Identify the project's ONE core loop / main abstraction
2. Read ALL key files along the critical path (entry point → core engine → plugins/extensions)
3. Identify 5-8 design decisions that shaped the codebase
4. Find ONE concrete scenario that exercises the most code paths
5. Note: data structures, control flow branches, error handling, edge cases
```

**Use parallel agents for research.** Dispatch multiple Explore agents to read different subsystems simultaneously. Gather all findings before writing.

### Phase 2: Plan the Layers

Each layer = ONE new concept. Order by dependency (concept B requires concept A).

**Template for planning:**

```
Layer N:
- New concept: [one sentence]
- The flaw it fixes from layer N-1: [what broke]
- Key data structures introduced: [list]
- Pseudocode delta: [what changes from previous layer]
- Scenario moment: [which part of the running example hits this]
```

Typical layer count: 5-8. More than 10 means your concepts aren't chunked well.

### Phase 3: Write the Document

Write ALL layers to a single file (or a directory of files). The user reads this offline.

**Each layer has exactly 3 sections:**

#### Section A: "Here's the System" (pseudocode + data structures)

Give the user a COMPLETE, RUNNABLE mental model at this layer's fidelity.

Rules:
- Pseudocode, not real code. No language-specific syntax noise.
- Show data structures explicitly: "messages is a list of dicts, each with role and content"
- Every variable, every branch, every loop must be traceable
- If this layer modifies a previous layer's pseudocode, show the FULL updated version with the new parts marked

#### Section B: "Now Run This Scenario" (concrete walkthrough)

Walk through ONE specific scenario step by step, showing the exact data at each point.

Rules:
- Use the SAME scenario across all layers (same user question, same tools, same alerts)
- Show the actual content of variables: `messages = [{role: "system", content: "You are..."}, {role: "user", content: "Why is my nginx pod crashing?"}]`
- When the system makes a decision (branch), explain which branch is taken and why
- End with: "This works. But what happens if...?" → reveals the flaw

#### Section C: "What Breaks" (the flaw that motivates the next layer)

Present a concrete situation where this layer's system fails. The user should go "oh right, that's a problem" before reading the next layer.

Rules:
- Be specific: "LLM returns tool_calls for a tool named 'bash' with command 'rm -rf /'. The system executes it immediately." Not: "security could be an issue."
- This section is 2-3 sentences max. The flaw should be obvious.
- The last layer's "What Breaks" section covers known limitations / things the project chose NOT to solve.

### Phase 4: Write the Final Chapter — Full Scenario Walkthrough

After all layers, write ONE chapter that walks through the complete scenario with ALL layers active. This is the "integration test" — the user's mental model should be able to follow every step.

This chapter should include:
- The complete data flow from user input to final output
- Every branch point and which branch is taken
- Every data structure at every stage
- What happens at error/edge cases

The user should be able to close their eyes and replay this chapter from memory.

## Writing Rules

### 语言

- 所有输出文档必须使用中文撰写
- 伪代码中的注释使用中文
- 技术术语首次出现时，在中文解释后括号标注英文原文，例如："上下文窗口（Context Window，即 LLM 单次请求能处理的最大文本量）"
- 数据结构中的字段名（如 role、content）保持英文原样，解释用中文

### For Users with Limited Experience

- Define every technical term on first use. Not in a glossary — inline, where it appears.
- "Context window" → "Context window (the maximum amount of text the LLM can see at once — like its short-term memory)"
- Use analogies anchored in universal experience, not in other technical concepts
- Never say "as you know" or "obviously"

### Pseudocode Style

```
// Use plain English for operations
send messages to LLM, get back response
if response contains tool_calls:
    for each tool_call in response.tool_calls:
        result = execute tool_call.name with tool_call.arguments
        append result to messages
```

Not:

```python
response = self.llm.completion(messages=parse_messages_tags(messages), tools=tools, tool_choice=tool_choice)
```

The second version requires knowing Python, OpenAI API conventions, and the codebase's naming. The first version requires knowing how to read.

### Data Structure Style

Show them as concrete examples, not type definitions:

```
messages = [
    { role: "system", content: "You are a troubleshooting assistant..." },
    { role: "user",   content: "Why is my nginx pod crashing?" },
    { role: "assistant", content: null, tool_calls: [
        { name: "kubectl_get_pods", arguments: { namespace: "default" } }
    ]},
    { role: "tool", content: "NAME   READY  STATUS           RESTARTS\nnginx  0/1    CrashLoopBackOff 5" }
]
```

Not:

```
messages: List[Dict[str, Any]]
```

### Scenario Rules

- Pick ONE scenario that exercises the most code paths
- Good scenario: user asks a question → LLM calls a tool → tool needs approval → user approves → LLM calls another tool → LLM gives final answer
- The scenario must be realistic and domain-appropriate (for a K8s tool, use a real K8s problem)
- Re-use the SAME scenario in every layer, adding detail each time

### Document Length

- Each layer: 500-1000 words (not counting pseudocode)
- Final walkthrough: 1000-2000 words
- Total: 5000-10000 words
- If a layer exceeds 1000 words of prose, the concept isn't atomic enough — split it

## Layer Ordering Heuristic

Most codebases follow this pattern. Adapt as needed:

```
1. Core loop / main abstraction (the 10-line version)
2. How inputs are represented (data model / schema)
3. How extensions plug in (plugin / module system)
4. How dangerous operations are controlled (auth / approval / validation)
5. How resource limits are managed (memory / tokens / rate limits)
6. How the system connects to the outside world (I/O, APIs, UI)
7. How quality is ensured (testing / monitoring)
```

Not all projects need all layers. Some need layers not listed here. Use judgment.

## Anti-Patterns

### Information Dump
"The project has 5 subsystems: A, B, C, D, E. A does X. B does Y..."
**Why bad:** Reader has no mental model to hang these facts on.

### Architecture Astronaut
"The ToolExecutor implements the Strategy pattern with a Factory Method..."
**Why bad:** Pattern names don't help someone with 1 year of experience.

### Code Tour
"In file X line 42, we see... then in file Y line 87..."
**Why bad:** Reader can't build a mental model from scattered file references.

### Conclusion First
"The approval mechanism works by yielding APPROVAL_REQUIRED from the generator."
**Why bad:** Reader hasn't discovered WHY approval is needed yet. The answer arrives before the question.

### Skipping "What Breaks"
Jumping from one concept to the next without showing why the previous version is insufficient.
**Why bad:** Without the flaw, the next layer feels like arbitrary complexity instead of necessary evolution.

## Output Format

Write output to a directory. Suggested structure:

```
./{project-name}-guide/
    00-overview.md          # One-paragraph summary + what scenario we'll follow
    01-core-loop.md         # Layer 1
    02-{concept}.md         # Layer 2
    ...
    NN-full-walkthrough.md  # Final chapter
```

Or a single file if the project is small enough. Use judgment.

## Quick Reference

| Phase | What You Do | Output |
|-------|------------|--------|
| Research | Read all key files, identify core abstractions | Notes (not shown to user) |
| Plan | Decide layers, order, scenario | Layer plan (not shown to user) |
| Write | Write all layers + final walkthrough | Document files |
| Deliver | Tell user where to read | File paths |

## Red Flags — You're Doing It Wrong

- You started writing before finishing research → STOP, finish research
- A layer introduces 2+ new concepts → split it
- You're explaining a concept without showing pseudocode → add pseudocode
- The "What Breaks" section is abstract ("security issues") → make it concrete
- You're using real code syntax instead of pseudocode → simplify
- The scenario changes between layers → keep the same scenario
- You're telling the user the answer before showing the problem → restructure
