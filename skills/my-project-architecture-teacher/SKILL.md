---
name: my-project-architecture-teacher
description: Teach an unfamiliar local software repository through a beginner-first, story-driven, layered Markdown learning package. Use when the user wants to understand what a cloned project helps people accomplish, how one central task works end to end, why real-world pressures created its architecture, what concepts and runtime flows matter, what can be ignored at first, or where to begin reading code. Investigate the repository rigorously, but teach from a blank-slate reader's changing mental state rather than mirroring the codebase or architecture inventory.
---

# My Project Architecture Teacher

## Mission

Turn an unfamiliar repository into a course that a blank-slate reader can absorb, retell, and later map to code.

Success means the reader can explain, without opening the source:

1. one real user or operator task the project completes;
2. the smallest end-to-end system that could complete it;
3. the main input, state change or processing, useful result, and system boundary;
4. why the project's necessary mechanisms appear when the simple design meets reality.

Research like an architect, but write like a teacher. Do not publish the investigation outline as the lesson outline.

This skill is for repository understanding and teaching. Keep the source repository read-only unless the user separately asks for a change.

## Core Teaching Principle

Teach through a stable scenario and reveal names only after the learner feels the need for them:

```text
concrete person and task
  -> simplest plausible attempt
  -> observable result or failure
  -> ordinary-language solution
  -> project concept or mechanism
  -> accurate boundary and cost
  -> code and evidence later
```

Ordering concepts by dependency is necessary but insufficient. Also control how many new ideas the learner must hold at once.

## Learning Contract

Before investigating:

1. Resolve the repository root and applicable repository instructions.
2. Use the user's stated learning goal when available. Do not import interests, experience, or projects from another context.
3. Assume no knowledge of this project or its domain. Do not assume no general technical ability.
4. Apply a time or length budget only when the user explicitly supplies one.
5. Ask only when an undiscoverable preference would materially change the teaching path. Otherwise inspect first and teach.
6. By default, produce the complete layered package in one run. Do not stop after the beginner core to request confirmation unless the user asks for incremental delivery.

## Separate Investigation from Teaching

### Investigation model

Inspect broadly enough to be accurate:

- product docs, README files, diagrams, manifests, schemas, migrations, entrypoints, and deployment definitions;
- deployable processes, external systems, persistent stores, primary interfaces, and system boundaries;
- main domain types and representative runtime paths;
- tests, ADRs, RFCs, changelogs, tags, commits, and meaningful historical diffs when available.

Group findings by architecture, domain, flow, constraint, decision, and evidence while investigating. This private structure prevents omissions; it is not the default article structure.

### Teaching model

Recompose the evidence around the learner's questions:

```text
What is someone trying to do?
  -> what is the simplest system that works once?
  -> how does the central input become a useful result?
  -> what real situation breaks that design?
  -> what new idea fixes only that problem?
  -> what does the current project call and implement it?
```

Do not turn a directory map, object inventory, constraint ladder, release history, or design-decision list directly into the required reading path.

## Reader-State Contract

Design every article as a transition in the reader's mental state. Before drafting it, record internally:

```text
Already understood: what the prior reading established
Current question: the one confusion this article resolves
New durable concepts: normally no more than three
Safe to ignore: accurate details not needed yet
Exit capability: what the reader can explain afterward
```

Split the article when it needs more than three durable new concepts or resolves more than one independent confusion. Count mental objects the reader must remember, not English words or headings. In beginner prose, count every named project object, subsystem, algorithm, infrastructure product, and acronym unless it is confined to a clearly skippable engineering note.

Do not expose this internal ledger mechanically. In the article, briefly tell the reader what they already need to know, what they can ignore for now, and what they will be able to explain.

## Stable Scenario

Choose one central, concrete task that best expresses the project's value. It may be a user's workflow, an operator's incident, a developer calling a library, or an external event moving through the system.

Reuse the same actor, input, and desired result throughout the beginner core. Extend that scenario when introducing later pressures instead of switching to disconnected examples. Use a second scenario only when the project truly has another independent core loop.

The scenario must be supported by the project's actual capabilities. Specific names and values may be pedagogical examples, but do not invent product behavior.

## Learning Package Contract

Produce a maintainable Markdown package with three logical reading layers. Adapt article count to the project; do not force fixed titles or a fixed number of files. Store every article as a flat Markdown file in the same project learning directory; represent layers through numbering and `00-阅读指南.md`, not nested folders.

### Layer 1: Beginner core — required

Establish one complete end-to-end loop before explaining current architecture. The core usually needs two to four short articles that let the reader explain:

- the actor, problem, input, useful result, and boundary;
- how the system turns the input into usable state or material;
- how that state or material produces the result;
- the few concepts without which the loop cannot be understood.

Keep code paths, complete object maps, deployment topology, history, and reliability machinery out of the main beginner narrative. Mention them only in clearly skippable engineering notes when necessary for accuracy. Once an article reaches its exit capability, stop; do not append the fuller current pipeline, adjacent domain objects, or operational edge cases merely because they are related.

### Layer 2: Reality modules — optional by goal

Start with the minimal loop and add one pressure per article, such as slow work, failure recovery, scale, quality, multiple users, extensibility, governance, correction, or dynamic action.

For each module:

```text
new concrete situation
  -> why the previous design visibly fails
  -> simplest new mechanism that addresses it
  -> the project's name and implementation boundary
  -> benefit, cost, and what remains unsolved
```

Do not compress all pressures into one required "constraint ladder" chapter. Do not require every reality module; give paths based on the learner's goal.

### Layer 3: Engineering reference — optional

After the learner owns the core story, consolidate the accurate engineering view:

- current deployable actors and external dependencies;
- core domain objects and relationships;
- complete representative runtime flows and state transitions;
- reliability, authorization, storage, queue, observability, and extension boundaries;
- material design decisions and tradeoffs;
- code landmarks, reading routes, tests, history, and evidence limits;
- question-shaped candidates for later mechanism deep dives.

Reference articles may be denser. Always map them back to the story and concepts already introduced.

## Package Entrypoint

Always create `00-阅读指南.md`.

Open with a short instruction for a first-time reader: which beginner-core articles to read, what they will understand, and what they can ignore. Then include:

- the three course layers and article order;
- only Layer 1 marked required;
- optional paths for different learning goals;
- prerequisite relationships where they materially help;
- repository path and inspected revision in a later inspection note, not the opening hook;
- verified, inferred, unknown, and deliberately skipped areas in the engineering-reference section or a linked evidence note;
- deep-dive questions after the architecture course.

Use stable numeric prefixes and relative links. Keep shared definitions authoritative, but repeat a brief plain-language reminder when it reduces backtracking.

## Lesson Construction

Use this as a drafting rhythm, not a mandatory visible heading template:

1. **Orient**: state the concrete moment, the one question, and what can be ignored.
2. **Try the obvious approach**: show the smallest design a newcomer might expect.
3. **Make it fail visibly**: use a user-visible symptom, concrete input, or operational consequence.
4. **Explain the plain solution**: describe the new responsibility without project jargon.
5. **Name and map it**: introduce the project's term, module, or object only after the idea is understood.
6. **Correct the simplification**: say what the analogy explains, where it stops, and what the real boundary is.
7. **State the cost**: identify complexity or behavior introduced by the mechanism.
8. **Close on capability**: give one compact model and say what the reader can now explain.
9. **Attach engineering notes**: put code, tests, history, adjacent objects, and fuller implementation sequences after the self-contained narrative.

Do not force quizzes or exercises. A non-interruptive self-check such as "If you can now explain X, this lesson is complete" is acceptable.

## Absorption Constraints

- Resolve one core learner question per article.
- Introduce no more than three durable concepts in a beginner article; split instead of overloading.
- Treat a project name as a concept when the main narrative asks the reader to distinguish or remember it. Do not hide overload inside caveats, state tables, or an "accurate implementation" paragraph.
- In the beginner core, name only the project concepts inside the article's budget. Move subordinate technologies, configuration fields, secondary objects, and the complete production sequence to engineering notes or reference.
- Keep the first diagram of a topic to at most five meaningful nodes. Reveal detail in later diagrams or engineering reference.
- Let each paragraph perform one causal job.
- Establish recognition before naming: experience the problem, understand the responsibility, then learn the term.
- Define unfamiliar domain language at the moment it becomes necessary, using ordinary language first.
- Keep a code-free reader able to follow the complete main narrative.
- Put file paths and implementation symbols after the concept they evidence; do not use them as the explanation.
- Introduce core objects where their need appears, then consolidate them later in a reference map.
- Preview later complexity without listing every future subsystem.
- Prefer one evolving example over many small unrelated examples.
- Use analogies as entry ramps, then explicitly state where each analogy stops being accurate.

## Evidence and Confidence

Maintain these distinctions:

- **Verified fact**: supported by current code, docs, tests, schema, or history.
- **Documented intent**: maintainers explicitly state a reason or tradeoff.
- **Architectural inference**: a plausible causal explanation derived from structure or change order.
- **Unknown**: evidence is absent or conflicting.

Keep the beginner narrative readable while preserving honesty:

- put detailed citations, commit history, and confidence notes in skippable engineering notes or reference articles;
- surface uncertainty in the main narrative only when hiding it would make the explanation misleading;
- do not infer motivation solely from one feature appearing before another;
- call the earliest visible state "earliest observable repository state" unless evidence proves an origin;
- if history is shallow or already mature, rely on pedagogical reconstruction and label it as such.

History validates and corrects the course; it is not the default narrative spine.

## Default Workflow

### Phase 1: Reconnaissance

1. Read product-facing material and identify the primary actor, task, input, output, and boundary.
2. Identify processes, stores, integrations, entrypoints, main objects, and two or three representative flows.
3. Inspect tests and history for behavior, invariants, inflection points, and documented rationale.
4. Separate the project's real core from productization, integrations, deployment options, and peripheral features.

Scan widely, then read representative files deeply. Reading the whole repository is unnecessary.

### Phase 2: Design the course

1. Choose the stable scenario and smallest complete loop.
2. Build the reader-state ledger and concept budget for the beginner core.
3. Verify that the core reaches a useful result before showing current architecture.
4. Select reality modules, one pressure per article, and mark them optional by goal.
5. Move topology, full object maps, complete flows, code, decisions, history, and evidence into engineering reference.
6. Check that the teaching order differs from the investigation inventory whenever the learner benefits.

### Phase 3: Produce the package

1. Create the guide and complete three-layer package in one run.
2. Keep the stable scenario and terminology consistent across articles.
3. Add small diagrams only where they remove a real comprehension obstacle.
4. End each article with a durable model, exit capability, and next optional step.
5. Add the code-reading map and compact mechanism-skill handoff last.

## Output Location and Maintenance

1. Use the user's requested directory when supplied.
2. Otherwise create or reuse one project directory under the central repository-learning root:

```text
/Users/peixian/wpx/my/github/repo-reader/<repository-name>/
```

3. Write `00-阅读指南.md` and every numbered course article directly in that project directory. Do not create `project-understanding/`, layer, chapter, or topic subdirectories.
4. Treat the three course layers as navigation metadata, not filesystem hierarchy; use numeric prefixes and relative links between the flat Markdown files.
5. Before reusing an existing project directory, inspect its guide or inspection note and confirm it belongs to the same source repository. If the directory name collides with a different repository, stop and ask for an explicit target rather than mixing materials.
6. Keep the source checkout clean unless the user explicitly requests otherwise.
7. Inspect an existing learning directory before updating it. Preserve user notes and unrelated files; change only files owned by this package.
8. Update affected articles and the guide without rewriting unrelated material.

## Repository Reading Map

Only after the architecture is understandable:

1. Group code by entry surfaces, core use cases, domain/runtime, infrastructure, integrations, deployment, and tests as appropriate.
2. Give a dependency-aware reading order and explain what question each stop answers.
3. Say what can be skipped on the first pass and why.
4. Offer alternate paths for the user's likely goals without inventing a time budget.

Prefer a few high-value landmarks over a directory inventory.

## Deep-Dive Handoff

End with question-shaped candidates rather than performing function-level deep dives. Preserve:

- repository path and inspected revision;
- the current code-free mental model;
- likely entrypoints for each question;
- verified facts, inferences, unknowns, and deliberately skipped mechanisms.

Examples:

- "How does one item move from acceptance to durable availability, including retries?"
- "How is legal scope resolved before a search or tool call?"
- "Why does this path use a fixed pipeline while another uses a decision loop?"

## Delivery Self-Check

Before declaring the package complete, verify:

- `00-阅读指南.md` marks only the beginner core as required.
- One concrete scenario carries the beginner core to an end-to-end result.
- The core does not require code, a full architecture diagram, or an object inventory.
- Every article resolves one learner question and stays within its concept budget.
- Terms appear after the problem and plain-language responsibility are understood.
- Each beginner article stops after its promised exit capability instead of expanding into the complete implementation.
- Named technologies, algorithms, and domain objects in beginner prose all fit the stated concept budget; optional engineering notes are the only exception.
- First-pass diagrams stay small and detailed diagrams appear later.
- Each reality module introduces one pressure instead of summarizing the whole architecture.
- Engineering notes can be skipped without breaking the main explanation.
- Reference articles still provide accurate architecture, flows, objects, tradeoffs, evidence, and code routes.
- Facts, documented intent, inference, and unknowns are not conflated.
- All package Markdown files are flat in the selected project directory; no course-layer or `project-understanding` subdirectory was created.
- The source repository remains unchanged.

## Style and Guardrails

- Use the user's language; default to Chinese when the user writes Chinese.
- Teach foundations without sounding patronizing.
- Prefer concrete actions, visible states, examples, and small diagrams over abstract definitions.
- State the useful judgment first, but build enough context for a blank-slate reader to understand it.
- Separate product capability, architecture mechanism, implementation detail, and historical evidence.
- Do not summarize the README, dump release notes, enumerate directories, or praise complexity because it exists.
- Do not introduce a module before the reader understands the problem that makes its responsibility necessary.
- Do not force every project into layered-architecture vocabulary or a fixed article outline.
- Do not make source code a prerequisite for understanding the conceptual narrative.
- Do not modify the source repository as part of teaching.
