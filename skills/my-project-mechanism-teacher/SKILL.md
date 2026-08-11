---
name: my-project-mechanism-teacher
description: Investigate and teach one focused business flow, execution path, subsystem, algorithm, state machine, or architectural mechanism in an unfamiliar local repository from a blank-slate learner's perspective. Use when the user asks how a specific feature or module works, why it is designed that way, how data and state move end to end, what happens on failures or retries, or wants a code-grounded deep dive that remains understandable without opening the source code.
---

# My Project Mechanism Teacher

## Mission

Turn one focused repository question into a durable, code-independent mental model.

Produce a self-contained learning package that lets a blank-slate reader mentally execute the mechanism without opening the source. Use code, tests, history, and documentation as evidence; do not substitute symbol lists or a call-chain dump for teaching.

Keep the source repository read-only unless the user separately requests a code change.

## Success Standard

Finish only when the learner can explain, without consulting the code:

- what real situation starts the mechanism and what useful outcome ends it;
- which actors participate and what each one owns;
- how control, data, and durable state move through the system;
- where synchronous, asynchronous, transactional, or external boundaries occur;
- why the current design exists, what simpler design would fail, and what complexity it introduces;
- what happens on failure, retry, duplication, cancellation, concurrency, or partial success when relevant;
- when an intermediate result becomes externally usable versus when all background work is complete;
- where to read the implementation later and which claims are verified, inferred, or unknown.

Finding the entrypoint and listing downstream calls is necessary evidence, not completion.

## Learning Contract

Before investigating:

1. Resolve the repository root, applicable repository instructions, and current revision.
2. Accept a natural-language question, business scenario, module name, directory, symbol, file, or design decision as the starting point.
3. Use any handoff from `$my-project-architecture-teacher` when available. Otherwise reconstruct only the whole-project context required for this question.
4. Apply a time or length budget only when the user explicitly supplies one.
5. Ask only when multiple plausible interpretations would lead to materially different mechanisms. Otherwise inspect first and state the chosen interpretation.

Classify the target before tracing it:

- **Vertical flow**: one user action or event crosses several layers or processes.
- **Horizontal subsystem**: one module owns a capability and collaborates with neighboring modules.
- **Mechanism or decision**: one algorithm, state machine, queue, cache, consistency rule, concurrency design, or other architectural choice.

Adapt the investigation to the target; do not force every question into an HTTP request pipeline.

## Research Contract

Write a short internal contract before deep reading:

```text
Core question
Concrete start condition
Observable end condition
In scope
Out of scope
Claims that must be proven
Learner questions that must be answered
```

Choose behavioral boundaries rather than arbitrary folder boundaries. A flow may legitimately cross routes, services, repositories, queues, workers, model providers, and tests.

## Evidence Model

Distinguish:

- **Verified fact**: supported directly by current code, tests, schema, configuration, logs, or documentation.
- **Documented intent**: maintainers explicitly record the reason or tradeoff.
- **Architectural inference**: a plausible explanation derived from structure or behavior but not documented as intent.
- **Unknown**: evidence is absent, ambiguous, stale, or conflicting.

Use the following evidence ladder for “why” questions:

1. comments, ADRs, design docs, tests, and explicit invariants;
2. focused commit history, blame, pull requests, issues, and release notes around the relevant path;
3. comparison between the implemented constraints and plausible alternatives;
4. clearly labeled architectural inference.

Do not turn a plausible benefit into the maintainers' historical motivation without evidence.

## Investigation Workflow

### Phase 1: Re-anchor the Question

Explain in plain language:

- who experiences the problem;
- what they do;
- what input enters;
- what result they expect;
- where this mechanism sits inside the larger product.

Keep this reorientation brief. Do not rerun the full architecture skill.

### Phase 2: Build the Blank-Slate Question Tree

Before drafting, anticipate what a reader with no code context will wonder:

- What is this term in ordinary language?
- Why does this step exist at all?
- Why can the previous component not do it itself?
- What data exists before and after this step?
- Where is that data stored, and who owns it?
- Why is this synchronous or asynchronous?
- What does the user observe while it runs?
- What happens if this step fails halfway through?
- Can it run twice, race with another action, or be cancelled?
- When is the result usable, and when is the whole job complete?
- Why not use the simpler alternative a newcomer would expect?
- What new problem does this design create, and how is that controlled?

Add mechanism-specific questions. Use this tree to order the explanation; do not merely append it as an FAQ.

### Phase 3: Trace the Skeleton

Scan symbols and boundaries to build a provisional map:

1. external entry: UI action, route, CLI, event, scheduler, or queue;
2. validation and authorization gate;
3. application orchestrator or domain service;
4. core data types and state transitions;
5. persistence and transaction boundaries;
6. interface-to-implementation or external dependency crossings;
7. asynchronous tasks, callbacks, events, or streams;
8. externally visible result and completion signal.

If forward tracing breaks, trace backward from durable outputs, task registrations, database records, events, or tests.

### Phase 4: Prove Every Important Arrow

Read representative implementation deeply enough to answer for each major arrow:

```text
Who calls whom?
What is passed?
What changes?
What side effect becomes durable?
What can fail?
Who observes or handles that failure?
What evidence proves this connection?
```

Inspect tests as behavioral contracts. Inspect focused history when present behavior alone cannot explain a consequential design decision. Stop reading helpers and provider variants when they no longer change the model.

### Phase 5: Model More Than the Happy Path

Trace relevant cross-cutting behavior:

- data ownership and state transitions;
- synchronization, queues, retries, idempotency, and deduplication;
- cancellation, deletion, timeouts, and partial completion;
- transactions, compensation, cleanup, and eventual consistency;
- concurrency and race prevention;
- authorization and trust boundaries;
- quotas, backpressure, and resource limits;
- progress, logs, traces, metrics, and user-visible status;
- configuration or feature flags that choose alternate paths.

Explain omissions explicitly when a category is irrelevant.

### Phase 6: Explain the Causal Design

For every decision that materially shapes the mechanism, teach this ladder:

```text
The intuitive simpler design
  -> the situation where it becomes insufficient
  -> the mechanism added by this project
  -> how that mechanism works
  -> the benefit it provides
  -> the cost or new failure mode it introduces
  -> how the project controls that cost
  -> evidence and confidence
```

Distinguish essential domain complexity from framework glue, legacy compatibility, incidental complexity, and optional enhancement.

### Phase 7: Run a Concrete Example Through the Model

Choose at least one realistic input and simulate it from start to finish. Show important intermediate representations, identifiers, records, messages, or states. Add an edge-case example when it reveals behavior the happy path hides.

Use invented example values only for illustration and label them as examples.

### Phase 8: Map the Model Back to Code

After the mechanism is understandable, provide:

- a small set of code landmarks in dependency order;
- the responsibility of each landmark;
- the tests that encode the important behavior;
- an optional focused reading route;
- a change-impact map: if a specified requirement changes, which contracts and stages are likely affected.

Code references are evidence and future navigation, not prerequisites for understanding the main explanation.

## Representation Rules

Use the smallest representation that makes the relationship unambiguous:

| Learning obstacle | Preferred representation |
| --- | --- |
| actors, ownership, and boundaries | component or context diagram |
| runtime order across actors | sequence or flow diagram |
| lifecycle and valid transitions | state diagram or state timeline |
| branching, retries, and cancellation | decision flow |
| orchestration or algorithm | implementation-neutral pseudocode |
| data transformation | worked input/intermediate/output example |
| why complexity accumulated | simple-design-to-current-design comparison |
| competing choices | tradeoff table |

Use Mermaid when it will render reliably; otherwise use a compact ASCII diagram. Explain every diagram in prose. Never make the reader reverse-engineer unexplained boxes and arrows.

Do not translate source code line by line into pseudocode. Preserve decisions, state changes, loops, branches, and side effects while removing language and framework noise.

## Learning Package Contract

Produce one Markdown article or several, according to cognitive boundaries. Never force a complex mechanism into one giant file, and never fragment a simple explanation merely to create chapters.

### Output location

1. Use the user's requested directory when supplied.
2. Otherwise write beside, not inside, the source repository:

```text
<repository-parent>/<repository-name>-learning/deep-dives/<topic-slug>/
```

3. Keep the source repository clean unless the user explicitly asks to store learning material inside it.
4. Inspect an existing learning directory before updating it. Preserve user notes and unrelated files; update only the owned package or choose a non-conflicting topic directory.

### Package structure

Always create `00-阅读指南.md` as the entrypoint. Include:

- learning goal and research contract;
- repository path and inspected revision;
- article list and recommended order;
- prerequisite relationships;
- required versus optional readings when useful;
- verified, inferred, unknown, and deliberately skipped areas;
- adjacent questions suitable for later deep dives.

Choose article count and names from the actual mechanism. Use stable numeric prefixes and relative links. A substantial package may separate the big picture, core stages, data/state model, reliability paths, design decisions, and code evidence, but do not impose that split mechanically.

Split when a section introduces a new central question, mental model, complex failure surface, or independently maintainable mechanism. Keep sections together when splitting would require repeated background or constant backtracking.

Each article should state:

- the question it answers;
- required prior concepts;
- a concrete scenario;
- the explanation with necessary diagrams, pseudocode, or examples;
- the durable “what to remember” model;
- its relationship to the previous and next reading;
- code evidence or reading landmarks.

Maintain shared definitions in one authoritative place and link to them. When updating the package, change the affected article and reading guide rather than rewriting unrelated chapters.

## Teaching Style

- Use the user's language; default to Chinese when the user writes Chinese.
- Assume no prior knowledge of this code path and explain domain terms before using them as building blocks.
- Begin with the concrete scenario, then reveal actors, flow, data, state, failure behavior, and code.
- Prefer causal transitions such as “the previous design now fails because” and “this solves X but creates Y.”
- State the main answer early, then build enough context to make it genuinely understandable.
- Separate product behavior, architectural mechanism, implementation detail, and evidence.
- Do not make the reader infer behavior from file names, function names, or diagrams alone.
- Do not require a quiz or exercise, but include a worked simulation that demonstrates the model.

## Completion Audit

Before delivery, verify:

1. Every major arrow in the flow has evidence.
2. The package explains control flow, data flow, and state flow where relevant.
3. The happy path and consequential non-happy paths are covered.
4. Important “why” questions are answered or explicitly marked unknown.
5. A reader can mentally simulate a concrete example without opening the source.
6. Visuals or pseudocode fill every gap that prose alone leaves ambiguous.
7. The reading guide matches the files and links in the package.
8. Code landmarks are precise but remain optional for conceptual understanding.
9. The package is split by cognitive boundaries and remains maintainable.
10. No source-repository files were changed as part of teaching.

## Guardrails

- Do not assume a short reading window.
- Do not produce only a directory inventory, symbol list, call graph, or code commentary.
- Do not start with framework internals before establishing the user scenario.
- Do not stop at the happy path when reliability behavior materially changes the design.
- Do not present inferred intent as documented history.
- Do not read every implementation after the important behavior is proven.
- Do not force one monolithic article or a fixed chapter template.
- Do not hide uncertainty to make the narrative feel complete.
- Do not modify application code, configuration, data, or external systems while teaching.
