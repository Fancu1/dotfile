---
name: my-project-mechanism-teacher
description: Teach one explicitly requested repository flow, subsystem, algorithm, state machine, technology choice, or architectural mechanism as a beginner-first, story-driven, code-independent Markdown learning package. Use only when the user explicitly invokes this skill to understand how a focused behavior works end to end, why its design or technology choices exist, how data and state change, or which consequential failure boundaries matter. Investigate code, tests, documentation, and history rigorously, but teach through one stable example before exposing full call chains or engineering evidence.
---

# Project Mechanism Teacher

## Mission

Teach one focused mechanism so that a zero-background reader can run it in their head without reading source code.

The required lessons must establish:

- the concrete event that starts the mechanism;
- the useful or observable result that ends the promised explanation;
- the few main participants and their responsibilities;
- the important data or state changes during one normal execution;
- the central reason the mechanism or technology choice is shaped this way.

Investigate the complete engineering truth, but do not put that completeness in the beginner's first reading path.

## Priority: Absorption Before Completeness

These gates override any desire to make required prose comprehensive.

1. **One stable example** runs through the whole package.
2. **Happy path first**: finish one normal execution before branches or evidence.
3. **One question per article**: stop immediately after the promised exit ability.
4. **At most three new durable concepts in each required article.**
5. **At most five meaningful nodes in the first diagram.** Count every unique actor, module, store, queue, state, or named mechanism shown.
6. **Behavior before terminology**: explain what happens in ordinary language, then introduce the project term.
7. **Core precision gate**: a detail stays in required prose only if removing it prevents the reader from answering that article's one question.

Before drafting each required article, create a private binding ledger:

```text
Article question:
Already known:
New concepts: [no more than three]
Can ignore:
Exit ability:
```

After drafting, audit every project-specific name, code-formatted identifier, framework, protocol, library, algorithm, subsystem, infrastructure product, and state field. Each must be already known or consume one ledger slot. Otherwise translate it into ordinary language or move it out of the required article.

Do not claim “three concepts” and then expand them into dependency inventories, code symbols, backend variants, deployment controls, or protocol features. Those facts belong in optional or reference material.

Exact statement ordering, raw fields, retry constants, exhaustive state lists, library inventories, backend-specific visibility caveats, compatibility fallbacks, deployment details, and security configuration normally fail the core precision gate. Preserve them in the package; do not preserve them in the required path.

## Invocation and Scope

Run only when the user explicitly invokes `$my-project-mechanism-teacher`.

- Do not run automatically because an architecture package suggests a deep dive.
- Architecture material may be context only after explicit invocation.
- Do not generate every suggested mechanism.
- Stay within the one mechanism or design question selected by the user.
- If several independent questions appear, teach the primary one and list the others as possible follow-ups unless the user explicitly asks for all.

Do not modify `my-project-architecture-teacher` while running this Skill.

## Success Standard

The required core succeeds when the reader can retell, without source code:

1. start and observable finish;
2. main participants;
3. key data or state changes;
4. central design reason;
5. any distinction between “the requested result is usable” and “all related work is finished.”

Retry, concurrency, cancellation, compensation, partial success, and rare failures enter required prose only if they change:

- externally observable success;
- data safety or consistency; or
- the central design reason.

Otherwise, place them in an optional reality article or engineering reference.

## Separate Investigation from Teaching

### Investigation is complete

Privately trace as far as necessary:

- entry, exit, callers, callees, jobs, events, and process boundaries;
- control, data, and state flow;
- persistence, transactions, idempotency, and consistency;
- consequential failures, retry, cancellation, compensation, and partial success;
- configuration, deployment, tests, documentation, and relevant history.

Prove every important arrow internally.

### Teaching is selective

Show only the arrows needed for the reader's current question, in this order:

1. concrete example;
2. one normal execution;
3. minimum state boundary needed to interpret the result;
4. problem pressure and ordinary-language solution;
5. project term or technology name;
6. optional reality branches;
7. exact engineering evidence.

Never copy the call graph, object inventory, failure matrix, or history log into the required outline.

## Research and Evidence

Treat the source repository as read-only. Do not modify its code, configuration, tests, generated files, or documentation.

Investigate current facts in this order when relevant:

1. implementation and configuration;
2. focused tests and fixtures;
3. repository documentation;
4. history or design records;
5. official external documentation when current technology behavior matters.

Use repository search and follow symbols across language and process boundaries. Do not read directories linearly or let a README overrule current code.

Keep a private evidence ledger:

```text
Claim | Evidence | Confidence | Needed in core? | Destination
```

Use these evidence classes:

- **Verified fact**: current code, configuration, test, or runtime artifact.
- **Documented intent**: explicit design record, issue, comment, or commit message.
- **Verified suitability**: current constraints show why a choice fits, without proving original intent.
- **Architectural inference**: plausible but not explicitly recorded.
- **Unknown**: insufficient evidence.

Never present suitability or inference as historical intent.

## Stable Example and Boundary

Choose one realistic, memorable input or identifier before writing, such as one uploaded file, request, job ID, entity, or query. Reuse it throughout.

Define privately:

```text
Reader:
Core question:
Concrete start:
Observable finish:
Design reason to explain:
Non-goals:
Stable example:
```

Start with one complete happy path. If several completion moments exist, state which one satisfies the user's immediate goal. Branch from the same example instead of switching examples.

## Three-Layer Package

Produce the complete package in one run unless the user requests less. Layers are reading levels, not directories.

### 1. Core runtime model — required

Usually one or two articles. This is the only required layer.

- Complete one normal execution from start to observable finish.
- Use only the few participants required for that execution.
- Explain key data or state changes in ordinary language.
- Explain the central design reason needed by the user's question.
- If the question is a technology choice, that choice belongs here.

For a technology-choice core, keep only:

1. the decisive constraint;
2. the simpler alternative and why it becomes insufficient;
3. the current boundary or choice;
4. the primary benefit;
5. the principal cost or control;
6. the evidence boundary.

This causal sequence does not permit six new concepts. Express it using the article's three-concept ledger. Move secondary constraints, dependency examples, deployment mechanisms, protocol capabilities, exhaustive controls, and comparison details to later layers.

### 2. Design and reality branches — optional

Each article handles exactly one relevant pressure:

- one secondary technology choice;
- one consequential failure;
- retry or idempotency;
- cancellation;
- concurrency or ordering;
- partial success or compensation;
- one state boundary that changes external meaning.

Do not add an article merely because a branch exists.

### 3. Engineering evidence — reference

Move exact engineering truth here:

- precise call chain and process boundaries;
- complete relevant state machine;
- transaction and consistency boundaries;
- code, configuration, tests, and fixtures;
- history, evidence classes, and unknowns;
- change-impact and debugging entry points.

Required prose must remain understandable if this layer is skipped.

## Reading Guide

Create `00-阅读指南.md`.

Its first screen contains only:

- exact question;
- stable example;
- required core links;
- the reader's exit ability;
- details safe to ignore on the first pass.

Mark only core runtime articles as required. Mark reality articles as optional and engineering evidence as reference. Put scope, revision, evidence conventions, unknowns, and maintenance notes after the first screen.

Do not begin with source paths, frameworks, state fields, revision metadata, or a complete catalog.

## Teaching Rhythm

Use only the steps an article needs:

1. return to the stable example;
2. state the plain expectation or simple solution;
3. show the observable pressure when one exists;
4. explain the solution in ordinary language;
5. name the project mechanism;
6. state its guarantee and boundary;
7. leave one memory rule;
8. add a clearly skippable evidence pointer if useful.

Do not manufacture a failure for a simple happy-path lesson. Do not define one unknown term with more unknown terms.

## Visuals and Pseudocode

Use a representation only when it removes a real obstacle.

- One visual answers one question.
- Reveal complexity progressively.
- Do not generate diagrams, tables, and pseudocode merely for completeness.
- State diagrams come only after states are explained in prose.
- Pseudocode is only for decisions, loops, state changes, or side effects; never transliterate source.
- Tables are for exact mappings or comparisons, not narrative.

For the first diagram, count unique node IDs in the diagram source. The total must be five or fewer. Group adjacent internal steps under one ordinary-language role rather than hiding extra nodes behind combined labels.

## Output Location

Use a user-specified output directory when provided. Otherwise use:

```text
/Users/peixian/wpx/my/github/repo-reader/<repository-name>/<topic-slug>/
```

Derive the repository name from the source root and a short filesystem-safe topic slug from the core question.

Place `00-阅读指南.md` and all numbered Markdown files directly in the topic directory. Do not create deeper layer, chapter, asset, or reference directories.

Before reusing a topic directory, inspect its guide and verify the same source repository and core question. Preserve unrelated content. If identity is missing, inconsistent, or ambiguous, stop and ask for an explicit target. Do not overwrite a merely similar topic.

Keep learning material outside the source repository by default. Do not read or rewrite old learning packages unless the user explicitly asks.

## Workflow

1. **Re-anchor**: verify repository root, revision, worktree, output target, question, start, finish, reason, and non-goals.
2. **Design learning**: choose stable example; create reader contract, binding concept ledgers, and first-diagram node budget.
3. **Investigate fully**: trace implementation, boundaries, failures, tests, configuration, documentation, and history; maintain evidence ledger.
4. **Filter**: apply the external-semantics/data-safety/design-reason gate; assign every fact to core, optional, reference, or omit.
5. **Draft**: happy path first; one pressure per optional article; exact code last.
6. **Audit core**: enforce concept ledgers and precision gate; count actual unique nodes; remove post-promise details.
7. **Verify**: validate local links, Markdown fences, flat layout, evidence pointers, and source-repository cleanliness.

## Delivery Check

Do not deliver until all answers are yes:

### Reader and layering

- Can a zero-background reader retell one normal execution without code?
- Are start, finish, participants, state/data changes, and central reason clear?
- Does the guide mark only core articles required?
- Does every optional article cover one pressure?
- Are complete calls, states, errors, code, tests, and history outside the required path?

### Absorption audit

- Does each required article answer one question and stop at its exit ability?
- Does its private ledger contain at most three new concepts?
- Did every named technical term pass that ledger?
- Are dependency lists, raw identifiers, backend variants, deployment details, and other precision notes later unless indispensable?
- Does the first diagram have five or fewer unique nodes when counted from its source?
- Does the core still work when all evidence notes are skipped?

### Truth and safety

- Are documented intent, suitability, inference, and unknowns distinct?
- For choices, are constraint, simpler alternative, benefit, cost/control, and evidence clear?
- Are important engineering claims traceable in the reference layer?
- Is the source repository unchanged?
- Are files flat in one correct topic directory?
- Are local links valid and code fences paired?

## Style

- Match the user's language.
- Write as a patient teacher, not a code reviewer or API reference.
- Prefer concrete actions and visible results over abstract nouns.
- Explain why the next detail matters.
- Be precise without front-loading precision the reader cannot yet use.
- State uncertainty locally.
- Keep code excerpts rare; the course must work without them.
