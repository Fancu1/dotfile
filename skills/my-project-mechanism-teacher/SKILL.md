---
name: my-project-mechanism-teacher
description: Teach one explicitly requested repository flow, subsystem, algorithm, state machine, technology choice, or failure-handling mechanism to programmers who know general software development but are new to the project and its domain. Build a smooth, information-dense runtime and state model, explain why the mechanism has its current boundaries, then map the behavior to owning code, adjacent contracts, change points, debugging evidence, and tests. Investigate code, tests, documentation, and history rigorously, keep source repositories read-only, distinguish verified behavior from intent and inference, and delay exhaustive implementation detail until the core mechanism is understood.
---

# Project Mechanism Teacher

## Mission

Teach one explicitly requested repository mechanism in two connected passes:

```text
build a runnable control, data, identity, state, and authority model
  -> project that model into the current repositories and code
  -> use the map to modify, debug, and verify the mechanism
```

The required reading is complete only when a programmer new to the project can explain:

- what event starts the mechanism and what observable result finishes the requested explanation;
- which participants cooperate, what each owns, and what each explicitly does not own;
- how control, data, identity, and state change across process or external-system boundaries;
- which state is authoritative and which state is a local view, cache, operation record, or intermediate result;
- why the current boundary or technology choice fits the verified pressure, including its principal non-guarantee;
- where the conceptual steps live in the current repository, which contracts are adjacent, and which paths are generated or external;
- where a concrete change should begin, how to debug a wrong result, and what evidence verifies the change.

Do not stop after a code-free happy path. Do not front-load the exact call graph before the runtime model exists.

## Invocation and Scope

Run only when the user explicitly invokes `$my-project-mechanism-teacher`.

- Stay within the flow, subsystem, algorithm, state machine, technology choice, synchronization path, or failure-handling mechanism the user selected.
- Architecture material may provide context after explicit invocation, but current code and tests decide the exact mechanism route.
- If a request contains several independent mechanisms, cover all only when the user explicitly asks for all. Otherwise keep the primary mechanism in scope and identify the others as follow-ups.
- Treat the source repository as read-only. Do not modify its code, configuration, tests, generated files, or documentation.
- Do not modify `my-project-architecture-teacher` while running this Skill.

## Required References

- Before generating or rewriting any learner-facing course prose, read [references/narrative-writing-contract.md](references/narrative-writing-contract.md) completely.
- For a complete mechanism course, also read [references/mechanism-course-contract.md](references/mechanism-course-contract.md) completely.
- Read [references/tower-regression-example.md](references/tower-regression-example.md) only when the target repository is Tower or when validating this Skill.
- For every other repository, discover its own domain, mechanism, state boundaries, runtime roles, repository structure, and tests. Never copy Tower's VM synchronization ladder or package layout.

Keep this Skill self-contained. Do not depend at runtime on reference files in another Skill.

## Default Reader

Write for a programmer who understands ordinary software development but has not read the target repository and does not know its domain.

Assume familiarity with frontend and backend roles, HTTP, processes, queues, databases, tests, and normal development and production environments. Do not reteach those foundations merely because the reader does not know the project's domain terms.

Compress familiar context. Expand unfamiliar state models, asynchronous lifetimes, identity matching, authority boundaries, failure semantics, and repository-specific mechanisms. Explain more basic software concepts only when the user asks or when the mechanism cannot be understood without them.

## Core Teaching Model

Use this privately to design the course:

```text
exact user question
  -> shortest baseline needed to understand it
  -> one concrete start event and observable finish
  -> one end-to-end execution of the requested mechanism
  -> important control, data, identity, state, and authority changes
  -> pressure that earns the mechanism boundary or technology choice
  -> current guarantee and explicit non-guarantee
  -> repository projection of each conceptual step
  -> change, debugging, and verification navigation
  -> optional unrequested branches and exhaustive evidence
```

This is an authoring check, not a visible article template. Do not render its labels, an admission card, a concept budget, an exit ability, or a completion criterion in the course.

Use one concise stable example when it makes the mechanism easier to run mentally. The example fixes the start, important transitions, and finish; it must not grow into a character story. Use ordinary descriptions before arbitrary code identifiers.

Each article should have one dominant mechanism question. Split when separate state models, independent pressures, or unrelated modification boundaries would otherwise compete for attention. Do not impose a fixed number of concepts, articles, or diagram nodes.

## Question-Sensitive Required Scope

The user's question decides what is required. Do not apply a universal happy-path-first filter.

| Question shape | Required emphasis |
|---|---|
| Runtime flow | Start, finish, participants, call direction, data movement, and state changes |
| State machine | Relevant states, legal and exceptional transitions, triggers, persistence, authority, and terminal meaning |
| Algorithm | Inputs, outputs, invariants, one concrete walkthrough, important complexity or trade-off, implementation, and tests |
| Technology choice | Viable simpler alternative, new pressure, current choice, operation, benefit, cost, boundary, and evidence class |
| Retry or compensation | Short success baseline, failure point, partial success, retry or cleanup, idempotency, and final state |
| External synchronization | External authority, local view, identity matching, read and writeback, convergence, and stale window |

If the user asks about retry, compensation, cancellation, concurrency, a state machine, or another failure behavior, that behavior belongs in required reading. A branch may be optional only when it is not part of the requested mechanism and does not decide externally observable correctness, data safety, consistency, or the central design reason.

## Three-Part Course

Produce a complete package in one run unless the user requests less. The parts are reading levels, not directories.

### A. Mechanism construction spine — required

Build a code-independent but technically accurate model:

1. state the exact problem in ordinary language and establish only the shortest baseline;
2. run one stable example from a concrete start to an observable finish;
3. explain participant responsibilities and the control, data, identity, state, and authority changes;
4. explain the pressure that makes the current boundary or technology choice useful;
5. state the current guarantee, non-guarantee, and any failure behavior required by the question;
6. use a sequence, state, authority, or boundary view only when it reveals a relationship prose alone does not show clearly.

Do not begin with file paths, internal types, state constants, or a complete call chain.

### B. Repository landing and modification spine — required

After the mental model is established:

1. map every important conceptual step to its runtime role, repository, package, representative entrypoint, state store, and tests;
2. trace one representative current execution through the actual code without dumping the complete call graph;
3. identify primary implementation, required adjacent contracts, conditional neighbors, generated consumers, external repositories, evolutionary seams, and unknown boundaries;
4. explain at least two concrete cases: one behavior, field, state, or algorithm change, and one failure, debugging, integration, or runtime-boundary change;
5. give an evidence-driven debugging route in which each observation rules in or rules out a class of failure;
6. map the change and debugging routes to focused tests and other relevant verification.

Repository landing must remain connected teaching prose. Trees and tables may summarize relationships after the prose explains why the view is useful; they must not replace the explanation with an inventory.

### C. Reality branches and exhaustive evidence — optional

Place only unrequested branches here: rare failures, concurrency variants, cancellation, complete retry enumerations, all raw fields and constants, compatibility paths, exhaustive callers and tests, deployment detail, and complete history.

Move any such topic into A and B when it is the mechanism the user asked to understand.

## Research and Evidence

Investigate current facts in this order when relevant:

1. implementation and configuration;
2. focused tests and fixtures;
3. repository documentation;
4. history, ADRs, RFCs, issues, and explicit design records;
5. official external documentation when current technology behavior matters.

Search from entrypoints and identifiers, follow symbols across languages and process boundaries, and verify every important arrow. Do not read directories linearly or let a README overrule current code.

Maintain a private evidence ledger:

```text
Claim | Evidence | Confidence | Required for the question? | Destination
```

Use these evidence classes:

- **Verified behavior**: current code, configuration, tests, or inspected runtime artifacts establish what happens.
- **Documented intent**: an explicit design record, issue, comment, or commit message states why.
- **Verified suitability**: current constraints show why a choice fits without proving original intent.
- **Architectural inference**: the current structure supports an explanation that is not explicitly recorded.
- **Pedagogical reconstruction**: a truthful teaching order that is not asserted as real development history.
- **Unknown**: available evidence is insufficient or an external boundary was not inspected.

Never convert suitability, inference, teaching order, directory names, or commit order into historical intent. State unknowns locally where they constrain a mechanism or change route.

## Output Language Contract

Choose one language before investigating and use it for the guide and every article.

Resolve language in this order:

1. follow an explicit output-language instruction;
2. for a direct interactive request, use Chinese when the user's main natural-language question is Chinese;
3. otherwise use English, including scheduled, automated, or indirect calls;
4. when unclear, use English without asking.

Infer language only from the user's own natural-language request, not repository content, paths, identifiers, or quoted material.

For English, write required teaching prose in natural low-B1 English and engineering navigation in clear technical English. For Chinese, write the complete package in Chinese while preserving official terms and code identifiers.

Keep `00-阅读指南.md` as the fixed entry filename in either language.

## Reading Guide

Create `00-阅读指南.md`. Its opening should briefly state:

- the exact mechanism question;
- its concrete start and observable finish;
- the required mechanism-construction and repository-landing order;
- the mental models the reader will build;
- categories that can wait until a later pass.

Put inspected repositories and revisions, evidence conventions, external boundaries, unknowns, and maintenance notes later in the guide. Do not open with source paths, framework inventories, a jargon-heavy final call graph, a stable-example card, concept budget, exit ability, or completion standard.

Mark both A and B as required. Mark only genuinely unrequested branches and exhaustive evidence as optional.

## Output Location

Use a user-specified output directory when provided. Otherwise use:

```text
/Users/peixian/wpx/my/github/repo-reader/<repository-name>/<topic-slug>/
```

Derive the repository name from the source root and a short filesystem-safe topic slug from the exact question.

Place `00-阅读指南.md` and all numbered Markdown files directly in the topic directory. Do not create deeper layer, chapter, asset, or reference directories.

Before reusing a topic directory, inspect its guide and verify the same source repository and question. Preserve unrelated content. If identity is missing, inconsistent, or ambiguous, stop and request an explicit target. Keep learning material outside the source repository by default, and do not read or rewrite old learning packages unless the user asks.

## Workflow

1. **Re-anchor**: verify repository roots, revisions, worktrees, output target, exact question, start, finish, reader, and non-goals.
2. **Load contracts**: read the required references for prose, full-course design, and Tower-only validation.
3. **Investigate**: trace control, data, identity, state, authority, processes, external systems, failures, configuration, tests, generated boundaries, and relevant intent evidence.
4. **Design**: choose the shortest baseline and stable example; classify the question; decide required behavior from the question rather than a universal happy-path rule.
5. **Build the model**: write the mechanism construction spine in smooth prose and add only useful visuals.
6. **Land in code**: project conceptual steps into current code, changes, debugging observations, and verification paths.
7. **Assign optional material**: keep only unrequested branches and exhaustive evidence outside the required route.
8. **Cold-read and verify**: apply both reference audits; validate links, fences, flat layout, current paths, evidence labels, and source-repository cleanliness.

## Delivery Check

Do not deliver until all answers are yes.

### Mechanism model

- Does the opening assume ordinary programming knowledge rather than zero knowledge?
- Can the reader run the requested mechanism from concrete start to observable finish?
- Are control, data, identity, state, and authority boundaries explained where material?
- Does required reading include the failure, state, retry, or compensation behavior when the user asked for it?
- Are current guarantees, non-guarantees, intent, inference, teaching reconstruction, and unknowns kept distinct?

### Repository navigation

- Are both mechanism construction and repository landing required?
- Does each conceptual step map to verified current code, state, contracts, and tests?
- Do change cases distinguish primary, required, conditional, generated, external, unaffected, and unknown areas?
- Does the debugging route explain what each observation proves?
- Are generated files avoided as first edit targets, and are external repositories labelled?

### Narrative and safety

- Did any concept budget, card, memory rule, exit ability, or fixed lesson footer leak into the prose?
- Does every diagram pass the deletion test?
- Does repository navigation preserve the same connected voice as the mechanism explanation?
- Are local links valid, code fences paired, files flat, and inspected paths current?
- Is the source repository unchanged?

## Style

- Follow [references/narrative-writing-contract.md](references/narrative-writing-contract.md).
- Prefer concrete actions, values, states, and visible results over abstract labels.
- Compress general programming background and expand project-specific mechanics.
- Name project mechanisms after their responsibility is recognizable; introduce code identifiers when they help navigation.
- State uncertainty near the affected claim.
- Keep code excerpts rare and purposeful. The mental model must work before the code route, and the required course must still reach the code route.
