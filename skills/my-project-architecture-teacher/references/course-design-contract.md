# Complete Course Design Contract

Read this reference for every complete project-architecture course. It turns the shared teaching principles in `SKILL.md` into a concrete investigation, course-design, repository-navigation, and delivery contract.

## 1. Required Learning Outcome

The required reading must take the learner through two connected achievements:

```text
reconstruct the current architecture from real needs and pressures
  -> understand how maintainers project those responsibilities into repositories and directories
  -> use that map to locate and verify concrete changes
```

Do not treat the minimal project loop as completion. Do not make complete topology, major modules, repository organization, or change navigation optional when the user's goal is whole-project understanding.

Article count is derived from cognitive transitions and repository complexity. Do not impose another project's numbering or module taxonomy.

## 2. Investigation Ledger

Before course design, record internally:

```text
Business goal:
Actor and visible success:
Default programmer knowledge:
Domain knowledge not assumed:
Familiar context to compress:
Unfamiliar mechanisms to expand:
Code identifiers deliberately delayed:
Solution words already embedded in the apparent task:
Earliest system that genuinely works:
Domain foundation required before naming the project:
Where the actual project responsibility begins:

Product domains:
Core domain objects and relationships:
Deployable or executable roles:
Shared architecture responsibilities:
Cross-cutting authorities:
Persistent stores and state owners:
External systems and integrations:
Build and deployment boundaries:

Representative read flows:
Representative write flows:
Representative asynchronous flows:
Background convergence flows:

Current repository roots:
Workspace or package boundaries:
Primary repository-organizing axis:
Secondary repository-organizing axis:
Generated-code boundaries:
External-repository boundaries:
Test and verification boundaries:
Evolutionary seams:

Documented decisions and intent:
Architectural inferences:
Unknowns and inaccessible evidence:
```

Inspect product material, repository instructions, manifests, workspaces, build configuration, entrypoints, deployment definitions, schemas, migrations, representative code, tests, ADRs, RFCs, release material, and meaningful history where available.

Use imports and package dependencies to verify current coupling and direction, not to invent original motivation.

## 3. What Counts as a Major Architecture Responsibility

A responsibility belongs in the required architecture spine when any of these is true:

- it materially participates in a central read, write, asynchronous, or convergence flow;
- it owns important domain, operation, identity, or workflow state;
- it defines a contract consumed across module or repository boundaries;
- it is an independently executable, buildable, deployable, or delivered role;
- it drives or records a long-lived operation;
- it isolates external-system differences;
- it rereads external facts or converges a local management view;
- it controls authorization, audit, tenancy, legal scope, or another cross-cutting authority;
- it determines which repository actually owns user-visible behavior;
- removing it would make the final architecture or change-navigation model materially false.

Do not promote every directory, helper package, object type, or infrastructure product into a main module. Group supporting implementation by the responsibility it serves.

## 4. Architecture Admission Card

Prepare one card for every architecture responsibility introduced through a pressure:

```text
Previous system:
Why it works:
New pressure:
Visible problem:
New responsibility:
Project term:
Benefit:
Cost:
Remaining problem:
Architecture-model delta:
Current repository implementation:
Evidence boundary:
```

This card is internal. Its labels must not become a repeated article structure.

The previous system must be genuinely viable under stated conditions. If no simpler viable system exists, state the non-negotiable constraint and evidence instead of inventing a straw man.

The visible problem must be imaginable or observable: a user cannot find a resource, a request ends before work does, data becomes stale, a process restart loses progress, two consumers need a stable contract, or a release artifact cannot reach its runtime.

## 5. Repository Organization Decision Card

For every important repository, top-level package family, or directory boundary, record:

```text
Architecture responsibility:
Current directory or package:
Primary organizing axis:
Secondary organizing axis:
Alternative organization:
Why the alternative could work:
Pressure favoring the current organization:
Runtime, build, or deployment boundary:
Shared contract:
Generated-code boundary:
External-repository boundary:
Verified evidence:
Documented intent:
Architectural inference:
Evolutionary seam:
Tradeoff:
Change-navigation consequence:
```

This card is internal. The visible course may use a comparative table when several mappings benefit from comparison, but it must not repeat the card as a form for every directory.

Possible organizing axes include:

- product domain;
- technical responsibility or layer;
- executable/runtime role;
- build or deployment unit;
- stable shared contract;
- external integration;
- team or independent delivery boundary;
- a hybrid with one primary and one secondary axis.

Explain at least one plausible alternative. Do not compare the current tree with an obviously unworkable caricature.

When intent is not documented, prefer wording such as:

> The current structure reflects top-level separation by runtime responsibility and shared capability, with product domains inside those packages. This fits the verified execution and dependency boundaries, but it is an architectural inference rather than a confirmed account of the original design decision.

## 6. Required Course Sections

### Section A: Architecture construction — required

Build in this order:

1. solution-free human or business goal;
2. earliest working system and visible success;
3. only the domain foundation necessary to understand the project;
4. why the project itself appears;
5. one minimal successful project loop;
6. one pressure at a time until every major current responsibility is earned;
7. current product-domain map;
8. complete architecture assembly;
9. representative flows and state/authority boundaries;
10. module responsibility map.

The center scenario may remain stable while technical inputs, system boundaries, and acceptable completion methods evolve.

The minimal loop may temporarily assume fast work, one integration shape, success, no external drift, or one operator. Later required articles break those assumptions one at a time when the resulting responsibility is part of the current architecture.

### Section B: Repository landing — required

After the code-free architecture is understandable:

1. explain the organizing pressures maintainers face;
2. identify the primary and secondary repository axes;
3. compare the current structure with at least one viable alternative;
4. identify runtime/build/deploy units, shared contracts, generated artifacts, integrations, external repositories, and historical seams;
5. show an annotated repository tree at architecture-relevant depth;
6. map representative flows through current directories and representative entrypoints;
7. route concrete changes through primary, required, conditional, external, unaffected, and unknown areas;
8. map each route to tests and other verification evidence.

### Section C: Mechanism deep dives — optional

Offer question-shaped follow-ups for one state machine, algorithm, lifecycle, retry policy, payload mapping, synchronization mechanism, or delivery chain. Do not perform all deep dives inside the architecture course.

## 7. Article Contract

For every architecture-growth article, record internally:

```text
Stable business goal:
Architecture already earned:
Default programmer knowledge:
Domain knowledge not assumed:
Familiar context to compress:
Unfamiliar mechanism to expand:
Conditions under which the current system works:
One new concrete pressure:
Visible symptom or unacceptable cost:
New responsibility:
New durable concepts:
Architecture-model delta:
Current repository implementation:
Evidence boundary:
Deliberately deferred categories:
Information gained in each paragraph:
Code identifiers deliberately delayed:
Diagram question:
Natural ending:
Exit capability: internal audit only
```

`Exit capability` is never a visible footer. Do not render it as "完成标准", "读者应该能够", a lesson objective, a review question, or an equivalent ending.

Normally introduce one primary responsibility. Supporting concepts may share the article only when they jointly solve the same pressure and remain cognitively manageable.

Each paragraph should mainly perform one causal action: establish need, make prior success visible, add pressure, show a problem, explain responsibility, name an element, correct a boundary, update the model, map responsibility to code, or establish the next pressure.

One causal action is necessary but not sufficient. Paragraphs must connect naturally and add information. Do not keep a low-information paragraph merely because it fills one field in the contract. Compress ordinary software context a general programmer already knows; expand unfamiliar domain mechanisms beyond a one-sentence definition when the reader needs process, state, relationship, or a concrete value to place them correctly.

## 8. Architecture Convergence Views

Before Section A ends, produce at least three mutually consistent views.

### Domain and responsibility map

Show:

- the major product domains;
- shared platform or infrastructure responsibilities;
- which responsibilities are domain-specific versus cross-domain.

The center scenario is an entry route, not permission to present one domain as the whole product.

### Runtime and deployment topology

Show:

- user/client surfaces;
- executable services and workers;
- persistent stores;
- workflow, queue, or scheduler dependencies;
- external platforms;
- build, delivery, and deployment boundaries when material.

### State and flow map

Show:

- important state and identity owners;
- source-of-truth or authority boundaries;
- read, write, asynchronous, and background-convergence directions;
- two to four representative flow overlays.

The final assembly should introduce few or no new durable concepts. If a node first appears there, return it to an earlier admission article or remove it.

## 9. Module Responsibility Card

Every major module needs a compact card or table row answering:

```text
Why it exists:
Input:
Output:
State it owns:
Who calls it:
What it calls:
What it explicitly does not own:
Current runtime role:
Current repository or repositories:
Representative entrypoints:
Generated artifacts:
Representative tests:
Common changes primarily owned here:
Adjacent contracts that may also change:
```

This is an internal completeness record. Render a responsibility map in the form that best supports comparison; do not force every module into a visible form with repeated field labels.

Do not equate modules with every filesystem directory. A conceptual responsibility may span several packages; a large package may host several product domains.

## 10. Annotated Repository Tree

The tree must teach rather than inventory:

```text
architecture responsibility
  -> current repository and directory/package
      -> representative file, type, or function
          -> test and verification path
```

Mark:

- implementation homes;
- executable/build/deployment units;
- generated code that should not be the first edit target;
- test directories;
- external repositories;
- unverified or inaccessible paths;
- first-pass skip areas.

Use current verified paths at the inspected revision. If the repository is too large, show a responsibility-oriented slice and explain what was deliberately omitted.

## 11. Representative Code Routes

Repeat the already-understood conceptual flows through real code. Do not use code to reintroduce unexplained architecture.

For each route show:

```text
user or external event
  -> entry surface
  -> contract and validation
  -> use-case or domain coordinator
  -> state and/or external integration
  -> asynchronous or convergence path where applicable
  -> visible result
  -> representative tests
```

Label generated hops and external repository hops. Use representative files rather than dumping complete call graphs.

## 12. Change Navigation Cases

Use at least three cases:

1. a local presentation or UI behavior change;
2. a cross-layer business capability or persisted-field change;
3. a background synchronization, external integration, workflow, or delivery change.

For every case distinguish:

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

Conditions must be meaningful. For example, data-model work is required only when the new capability persists state; synchronization work is required only when the external fact must be read back; deployment work is required only when runtime roles, configuration, or delivery artifacts change.

## 13. Guide Contract

`00-阅读指南.md` must:

- introduce the solution-free goal, not the final jargon-heavy diagram;
- mark both architecture construction and repository landing as required;
- state what mental models the reader will build;
- provide the complete required order and optional mechanism paths;
- state inspected repositories and revisions later in the guide;
- link evidence and unknowns;
- avoid claiming that the minimal loop alone gives whole-project understanding.

The guide may state the overall reading outcome once. Individual articles must not repeat lesson objectives or completion standards.

Keep every article flat in one directory with stable numeric prefixes and relative links.

## 14. Evidence Placement

Keep the causal narrative readable, but attach enough evidence for maintainers to verify it.

- Put paths and symbols after the responsibility is understood.
- Surface uncertainty in the main text when hiding it would make the model false.
- Put detailed commits, tests, and source citations in compact engineering notes or the repository-navigation section.
- Never write "the developers wanted" without documented intent.
- Explicitly identify external repositories that were not inspected.
- Preserve the same connected voice in repository navigation: explain the responsibility and organization pressure before presenting a tree, matrix, path list, or test map.

## 15. Delivery Audit

### Narrative audit

- Does the opening assume ordinary programming knowledge without reteaching frontend/backend, HTTP, or databases?
- Is familiar context compressed while unfamiliar project or domain mechanisms receive enough explanation?
- Does every scenario detail affect the architecture model or the current pressure?
- Does every paragraph add a fact, changed condition, causal relationship, mechanism, boundary, code mapping, or necessary transition?
- Are arbitrary code identifiers delayed until they provide domain recognition or repository-navigation value?
- Is prior success demonstrated through an observable result rather than a repeated "this solution works" announcement?
- Do unfamiliar concepts include the smallest useful process, state, relationship, quantity, or example needed for understanding?
- Does each diagram pass the deletion test from `narrative-writing-contract.md`?
- Did any admission card, concept budget, responsibility card, decision card, or exit capability leak into visible prose?
- Does each article end with the current system state or next pressure rather than a completion standard or fixed summary?
- Does the repository-navigation spine continue the narrative rather than becoming a directory inventory?

### Causal audit

- Does the initial goal contain an unearned solution?
- Did the previous system genuinely work?
- Does each growth article add one primary pressure?
- Is the problem visible rather than a list of concerns?
- Does ordinary-language responsibility precede the project term?
- Can the reader explain the new element as "because X, the system needs Y"?

### Architecture-completeness audit

- Are all major domains represented without pretending the center scenario is the whole product?
- Are all important runtime roles, state owners, integrations, cross-cutting authorities, and delivery boundaries included?
- Are two to four representative flows complete?
- Do final diagrams contain only previously explained nodes?
- Does every major module have a responsibility card?

### Repository-organization audit

- Are primary and secondary organizing axes explained?
- Is at least one viable alternative compared fairly?
- Are runtime, build, deployment, contract, generated, external, and evolutionary boundaries distinguished?
- Is inferred rationale labeled as inference?
- Are migration seams shown rather than idealized away?

### Navigation audit

- Does every major responsibility map to current repositories and paths?
- Are representative code routes dependency-aware?
- Do change cases identify primary, required, conditional, external, unaffected, and unknown areas?
- Are tests and validation paths included?
- Are local paths verified and external paths labeled?

### Package audit

- Does `00-阅读指南.md` exist and mark both spines required?
- Do relative links resolve and code fences balance?
- Are all Markdown files flat in the selected learning directory?
- Are source repositories unchanged?
- Are document checks reported as document checks rather than runtime tests?

If a core audit fails, compress, expand, merge, split, reorder, or rewrite the affected material. Do not patch a missing mental model or low-information prose with a glossary, a long caveat, another summary, or a visible checklist.
