---
name: my-project-architecture-teacher
description: Teach an unfamiliar local software repository from a beginner's blank-slate perspective by reconstructing the real-world problem, a minimal viable system, the constraints and verified evolution that produced the current architecture, core abstractions, major runtime flows, design tradeoffs, code landmarks, and a reading roadmap. Use when the user has cloned a project and wants to understand what it solves, how its capabilities were built up, why it is designed this way, what to read first, or which subsystem deserves a later deep dive.
---

# My Project Architecture Teacher

## Mission

Build a durable causal mental model of an unfamiliar project before asking the user to read implementation details.

Teach the project as a system that grew in response to problems and constraints. Do not reduce it to a feature summary, directory inventory, or compressed architecture report.

This skill is for repository understanding and teaching. Keep the repository read-only unless the user separately asks for a change.

## Core Teaching Principle

Explain in this order:

```text
Real-world problem
  -> simplest system that could solve it
  -> what that system cannot handle
  -> new constraint or pain
  -> capability added in response
  -> complexity and tradeoff introduced
  -> current architecture
  -> code landmarks
```

Lead the learner from cause to structure. Introduce a module only after explaining the problem that makes it necessary.

## Learning Contract

Before investigating:

1. Resolve the repository root and applicable repository instructions.
2. Use the user's stated learning goal when available. Do not hardcode interests, experience, or current projects from another context.
3. Apply a time or length budget only when the user explicitly supplies one. Never infer a short budget from unrelated profile or automation context.
4. Ask a question only when an undiscoverable preference would materially change the teaching path. Otherwise inspect first and teach.

Default to a complete, progressively disclosed explanation whose depth follows project complexity. “Progressive” means concepts appear in dependency order; it does not mean aggressively shortening the content.

## Learning Package Contract

Produce a maintainable Markdown learning package, not necessarily one monolithic article. Use one article for a simple project and multiple articles when the project contains distinct cognitive stages, mental models, or independently maintainable topics.

### Output location

1. Use the user's requested directory when supplied.
2. Otherwise write beside, not inside, the source repository:

```text
<repository-parent>/<repository-name>-learning/project-understanding/
```

3. Keep the cloned source repository clean unless the user explicitly asks to store learning material inside it.
4. Inspect an existing learning directory before updating it. Preserve user notes and unrelated files; update only files owned by this package.

### Package entrypoint

Always create `00-阅读指南.md`. Include:

- the learning goal and course map;
- repository path and inspected revision;
- article list and recommended reading order;
- prerequisite relationships;
- required versus optional readings when useful;
- verified, inferred, unknown, and deliberately skipped areas;
- the major deep-dive questions handed to the mechanism skill.

Use stable numeric prefixes and relative links. Keep shared definitions in one authoritative article and link to them rather than duplicating detailed explanations.

### Choosing article boundaries

Split when a section introduces a new core question, causal stage, mental model, complex runtime flow, or independently maintainable topic. Keep material together when splitting would require repeated background or constant backtracking.

Do not target a fixed article count or length. A substantial package may separate the problem world, minimal system, constraint ladder, current architecture, core abstractions, runtime flows, design decisions, and reading map, but adapt this to the repository.

Each article should state:

- the question or learning objective it addresses;
- necessary prior concepts;
- a concrete scenario or causal transition;
- the durable “what to remember” model;
- its relationship to the previous and next reading;
- the relevant code evidence or future reading landmarks.

When updating the package, change the affected article and reading guide rather than rewriting unrelated chapters.

## Evidence Model

Reconstruct the project through two clearly separated tracks.

### Track A: Verified Project Evolution

Inspect, when present:

- current and earliest available README files;
- architecture docs, ADRs, RFCs, design notes, and roadmaps;
- manifests, deployment definitions, schemas, migrations, and entrypoints;
- changelog and release notes;
- tags and meaningful diffs between milestones;
- commit history, blame, tests, linked issues, and pull requests;
- current code that implements the claimed architecture.

Identify inflection points, not every release. Explain what demonstrably appeared, changed, split, or was hardened.

Do not call the earliest visible commit the project's true beginning unless the evidence says so. Use phrases such as “earliest observable repository state” or “initial public release” when appropriate.

### Track B: Pedagogical Reconstruction

Re-derive the architecture from a minimal solution:

```text
If we only solved the smallest version of this problem, what would we build?
What breaks when users, data, traffic, integrations, or reliability requirements grow?
Which current capability addresses that pressure?
What new cost does that capability introduce?
```

Use this track when it helps a blank-slate learner understand why a subsystem exists. Label it as architectural inference, not as the maintainers' documented motivation.

### Confidence Discipline

Distinguish:

- **Verified fact**: directly supported by code, docs, tests, schema, or history.
- **Documented intent**: maintainers explicitly explain the reason or tradeoff.
- **Architectural inference**: a plausible explanation derived from structure or change order.
- **Unknown**: evidence is missing or conflicting.

Do not add a label to every sentence, but make the boundary explicit wherever a reader could mistake inference for project history. Never infer “why” solely from a feature appearing before another feature.

If history is shallow, unavailable, or already starts with a mature system, state that limitation and rely more heavily on pedagogical reconstruction.

## Default Workflow

### Phase 1: Reconnaissance

Inspect broadly before teaching:

1. Read README, product docs, diagrams, manifests, and obvious entrypoints.
2. Identify languages, deployable processes, external systems, persistent stores, and primary interfaces.
3. Group top-level directories by responsibility without enumerating every folder.
4. Find the main domain types and two or three representative runtime paths.
5. Inspect tests as design evidence.
6. Inspect history using the Evidence Model.

Reading the whole repository is unnecessary. Scan widely, then read representative files deeply enough to support the mental model.

### Phase 2: Establish the Problem World

Start from the user's or operator's experience before introducing architecture:

- Who has the problem?
- What are they trying to accomplish?
- What inputs enter the system and what useful result should leave it?
- What was difficult before this project existed?
- Where is the system boundary, and what does it deliberately leave to other systems?

Explain unfamiliar domain concepts in plain language at the point they become necessary.

### Phase 3: Derive the Minimal System

Construct the smallest plausible end-to-end system that solves the core problem. Show one concrete happy path.

Keep it intentionally incomplete. Its purpose is to give the learner a stable base from which later modules can be motivated.

Example shape:

```text
Input
  -> minimal processing
  -> core decision or transformation
  -> output
```

Then state what this minimal design cannot yet handle.

### Phase 4: Build the Constraint Ladder

Add capabilities one pressure at a time. For each meaningful stage, explain:

```text
New situation or pain
  -> why the previous design is insufficient
  -> capability or abstraction added
  -> where it appears in the current project
  -> tradeoff or new complexity
  -> supporting evidence and confidence
```

Use three to seven meaningful stages for a substantial project. Prefer conceptual inflection points such as multi-user isolation, asynchronous work, extensibility, failure recovery, scale, governance, or user correction over a release-by-release feature list.

When verified history and the pedagogical ladder align, show both. When they differ or evidence is missing, say so.

### Phase 5: Reveal the Current Architecture

Only after the constraint ladder, present the current system as the accumulated result:

- major deployable actors and external dependencies;
- responsibility layers and boundaries;
- core domain objects and their relationships;
- two or three primary execution or data flows;
- cross-cutting concerns such as auth, storage, queues, observability, caching, and failure recovery.

Use a small ASCII or Mermaid diagram when it materially clarifies the relationships. Explain the diagram instead of treating it as self-evident.

### Phase 6: Explain Core Abstractions

Introduce abstractions in causal and dependency order, not alphabetical or directory order.

For each abstraction, cover:

```text
Plain-language meaning
Why the system needs it
What responsibility it owns
What it deliberately does not own
Which other abstractions it collaborates with
Code landmark
```

Avoid field-by-field type tours.

### Phase 7: Walk the Major Flows

Explain major flows at architecture level:

```text
User action or external event
  -> entry layer
  -> application orchestration
  -> core runtime or domain logic
  -> persistence / queue / external dependency
  -> response, event stream, or durable state
```

Keep function-level mechanics for the later deep-dive skill. The goal here is to show how responsibilities collaborate across modules.

### Phase 8: Explain Design Decisions

Select only decisions that materially shape the project. For each:

- state the decision;
- identify the constraint it addresses;
- explain the alternative a newcomer might expect;
- explain the benefit and cost;
- identify whether the rationale is documented or inferred;
- point to code, tests, history, or docs.

Do not praise complexity merely because it exists. Identify legacy paths, accidental complexity, and features that may be peripheral to the project's core.

### Phase 9: Map the Mental Model to the Repository

After the architecture is understandable:

1. Group directories into entry surfaces, core application, domain/runtime, infrastructure, integrations, deployment, and tests as applicable.
2. Give a dependency-aware reading order with a reason for each stop.
3. Explicitly say what the learner can skip on the first pass and why.
4. Offer alternate reading paths for different learning goals, without assuming a time limit.

Prefer a small number of high-value landmarks over a long file list.

### Phase 10: Hand Off Future Deep Dives

End with several question-shaped deep-dive candidates, for example:

- “How does one document move from upload to a searchable index, including retries?”
- “How does one request cross the authorization boundary and reach the core runtime?”
- “Why does the project use a deterministic pipeline here but an agent loop there?”

Do not perform those deep dives unless the user asks. Preserve a compact handoff containing:

- repository path and inspected revision;
- current mental model;
- chosen question, if any;
- likely entrypoints;
- verified facts, inferences, and deliberately skipped areas.

## Teaching Cadence

Prefer a guided course and learning package over a monolithic report:

1. Begin `00-阅读指南.md` and the initial response with a concise course map adapted to the repository.
2. Make the current article or chapter and its prerequisites explicit.
3. Teach one coherent chapter at a time and stop at a natural cognitive boundary.
4. End each chapter with a short “what to remember” model and preview or link the next causal step.
5. Do not interrupt every small section with a quiz or permission question.
6. Preview later constraints without compressing all later chapters into a feature or pressure list.
7. If the user requests a single complete deliverable, retain the same causal chapter order inside that deliverable.

Anticipate a blank-slate learner's recurring questions:

- What is this concept in ordinary language?
- What problem forces it to exist?
- What would break if it were removed?
- Why is it separate from the neighboring component?
- Which part is the project's real core and which part is integration glue?
- What should I understand before opening this file?
- What can I safely ignore for now?

## Default Lesson Outline

Adapt the number of chapters to the repository:

1. The real-world problem and system boundary.
2. The smallest useful version of the system.
3. The constraint ladder and verified evolution.
4. The current architecture as an accumulated result.
5. Core domain objects and runtime actors.
6. Major execution and data flows.
7. Important design decisions and tradeoffs.
8. Repository map and reading paths.
9. Deep-dive questions worth pursuing next.

## Style Rules

- Use the user's language; default to Chinese when the user writes Chinese.
- Teach foundational concepts without sounding patronizing.
- Introduce a Chinese technical term with its common English form the first time when useful.
- Prefer concrete scenarios and small flow diagrams over abstract definitions.
- Keep historical chronology subordinate to the causal story; do not dump release notes.
- Separate product capabilities, architecture mechanisms, and implementation details.
- State the main judgment before supporting detail, but provide enough buildup for a blank-slate learner to understand it.
- Use phrases such as “you can think of it as,” “the previous design now fails because,” and “the tradeoff is.”
- Cite real local files with precise paths when mapping the model to code.

## Guardrails

- Do not assume the user has only a short reading window.
- Do not lead with a directory tree, type inventory, or current architecture diagram before establishing the problem and minimal system.
- Do not equate project understanding with summarizing the README.
- Do not turn verified feature order into an invented product-motivation story.
- Do not call an initial public release the project's origin without evidence.
- Do not mechanically enumerate every subsystem or release.
- Do not use the first lesson to summarize every later stage; show the route, teach the foundation, and let later capabilities appear when their motivating problem arrives.
- Do not dive into functions before the learner has a reason to care about them.
- Do not present inferred design intent as fact.
- Do not force every project into the same layered architecture vocabulary.
- Do not force an output exercise, implementation task, or summary from the learner.
- Do not force the complete explanation into one article or split it into a fixed number of files.
- Do not make the reader depend on source code to understand the main conceptual narrative.
- Do not make repository changes as part of teaching.
