# Decision framework

Use this framework to gather only decision-relevant project context and prevent existing code, mature products, or “quality” arguments from silently expanding the requirement.

## 1. Lightweight project inspection

Start from the requirement, not from the repository root.

### Inspect in this order

1. Read the smallest available project description or manifest needed to identify the stack and major responsibility boundaries.
2. Search for requirement vocabulary, existing user-visible behavior, public routes or commands, persisted fields, and likely owning modules.
3. Read the likely owner files plus only direct contracts, consumers, tests, or configuration that constrain the decision.
4. Inspect more context only when a named unknown would materially change scope, placement, compatibility, or acceptance.

Do not automatically read every top-level directory, trace an entire runtime flow, inventory all abstractions, or reconstruct the architecture. A real flow is useful only when the new requirement changes or extends that flow and its behavior constrains the solution.

### Stop inspection when all are true

- The current problem and observable target outcome can be stated plainly.
- The likely responsibility owner and relevant module or subtree are known.
- Existing hard contracts and important project constraints are identified.
- The candidate files or file responsibilities can be proposed with reasonable confidence.
- Remaining unknowns are either non-blocking or require a product choice from the user.

### Expand inspection only for a concrete trigger

Examples include unclear ownership between two modules, a public or persisted contract, a security or permission invariant, an existing behavior that must remain compatible, or uncertainty about where the project already verifies the same behavior. State the trigger before expanding.

Classify every project statement as:

- `已验证事实`: directly supported by code, configuration, tests, or current documentation.
- `推断`: likely but not yet confirmed; do not use it as a hard constraint.
- `未知`: material information that cannot be discovered safely or cheaply and may require user input.

## 2. Restrained external research

Research only to answer a named question that can change the current decision. Prefer current primary sources, official documentation, or the actual source code of one or two closely comparable projects.

For each reference, extract only:

- What concrete problem it solves.
- The smallest relevant mechanism.
- Its prerequisites and operating assumptions.
- Its implementation and maintenance cost.
- Which part fits the current project now.
- Which part is too heavy or premature.

Stop when the decision can be made. Do not produce a market survey, collect patterns without a question, or treat popularity and repository structure as proof that a design belongs in the current project.

## 3. Candidate necessity dimensions

Evaluate each candidate behavior, safeguard, abstraction, infrastructure component, or structural adjustment on every dimension. Keep the dimensions separate; never convert them into numbers or a total score.

### 与当前目标的关系

- `没有关系`: Removing it does not change the stated result.
- `有帮助`: It improves convenience, completeness, maintainability, or future capability, but the result can still be delivered.
- `缺了目标不成立`: The stated observable result cannot be achieved without it.

### 当前证据

- `只是设想`: Supported only by a hypothetical future need.
- `有现实迹象`: Current usage, code, feedback, or constraints make the need plausible.
- `已发生或有硬契约`: A real failure has occurred, or an API, persisted-data, deployed-behavior, permission, safety, or compatibility contract requires it.

### 不做的后果

- `无明显影响`: The core result remains usable.
- `可人工处理或恢复`: A visible, bounded manual path can handle the problem.
- `阻断或不能接受`: Delivery fails, data becomes irrecoverable, or a hard contract or safety boundary is violated.

### 以后补做的成本

- `容易后补`: It can be added locally without changing contracts or stored data.
- `需要一定调整`: Some files, tests, or internal interfaces must change, but migration remains bounded.
- `后补代价很大`: It would require irreversible data changes, incompatible public contracts, or a broad migration.

### 当前结构影响

- `留在现有职责`: The behavior belongs to an existing owner and can remain local.
- `需要跨文件调整`: Multiple existing responsibilities must coordinate.
- `引入新模块或基础设施`: It creates another service, directory, scheduler, queue, persistence layer, plugin system, or comparable operational concept.

### 是否存在更小方案

- `有`: A smaller behavior or manual recovery path satisfies the current outcome.
- `暂不确定`: Investigate only the uncertainty that affects this choice.
- `没有`: Smaller alternatives fail the outcome or violate a hard contract.

## 4. Classification rules

Use judgment rather than a formula.

### 当前必须实现

Use when omission makes the target outcome impossible, violates a hard existing contract, creates an unacceptable irreversible consequence, and no smaller viable alternative exists.

### 当前只做最小版本

Use when the concern is real but a narrow behavior, visible state, manual recovery path, or local safeguard is enough for the current delivery. State exactly what the minimum version covers and excludes.

### 明确后置

Use when the item is helpful but not required, omission is recoverable, later addition is feasible, or the full version introduces disproportionate structure. State both why it is unnecessary now and the concrete signal that should reopen it.

Group deferred capabilities that share the same evidence, reason, structural cost, and reevaluation condition. Do not expand the specification by listing every recognizable mature-system feature.

### 本次不做

Use when the item is unrelated to the target, supported only by speculation, or belongs to a separate problem. This means outside the current requirement, not “never”.

Treat phrases such as “more robust”, “production quality”, “best practice”, and “top projects do this” as claims that still require evidence through the dimensions above.

## 5. Existing-code anti-anchoring

Treat current code as evidence of behavior and constraints, not proof of good design.

### Respect as constraints when verified

- Public APIs and actual consumers.
- Persisted data and required compatibility.
- Deployed behavior relied upon by users or systems.
- Permission, security, integrity, and data invariants.
- Existing tests that express intentional behavior rather than accidental structure.

### Challenge when appropriate

- Directory shape and file count.
- Internal wrappers, indirection, and one-implementation interfaces.
- Historical naming and legacy layering.
- Patterns created for hypothetical extensibility.
- Existing structure that is already hard to understand or mismatched with the new responsibility.

Before reusing an existing pattern, ask:

1. Is it a real contract or merely historical structure?
2. Does it solve the same responsibility and change for the same reason?
3. Would reusing it import unrelated complexity?
4. Is a smaller local implementation clearer?
5. Is the pattern itself part of the current problem?

Handle bad existing code by avoiding it when unrelated, correcting it locally only when it directly blocks the requirement, and deferring broad cleanup.

Treat every file action as a candidate scope item. Tests are normally justified when they prove an acceptance behavior. Documentation, changelogs, configuration cleanup, formatting, and adjacent maintenance are not automatic: include them only when the current requirement changes a documented contract, an existing project rule requires them, or the user explicitly asks for them.

## 6. File, directory, deletion, and refactor rules

Organize by cohesive responsibility and reason to change. A large cohesive file is acceptable; line count alone never justifies splitting.

### Keep logic in an existing file when

- The file already owns the responsibility.
- The new behavior changes for the same reasons as the existing behavior.
- The change remains understandable without introducing unrelated concerns.

### Create a file when

- It introduces a distinct, cohesive responsibility with its own reason to change.
- Keeping it in the current file would mix unrelated responsibilities.
- A real interface or lifecycle boundary requires separation.

Do not create a file merely to shorten another file, isolate a tiny helper, mirror a mature project, or prepare for hypothetical reuse.

### Create a directory only when

- A real module boundary contains multiple cohesive files.
- The dependency direction and ownership are clear.
- Keeping those files with the parent area would obscure a meaningful boundary.

### Delete, move, or merge only when

- The current requirement makes the old structure redundant or misleading.
- All known consumers and references have been checked.
- Equivalent behavior can be verified.
- The cleanup remains a direct, bounded consequence of the requirement.

### Refactor only when

- The existing structure directly blocks the required behavior or safe verification.
- The refactor is the smallest bounded correction.
- Its before-and-after file impact and reason can be explained.

“Cleaner”, “more elegant”, “more reusable”, or “might be useful later” is not enough.

## 7. Minimum safeguards

Include only safeguards needed to keep the core path usable and verifiable:

- Failures that directly block the required result.
- Irreversible data loss or corruption risks.
- Existing hard API, persistence, permission, security, or compatibility contracts.
- A minimum visible or manual recovery path when automatic recovery is unnecessary now.

Do not add exhaustive defensive branches, generalized retry frameworks, schedulers, compensation systems, observability platforms, or abstractions unless the current dimensions justify them independently.

Do not mention a hypothetical future contract, scale problem, failure mode, or best-practice caveat unless it changes a current scope, file, safeguard, or acceptance decision.
