---
name: requirement-to-spec
description: Turn a software feature request into a bounded, implementation-ready requirement specification through lightweight repository inspection, restrained external research, scope prioritization, and short interactive confirmation. Use when a user wants to discuss what a feature should include now, what should be deferred, where the logic belongs, how files or directories should change, or wants a PRD/development specification before coding. Do not use for direct implementation, generic architecture teaching, code review, or exhaustive repository analysis.
---

# Requirement to Spec

Turn an initial software requirement into a concise, decision-complete implementation specification without writing code or letting the design expand sideways.

## Operating boundaries

- Keep discussion and drafts in the conversation by default.
- Treat approval such as “认可”, “同意”, or “没问题” as confirmation of the current decision only.
- Create or update a specification file only when the user explicitly asks to write it to a file.
- Stop this workflow before implementation. Treat an explicit request to implement as a separate authorization and hand the confirmed specification to the implementation workflow.
- Do not require the user to choose an internal mode, phase, risk level, or command.
- Do not depend on another Skill, a code graph, persistent state, or a particular language or framework.

## Load the references

- Read [references/decision-framework.md](references/decision-framework.md) before inspecting a repository or judging what is necessary, deferred, reusable, or structurally justified.
- Read [references/spec-template.md](references/spec-template.md) before sending the first confirmation card and again before producing the final specification.

## Workflow

### 1. Establish the requirement

- Restate the desired outcome and current problem in plain language.
- Separate user-visible success from a proposed implementation.
- Identify only unknowns that can materially change the boundary, responsibility placement, data contract, or acceptance result.
- Investigate discoverable project facts before asking the user. Ask at most one material question per round.

### 2. Inspect the project lightly

- Inspect only enough repository context to identify the likely responsibility owner, relevant constraints, candidate change area, and important unknowns.
- Search from requirement terms, existing behavior, public contracts, and likely module names; read only the most relevant files and their direct constraints or consumers.
- Stop when the inspection stop conditions in the decision framework are satisfied.
- Expand the inspection only when a concrete unresolved decision requires it. Do not default to a full repository scan, architecture reconstruction, or end-to-end call-chain trace.
- Record project statements as verified facts, inferences, or unknowns. Do not turn an inference into a constraint.

### 3. Research externally only for a decision

- Research only when an external comparison can change a current scope or implementation decision or avoid a credible blind spot.
- Start with one explicit research question and inspect at most one or two closely relevant products, official documents, or open-source projects.
- Extract the problem solved, mechanism, prerequisites, cost, and applicability. Do not copy a mature product's architecture or directory structure as proof of correctness.
- Skip external research when the project facts and requirement already make the decision clear.

### 4. Classify the candidate scope

- List candidate behavior, safeguards, abstractions, infrastructure, and structural changes that the proposed solution introduces.
- Evaluate each candidate independently using all textual dimensions in the decision framework. Never calculate a total score.
- Classify each candidate as one of:
  - `当前必须实现`
  - `当前只做最小版本`
  - `明确后置`
  - `本次不做`
- State why a deferred item is unnecessary now and what concrete future condition should trigger reconsideration.
- Group related deferred items when they share the same reason and reevaluation condition. Do not enumerate future capabilities merely to show awareness.
- Prefer the smallest version that still achieves the stated outcome, respects hard contracts, and avoids unacceptable or irreversible failure.

### 5. Design the bounded solution

- Recommend one solution and include at most one strong alternative when the trade-off is genuinely material.
- Assign logic by responsibility and reason to change, not by line count or the current repository shape.
- Show only the relevant before-and-after directory subtree and file-level actions.
- Re-run the scope classification whenever the solution introduces another module, directory, abstraction, infrastructure component, broad refactor, or defensive mechanism.
- Treat every planned file action as scope, including documentation, tests, configuration, and cleanup. Include it only when it implements the behavior, proves acceptance, preserves a hard contract, or is explicitly requested.
- Include only minimum safeguards required for the core path, hard contracts, irreversible data risks, or minimum recovery. Do not add a standalone catalogue of hypothetical failures.
- Omit hypothetical future caveats unless they change a current decision. A deferred item's reevaluation condition is enough; do not repeat “future may need” warnings elsewhere.

### 6. Confirm one decision at a time

- Use the confirmation card from the specification template.
- Keep each round to one main decision, no more than five short bullets, and at most one clear question.
- Lead with a recommendation and its reason. Make “now”, “deferred”, and “not included” visually unambiguous.
- Replace superseded conclusions with the latest consensus; do not keep appending a long decision history.
- Continue until the goal, non-goals, necessary scope, solution, structural impact, implementation order, and acceptance approach are confirmed.

### 7. Produce the requirement implementation specification

- Produce the final Markdown only after the user explicitly asks to generate or finalize the specification.
- Follow the structure and writing constraints in the specification template.
- Make the result sufficient for another developer or AI to implement without reopening scope or file-responsibility decisions.
- Use short pseudocode or function names only when they remove a real ambiguity. Do not write production code, line-by-line patches, commit titles, or unnecessary helper functions.
- End after delivering the specification. Do not automatically modify the repository.

## Quality check

Before each confirmation card or final specification, verify:

- The investigation was driven by a concrete requirement decision.
- Existing code was treated as evidence, not automatically as a good pattern.
- Every new abstraction, directory, infrastructure component, safeguard, or adjacent refactor has a present requirement-level justification.
- Helpful work was not mislabeled as required merely because it improves completeness.
- File and directory decisions follow responsibility boundaries rather than size targets.
- Documentation, tests, and cleanup were not added automatically; every file action has a current justification.
- The same boundary or rationale is not repeated across multiple sections.
- The response is short enough to read while preserving the decision, reason, impact, and one required user choice.
- No file or code change is implied without explicit authorization.
