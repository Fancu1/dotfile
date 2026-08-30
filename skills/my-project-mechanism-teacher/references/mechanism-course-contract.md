# Complete Mechanism Course Contract

Read this reference for every complete mechanism course. It turns the routing and teaching principles in `SKILL.md` into an investigation, course-design, repository-navigation, debugging, and delivery contract.

## 1. Required Learning Outcome

The required route has two connected achievements:

```text
run the requested mechanism mentally from start to observable finish
  -> locate the same control, data, identity, state, and authority changes in current code
  -> use that map to change, debug, and verify the behavior
```

The mechanism-construction spine is not enough by itself. The repository-landing spine is also required. Optional material contains only branches and exhaustive evidence that the user's question does not require.

Do not impose a fixed article count. Derive articles from independent mechanism questions, state models, and repository boundaries.

## 2. Investigation Ledger

Record internally before designing the course:

```text
Exact user question:
Business or technical start event:
Observable finish:
Immediate success versus all related work finished:
Default programmer knowledge:
Domain knowledge not assumed:
Familiar context to compress:
Unfamiliar mechanism to expand:
Code identifiers deliberately delayed:

Callers:
Callees:
Runtime roles and processes:
External systems:
Inputs and outputs:
Identifiers and correlation rules:
State stores:
Authority sources:
State transitions:
Transactions and consistency boundaries:
Events, queues, schedulers, and workflows:
Retry and idempotency:
Cancellation and compensation:
Concurrency and ordering:
Partial-success boundaries:

Current repository roots:
Packages and representative entrypoints:
Generated-code boundaries:
External-repository boundaries:
Build and deployment boundaries:
Evolutionary seams:
Representative tests:
Debugging observations:

Documented intent:
Verified suitability:
Architectural inference:
Pedagogical reconstruction:
Historical evidence:
Unknowns:
```

Inspect repository rules, manifests, workspace definitions, entrypoints, interfaces, schemas, migrations, background executors, external adapters, state stores, tests, fixtures, configuration, deployment definitions, ADRs, RFCs, issues, and meaningful history where relevant.

Follow imports and runtime registration across language and process boundaries. Verify a current route from code and tests; do not infer it from a directory name or an earlier architecture course.

## 3. Classify the Question Before Selecting Required Material

Use the closest shape or combine shapes when the user's question genuinely spans them.

### Runtime flow

Required:

- concrete start and observable finish;
- participants and call direction;
- material input and output transformations;
- state before, during, and after;
- process and external-system boundaries;
- exact current repository route and tests.

### State machine

Required:

- every state and transition relevant to the requested behavior;
- trigger and actor for each transition;
- where the state is persisted and which representation is authoritative;
- legal, exceptional, and terminal transitions that change observable meaning;
- callers that initiate transitions, consumers that interpret them, and transition tests.

Do not demote exceptional transitions merely because they are failures. Raw states unrelated to the question may remain optional.

### Algorithm

Required:

- input, output, invariant, and stopping condition;
- one concrete data walkthrough;
- important complexity, allocation, approximation, or ordering trade-off when central;
- behavior at meaningful boundaries;
- implementation entrypoint, helpers that own the invariant, and representative tests.

Do not transliterate the source line by line. Use pseudocode only when it exposes a decision, loop, mutation, or invariant more clearly than prose.

### Technology choice

Required:

- a simpler alternative that is genuinely viable under stated conditions;
- the new pressure that makes it insufficient;
- how the current choice operates inside this repository;
- principal benefit, cost, and control;
- integration, configuration, operational, and test boundaries material to the question;
- the evidence class for the claimed reason.

Do not describe current suitability as the original developers' intent without explicit evidence.

### Retry, compensation, cancellation, or partial success

Required:

- the shortest baseline that establishes the ordinary result;
- the exact failure or interruption point;
- external and local state at that point;
- what is retried, skipped, cancelled, or compensated;
- idempotency key or deduplication boundary when present;
- final state, remaining ambiguity, and recovery evidence;
- current code and tests for the failure path.

### External synchronization or convergence

Required:

- external authority and local view;
- stable identity or matching rule;
- trigger, polling, event, or workflow path;
- normalization and writeback;
- visible consumer of the local state;
- stale window, deletion semantics, and error behavior when material;
- current task, mapper, persistence, read path, and tests.

## 4. Required-Scope Admission Test

A mechanism detail or branch belongs in required reading when any is true:

- the user directly asked about it;
- it decides the observable finish;
- it changes data safety, consistency, identity, ordering, or authority;
- it owns or transitions important state;
- it defines a cross-process, cross-repository, or external contract;
- it is the principal reason for the technology or module boundary;
- a maintainer must inspect it for the requested change;
- the mechanism cannot be debugged correctly without it.

Otherwise place it in an optional reality article or exhaustive evidence article. Do not create an article merely because a branch exists.

## 5. Internal Mechanism Article Contract

Record for each article:

```text
Core question:
Shortest baseline:
Stable example in ordinary language:
Requested behavior that must stay required:
Main participants:
Control before and after:
Data before and after:
Identity used:
State before:
State transitions:
State after:
Authority and process boundaries:
Central design reason:
Current guarantee:
Current non-guarantee:
Familiar context to compress:
Unfamiliar mechanism to expand:
Code identifiers deliberately delayed:
Representative current code route:
Optional branches:
Diagram question:
Information gained in each paragraph:
Natural ending:
Internal completion audit:
```

This is private authoring material. Never render it as a repeated card, lesson objective, `完成标准`, reader capability, concept budget, memory rule, or article footer.

An article normally has one dominant question. Supporting concepts may share it when they form one inseparable execution or state model. Split separate questions instead of enforcing a fixed concept count.

## 6. Trace Card for the Requested Execution

Prepare an internal row for each important step:

```text
Step in ordinary language:
Participant:
Trigger or input:
Action or decision:
Output:
State before and after:
Authority:
Process or external boundary crossed:
Failure that belongs to the asked mechanism:
Design reason:
Current code owner:
Evidence:
```

Use the rows to prove the end-to-end route, not as visible article sections. A visible sequence or state diagram may summarize the route only after prose establishes the participants and state meanings.

## 7. Concept-to-Code Landing Card

For every important conceptual step, record:

```text
Conceptual step:
Runtime role or process:
Current repository:
Package or directory:
Representative file or symbol:
Caller:
Callee:
State or store:
Primary ownership:
Required adjacent contract:
Conditional change:
Generated boundary:
External boundary:
Evolutionary seam:
Tests:
Debugging evidence:
Unknown:
```

The visible repository route must follow:

```text
mechanism responsibility already understood
  -> runtime role that performs it
      -> current repository and representative entrypoint
          -> state and contract effects
              -> modification consequence
                  -> debugging and verification evidence
```

Do not switch to an unexplained directory dump. Use only architecture-relevant tree depth and representative files.

## 8. State and Authority Model

For every material state, answer internally:

```text
State meaning:
Authoritative owner:
Local or derived representations:
Writer:
Readers:
Identity used to correlate copies:
Transition trigger:
Persistence boundary:
Staleness or consistency window:
Failure meaning:
```

Do not equate persistence with authority. A database may store a management view while an external platform remains authoritative for runtime state. Conversely, a local operation record may be authoritative for the product's workflow even when external work occurs elsewhere.

If authority differs by field, say so. Do not describe an entire object as uniformly authoritative when the evidence supports field-level ownership.

## 9. Representative Current Code Route

Repeat the already-understood execution through real code:

```text
user, scheduler, event, or external change
  -> entry surface or registered task
  -> contract and validation
  -> use-case, algorithm, or workflow coordinator
  -> state store and/or external integration
  -> background, retry, compensation, or convergence step when required
  -> readback or visible result
  -> representative tests
```

Use current verified paths at the inspected revision. Mark generated hops, external repositories, inaccessible code, and inferred links. Prefer representative entrypoints over an exhaustive call graph.

## 10. Change Navigation Cases

Include at least two question-relevant cases:

1. a behavior, field, state, algorithm, or decision change;
2. a failure-handling, debugging, external-integration, performance, or runtime-boundary change.

For each case decide internally:

```text
Primary owner:
Required contract changes:
Conditional adjacent changes:
Generated consumers:
External repositories:
Explicitly unaffected areas:
Debugging observations:
Verification paths:
Unknown or blocked boundaries:
```

Conditions must be causal, not defensive lists. Examples:

- persistence changes only when the value must be stored;
- public schemas change only when callers send or receive the value;
- synchronization changes only when an external fact must be read back;
- workflow or retry code changes only when execution or terminal semantics change;
- deployment artifacts change only when runtime roles, configuration, or delivery boundaries change.

Point to the source of generated artifacts, not the generated file as the primary edit target.

## 11. Debugging Navigation

Build debugging routes from observations, not log inventories.

For each checkpoint explain:

```text
Observation:
Where to obtain it:
What success proves:
What failure narrows the problem to:
Next checkpoint:
```

Trace from trigger to visible result. Include process liveness, registration, input contract, identity, external response, transformation, persistence, event or query propagation, and UI consumption only when they participate in the verified mechanism.

Do not invent log names, metrics, tracing spans, or operational commands that the repository does not provide. When observability is insufficient, state the gap.

## 12. Verification Map

Distinguish evidence types:

- static document checks prove package shape, links, fences, and paths;
- focused unit tests prove isolated branches and transformations;
- integration tests prove boundaries with real or controlled dependencies;
- builds prove compilation, generation, and packaging compatibility;
- runtime validation proves the mechanism in an executing system;
- external-environment validation proves behavior that source and mocks cannot establish.

Map each change case to the smallest relevant tests plus any broader check needed for a changed contract. Do not claim that Markdown checks execute the source system. Do not run live services or external infrastructure unless the user authorizes it.

## 13. Guide Contract

`00-阅读指南.md` must:

- state the exact question in ordinary language;
- define the concrete start and observable finish;
- mark both mechanism construction and repository landing as required;
- explain which mental models the required route builds;
- list optional branches by understandable category, without teaching them in the guide;
- record inspected repositories and revisions later;
- distinguish evidence classes and identify external or unknown boundaries;
- link every article in intended reading order.

Do not expose a stable-example card, concept budget, exit ability, completion criterion, source-path catalog, or jargon-heavy final call chain on the first screen.

## 14. Course Shape

Choose filenames that describe reader questions rather than internal phases. A typical complete course may contain:

```text
00-阅读指南.md
01-<为什么会出现这个问题>.md
02-<机制怎样完成一次执行>.md
03-<状态和权威怎样变化>.md
04-<当前代码怎样实现这条路径>.md
05-<修改时应该从哪里开始>.md
06-<结果不对时怎样排查>.md
07-<怎样验证修改>.md
08-<一个未被询问的现实分支，可选>.md
```

This is an example, not a required count or title template. Merge or split according to the mechanism's cognitive and repository boundaries.

## 15. Delivery Cold-Read Audit

Read the course in order and answer:

### Scope and model

- Does the opening answer the user's exact mechanism question rather than a nearby architecture topic?
- Is the shortest baseline sufficient without becoming a general project introduction?
- Does required reading include any failure or state behavior explicitly requested?
- Can the reader follow control, data, identity, state, and authority to the observable finish?
- Are current guarantee and non-guarantee clear without unsupported historical claims?

### Narrative

- Does the first paragraph assume only ordinary programming knowledge?
- Is familiar context shorter than the unfamiliar mechanism?
- Does every paragraph add a fact, causal link, state change, boundary, or navigation consequence?
- Are ordinary responsibilities introduced before project terms and code identifiers?
- Does every diagram pass the deletion test?
- Did any internal card, concept count, memory rule, exit ability, or lesson footer leak into prose?

### Repository and actionability

- Does each material conceptual step map to verified current code and state?
- Does repository prose explain responsibility before listing paths?
- Do both change cases distinguish primary, required, conditional, generated, external, unaffected, and unknown areas?
- Does the debugging path explain what each observation proves?
- Are tests and validation tied to claims rather than listed generically?
- Are generated and external boundaries marked?

### Truth and safety

- Are verified behavior, documented intent, suitability, inference, pedagogical reconstruction, and unknown kept distinct?
- Are code paths current at the inspected revision?
- Are the source repositories unchanged?
- Are output files flat, links valid, and code fences paired?

If a core answer is no, reorder, expand, compress, split, or rewrite. Do not repair an incomplete mechanism with a glossary, a longer summary, or more visible checklists.
