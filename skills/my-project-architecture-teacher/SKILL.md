---
name: my-project-architecture-teacher
description: Teach an unfamiliar local software repository to programmers who know general software development but are new to the project and its domain. Derive why the current architecture and major modules exist in smooth, information-dense prose; assemble the whole-project mental model; explain how those responsibilities shape the repository tree; and map common changes to owning code, contracts, external repositories, and tests. Use when the user wants a readable Markdown course from domain foundations through practical code navigation. Investigate rigorously, keep source repositories read-only, distinguish evidence from pedagogical reconstruction, and reserve function-level mechanism details for later.
---

# My Project Architecture Teacher

## Mission

Turn an unfamiliar repository into a readable course for a programmer who understands ordinary software development but is new to this project and its domain. The prose should let the reader reconstruct the current architecture and then use that model to navigate real code changes.

The required reading is complete only when the reader can:

1. explain the human or business need without assuming the project or its domain solutions;
2. show the earliest system that genuinely works under limited conditions;
3. explain which concrete pressure earns every major current architecture responsibility;
4. draw the current product-domain, runtime/deployment, and state/flow views from memory;
5. explain each major module's responsibility, inputs, outputs, owned state, neighbors, and explicit non-responsibilities;
6. explain the current repository's primary and secondary organizing axes, alternatives, tradeoffs, and evolutionary seams;
7. trace representative behavior through the current directories, entrypoints, generated boundaries, external repositories, and tests;
8. route a concrete change to its primary owner, required contracts, conditional neighbors, unaffected areas, and verification paths.

The learner should feel the architecture grow, see it converge into the current system, understand why that system is projected into the repository tree in its present shape, and then use the tree rather than merely inspect it.

This skill is for repository understanding and teaching. Keep every source repository read-only unless the user separately asks to change it.

## Required Resources

For every request that generates or rewrites course prose, read [references/narrative-writing-contract.md](references/narrative-writing-contract.md) before drafting. It defines the programmer audience, information-density rules, terminology timing, diagram admission, natural endings, and positive/negative examples.

For every complete course request, also read [references/course-design-contract.md](references/course-design-contract.md) before designing the package. It contains the detailed investigation ledger, architecture-admission rules, repository-organization analysis, required course outputs, and delivery audit.

Read [references/tower-regression-example.md](references/tower-regression-example.md) only when:

- the target repository is Tower; or
- this skill itself is being developed or behaviorally validated.

Do not load or copy the Tower sequence for other repositories. Other projects must earn their own domain runway, architecture responsibilities, organizing axes, and change routes from current evidence.

## Core Teaching Model

Teach through a stable human goal and an evolving system:

```text
solution-free human or business need
  -> smallest system that genuinely works under stated conditions
  -> visible successful result
  -> one new concrete pressure
  -> one observable failure or unacceptable cost
  -> new responsibility in ordinary language
  -> project or domain term
  -> updated cumulative architecture model
  -> repeat until every major current responsibility is earned
  -> assemble the complete current architecture
  -> explain how maintainers project it into the repository tree
  -> map representative flows and changes to code and tests
```

This sequence is internal design scaffolding, not a visible article template. Four rules are mandatory:

- Do not state the initial need using the project, mechanism, or domain object that the course is meant to explain.
- Let the previous system succeed under explicit limited conditions before adding a pressure. Do not create a straw-man design merely to justify the current architecture.
- If no simpler system can genuinely work, do not invent one. State the non-negotiable constraint, support it with evidence, and introduce only the responsibility it immediately requires.
- Show that a previous system succeeds through its observable result. Do not repeatedly announce that "the current solution works" merely to satisfy the sequence.

The minimal project loop is a checkpoint, not the course endpoint. Continue until all major current responsibilities have been taught and assembled.

## Learning Contract

Before investigating:

1. Resolve the source root, output location, applicable repository instructions, and current revision.
2. Use the user's stated learning goal when available. Do not import interests, experience, or projects from another context.
3. Assume ordinary programming knowledge: frontend/backend development, development and production environments, HTTP, processes, and databases need no foundational tutorial unless the user says otherwise.
4. Assume no knowledge of this project, its domain objects, runtime roles, architecture mechanisms, or repository conventions.
5. Descend below ordinary programming concepts only when the user explicitly needs that foundation or the target concept cannot be understood without it.
6. Treat a domain or project concept as already understood only when the user says so or the requested goal clearly establishes it.
7. Apply a time or length budget only when the user explicitly supplies one.
8. Ask only when an undiscoverable preference would materially change the teaching path. Otherwise inspect first and teach.
9. By default, produce the complete required architecture and repository-navigation spine in one run. Do not stop at the minimal loop to request confirmation.

## Output Language

Choose one output language before investigating and use it consistently across the guide and every article.

Resolve it in this order:

1. Follow an explicit output-language instruction.
2. For a direct interactive request, use Chinese when the user's main natural-language question is Chinese.
3. Otherwise use English, including scheduled, automated, or indirect calls.
4. When unclear, use English without asking.

Infer language only from the user's natural-language request, not repository content, paths, code identifiers, or quoted material.

For English output:

- write the architecture-construction narrative in natural low-B1 English;
- write repository-navigation material in clear technical English;
- preserve necessary code identifiers and explain unfamiliar terms simply.

For Chinese output, write the complete package in Chinese while preserving official technical names and code identifiers.

Keep `00-阅读指南.md` as the fixed entry filename in either language.

## Evidence and Historical Honesty

Maintain these distinctions:

- **Verified fact**: supported by current code, docs, tests, schemas, manifests, or history.
- **Documented intent**: maintainers explicitly state a reason or tradeoff.
- **Pedagogical reconstruction**: a simplified causal sequence that helps the learner derive the current design; it is not claimed history.
- **Architectural inference**: a plausible explanation derived from current structure and dependency boundaries.
- **Unknown**: evidence is absent, inaccessible, or conflicting.

Code proves current behavior and boundaries; directory names and commit order do not prove original motivation. Say "the current structure reflects..." or "a likely architectural reason is..." unless documentary evidence supports "the maintainers chose this because...".

History validates and corrects the course. It is not the default narrative spine. Call the earliest visible state the "earliest observable repository state" unless evidence proves an origin.

## Investigation Model

Inspect broadly enough to identify:

- the solution-free goal, actor, visible success, and system boundary;
- product domains and core object relationships;
- deployable or executable roles, persistent stores, external systems, and delivery boundaries;
- shared architecture responsibilities and cross-cutting authorities;
- representative read, write, asynchronous, and background-convergence flows;
- manifests, workspace configuration, package dependencies, entrypoints, schemas, migrations, generated code, tests, and deployment definitions;
- current repository roots, external repositories, primary and secondary organizing axes, and evolutionary seams;
- documented decisions, meaningful historical evidence, and remaining unknowns.

During investigation, distinguish:

```text
human or business goal
domain choice
project capability
architecture responsibility
repository organization
implementation detail
```

Scan widely, then read representative files deeply. Reading every directory is unnecessary; failing to identify a major runtime, state, integration, product-domain, repository, or delivery boundary is not.

## Stable Goal, Evolving System

Choose one central, concrete goal that best expresses the project's value. It may be a user workflow, operator incident, library call, or external event moving through the system.

Keep stable through the architecture-construction spine:

- the main actor or role;
- the final human or business goal;
- the visible result that proves success;
- the central scenario.

Allow to evolve:

- technical input;
- current system boundary;
- acceptable completion method;
- architecture nodes and relationships;
- module and repository knowledge.

Use a second scenario only when another independent core loop is necessary to explain the current architecture. Pedagogical names and values may make a verified capability concrete, but must not invent product behavior.

## Article Design

Design each architecture-growth article as one transition. Internally record:

```text
Stable business goal:
Architecture already earned:
Conditions under which the current system works:
One new concrete pressure:
Visible symptom or unacceptable cost:
New responsibility:
New durable concepts:
Architecture-model delta:
Current repository implementation:
Evidence boundary:
Deliberately deferred categories:
Exit capability:
```

These fields, architecture admission cards, concept budgets, repository decision cards, and module responsibility cards are authoring tools. Do not render them as repeated headings, lesson objectives, "completion standards," reader-capability statements, or fixed article endings.

Normally add one primary responsibility per article. Supporting concepts may appear when they solve the same pressure and the total durable-concept count remains manageable. Count domain objects, nodes, states, identities, authority distinctions, synchronization relationships, and necessary caveats as concepts.

Split an article when it resolves independent pressures or asks the learner to retain several unrelated system models. Do not repair a broken transition by appending caveats.

Use this causal rhythm internally while drafting natural prose:

1. recall the stable goal and current system;
2. make the current system's success evident through an observable result;
3. add one concrete pressure;
4. make the problem visible;
5. explain the missing responsibility in ordinary language;
6. name the project mechanism and update the model;
7. include benefit, cost, or boundary only when it improves the current explanation;
8. end naturally with the state the system has now reached or the next concrete pressure. Do not emit a completion criterion, lesson objective, or reader-capability statement.

## Required Course Shape

Produce three logical reading sections. Article count follows cognitive transitions and repository complexity, not a preset quota.

### 1. Architecture-construction spine — required

The required spine must establish:

1. a solution-free goal and earliest working system;
2. only the domain foundation needed to understand the project's responsibility;
3. why the project appears and one minimal successful project loop;
4. why every major current architecture responsibility appears;
5. the current product-domain map;
6. a complete architecture assembly;
7. two to four representative flows and their state/authority boundaries;
8. a responsibility map for every major module.

A responsibility belongs in this spine when it materially participates in a central flow, owns important state, defines a cross-module contract, is a runtime/build/deployment role, drives asynchronous lifecycle, isolates an external system, converges state, carries cross-cutting authority, or determines repository ownership.

### 2. Repository-navigation spine — required

After the architecture is understandable, teach:

1. the organizing pressures maintainers face;
2. the repository's primary and secondary organizing axes;
3. at least one genuinely workable alternative and its tradeoff;
4. how architecture responsibilities map to current repositories, directories, packages, entrypoints, generated artifacts, and tests;
5. how representative flows traverse the real tree;
6. how concrete changes map to primary owners, required contracts, conditional neighbors, external repositories, unaffected areas, and validation;
7. how evolutionary seams and unverified external boundaries affect modification choices.

The reader should not need to infer this mapping from a directory inventory.

Keep the same connected prose through this section. Begin from the architecture responsibility the reader already understands, explain the code-organization pressure, then introduce the directory, representative entrypoint, and change consequence. Trees, tables, responsibility maps, and test maps support that explanation; they do not replace it.

### 3. Mechanism deep dives — optional

Reserve function-level state machines, retry algorithms, payload construction, synchronization internals, complex lifecycle branches, and complete delivery chains for question-shaped optional follow-ups. Do not use optionality to hide a major current architecture responsibility.

## Architecture Convergence

Build diagrams progressively, then converge them.

- The first model contains only the earliest system that genuinely works.
- Later articles add only nodes and relationships already derived in prose.
- State which pressure earned each new node.
- Do not preview future mechanisms merely to make a diagram complete.
- Before the architecture spine ends, assemble at least the domain/responsibility, runtime/deployment, and state/flow views defined in the course contract.
- The assembly article should introduce few or no new durable concepts.

Every major module must have a responsibility card that explains why it exists, what it receives and produces, what state it owns, who calls it, what it calls, what it explicitly does not own, where it runs, where it lives, what changes it primarily owns, and which tests represent it.

The card may be rendered as a comparative summary table when that materially helps the reader. Do not repeat its field labels as a bureaucratic template for every module.

## Repository Organization and Code Navigation

Treat the repository tree as one projection of a multidimensional architecture, not as the architecture itself.

Determine whether the tree is primarily organized by product domain, technical responsibility, runtime/build/deployment unit, shared contract, integration boundary, or a hybrid. Identify the secondary axis used inside those top-level boundaries.

Compare the current choice with at least one plausible alternative. Explain the pressure, benefit, cost, and change-navigation consequence without pretending to know undocumented original intent.

Teach repository landing through:

```text
architecture responsibility
  -> current repository and directory/package
      -> representative file, type, or function
          -> test and verification path
```

An annotated tree must mark implementation homes, generated code, tests, runtime or delivery units, external repositories, unverified paths, and first-pass skip areas. Expand only to the depth that explains responsibility and ownership.

For every change example distinguish:

```text
Primary owner:
Required contract changes:
Conditional adjacent changes:
Generated consumers:
External repositories:
Verification paths:
Explicitly unaffected areas:
Unknown or blocked boundaries:
```

Do not promise that one feature maps to one module. Teach how to find the primary owner and then prove the conditional impact surface.

## Package Entrypoint and Output

Always create `00-阅读指南.md`.

Open with:

- the solution-free goal;
- the complete required architecture and repository-navigation path;
- the mental models the reader will build;
- which already-understood categories can be skipped initially.

Do not open with an unexplained final architecture or jargon inventory. Later include repository path, inspected revision, evidence boundaries, optional deep dives, and alternate routes.

Store every article as a flat Markdown file in one learning directory. Use stable numeric prefixes and relative links, not nested layer folders.

Use the requested output directory. Otherwise create or reuse:

```text
/Users/peixian/wpx/my/github/repo-reader/<repository-name>/
```

Before reusing an existing directory, verify it belongs to the same source repository. Preserve user notes and unrelated files. Keep source checkouts unchanged.

## Default Workflow

### Phase 1: Reconnaissance

1. Resolve instructions, language, source root, output, revision, and learning goal.
2. Identify the solution-free goal, domain runway, earliest working system, and visible success.
3. Identify product domains, roles, stores, external systems, major responsibilities, and representative flows.
4. Inspect current repository organization, dependencies, generated boundaries, tests, external repositories, delivery configuration, decisions, and history.
5. Build the evidence table, architecture admission cards, and repository organization decision cards from the course contract.

### Phase 2: Design

1. Design the code-free architecture-construction spine.
2. Record which ordinary programming concepts can be compressed, which domain mechanisms need expansion, and which code identifiers must be delayed.
3. Confirm that every major current responsibility has earned a required article or an explicit place in a shared-pressure article.
4. Design the convergence views, flows, and module responsibility cards.
5. Design the maintainer-organization bridge by comparing current and plausible alternative structures.
6. Map every responsibility and representative flow to real repositories, directories, entrypoints, generated artifacts, and tests.
7. Add at least three change-navigation cases: local presentation, cross-layer capability, and background/integration/delivery.
8. Assign optional mechanism deep dives last.

### Phase 3: Produce and audit

1. Create the guide and complete package in one run unless incremental delivery was requested.
2. Keep the stable scenario consistent while allowing the system and repository model to evolve.
3. Draft the complete package in connected prose; do not expose internal cards or causal checklists.
4. Add diagrams only when they materially remove a comprehension obstacle and pass the deletion test in the narrative contract.
5. Run the narrative, causal, architecture-completeness, repository-organization, path, link, and change-navigation audits from the references.
6. Report document checks as document checks; do not claim source tests or runtime validation that did not occur.

## Delivery Self-Check

Before declaring completion, verify:

- both required spines are marked required in `00-阅读指南.md`;
- the initial goal contains no unearned solution word;
- each old system visibly works before one new pressure appears;
- familiar software context is compressed while unfamiliar domain mechanisms receive enough explanation;
- internal cards, concept budgets, and exit capabilities do not leak into visible prose;
- each paragraph adds a fact, causal relationship, system model, boundary, or code-navigation consequence;
- each article ends on a natural result or next pressure rather than a fixed summary;
- every diagram still carries useful information after comparing it with the surrounding prose;
- every major current responsibility is in required reading;
- the final architecture views contain only explained nodes;
- the reader can traverse two to four representative flows and identify state authority;
- every major module has a complete responsibility card;
- the repository's primary and secondary organizing axes and one alternative are explained;
- organizational rationale is labeled as fact, intent, inference, reconstruction, or unknown;
- evolutionary seams are not silently presented as an ideal design;
- every major responsibility maps to current repositories, directories, entrypoints, and tests;
- generated and external boundaries are explicit;
- change cases distinguish primary, required, conditional, unaffected, external, and unknown areas;
- local paths exist at the inspected revision and relative article links resolve;
- all package Markdown files are flat in the selected learning directory;
- source repositories remain unchanged.

## Style and Guardrails

- Teach foundations without sounding patronizing.
- Compress what a general programmer already knows; expand what is unfamiliar about this project or domain.
- Use a scenario only to establish the pressure. Do not develop atmosphere, character detail, or business background that does not improve the architecture model.
- Prefer concrete actions, visible states, and examples over abstract definitions, but use numbers and narrative detail only when they clarify resources, state, scale, cost, or boundaries.
- Resolve one core learner question per growth article.
- Establish recognition before naming; explain responsibility before project terminology.
- Use ordinary descriptive names before arbitrary code-like identifiers. Delay files, types, functions, and teaching names such as `order-api` until they provide real navigation value.
- Remove a paragraph that merely makes the story more vivid, restates the previous paragraph, or satisfies an internal template without adding information.
- Do not mechanically add meta prose such as "this article covers," "we will ignore," "the current solution works," "completion standard," "the reader can now explain," or "chapter summary." Use such phrasing only when its information is genuinely necessary.
- Do not append fixed summaries, review questions, lesson objectives, or capability statements to ordinary articles.
- A diagram must show a relationship, change, allocation, flow, authority, boundary, or architecture-to-code projection that adjacent prose does not make equally clear. Do not rearrange the same nouns into a decorative tree.
- Keep the code-free architecture narrative understandable without source access.
- Keep repository-navigation prose connected to the architecture narrative. Introduce paths, trees, matrices, and tests through the responsibility and modification question they answer.
- Do not summarize a README, dump releases, enumerate directories, or praise complexity because it exists.
- Do not introduce a module before the reader understands the pressure that earns it.
- Do not infer design intent solely from a package name, directory shape, import edge, or commit order.
- Do not force every project into Tower's domain runway, module taxonomy, or article numbers.
- Preserve technical depth by moving mechanism detail later, not by deleting major architecture responsibilities.
- Do not modify source repositories as part of teaching.
