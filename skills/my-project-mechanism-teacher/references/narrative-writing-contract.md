# Narrative Writing Contract

Read this reference before generating or rewriting any mechanism-course article. It governs learner-facing prose. Investigation ledgers, trace cards, state cards, change-impact fields, and cold-read audits remain private authoring tools.

## 1. Default Reader

Write for a programmer who understands ordinary software development but has not read this repository and does not know its domain.

Assume the reader recognizes:

- frontend and backend roles;
- HTTP requests, processes, queues, databases, and tests;
- development, test, and production environments;
- source files, modules, generated output, and build artifacts.

Do not reteach those foundations merely because the mechanism is unfamiliar. Explain a lower-level concept only when the user requests it or the project-specific behavior cannot be understood without it.

Before drafting, record internally:

```text
Familiar to a general programmer:
Unfamiliar project or domain concepts:
Code identifiers that should appear only later:
Concepts that require a concrete state or data example:
```

## 2. Allocate Detail Where It Teaches

Use two speeds:

```text
familiar context -> establish it quickly
new pressure or failure -> make the change concrete
unfamiliar mechanism -> slow down and explain its execution and state
project term -> name it after recognition
code location -> introduce it after responsibility is clear
```

Do not impose a word ratio. Familiar context normally needs no more than one short paragraph. If the setup is longer than the mechanism, review whether the article is telling a story instead of teaching behavior.

Programmer-friendly prose is not compressed jargon. It contains every necessary intermediate state and causal step while omitting explanations of ordinary software knowledge.

## 3. Scenarios Are Compressed Mechanism Setups

A scenario earns its place only when it fixes the mechanism's start, important transitions, or observable finish.

Keep:

- the user, operator, process, or external system that triggers the behavior;
- the current state and expected result;
- the one changed condition, failure, or scale pressure that makes the mechanism relevant;
- concrete values when they explain time, ordering, identity, capacity, retry, or partial success.

Remove:

- atmosphere and character detail;
- routine clicks or request steps that do not change the mechanism;
- business background that does not affect state or control flow;
- invented names used only for realism;
- repeated reminders of the same goal.

The stable example is a state-and-flow anchor, not a short story.

## 4. Keep Internal Scaffolding Invisible

Do not render authoring fields as article structure. In particular, do not mechanically output:

```text
本篇只讨论……
本篇暂不讨论……
完成标准……
读者现在应该能够……
Memory rule……
Exit ability……
本章小结……
```

The phrases are not banned from every possible sentence. They are forbidden as repeated boilerplate. Remove a sentence when it adds no fact, relationship, boundary, modification consequence, or necessary reading instruction.

Do not turn every article into visible `Pressure / State / Guarantee / Boundary / Evidence` cards. Weave only the relevant facts into connected prose.

## 5. Terminology and Code Names

Establish recognition before naming:

```text
ordinary-language problem
  -> responsibility the system needs
  -> domain or project term
  -> type, function, status, and file path
```

Weak:

> `REFRESH_ITEM` calls `mergeRemoteItem` to update an entity.

Better:

> The application periodically rereads the external record and uses its stable identity to replace fields in the local management view. The repository implements that work as the `REFRESH_ITEM` task; the field conversion is concentrated in `mergeRemoteItem`.

Use ordinary names such as “the uploaded document,” “the operation record,” or “the external resource” before arbitrary identifiers. Introduce internal names when they help the reader locate current code, distinguish states, or modify the mechanism.

Necessary technical terms are not noise. Unearned terms are.

## 6. Paragraph Information Gain

Every paragraph must add at least one:

- necessary fact about the current mechanism;
- concrete trigger, decision, or state transition;
- causal relationship;
- explanation of how an unfamiliar mechanism operates;
- authority, process, consistency, or failure boundary;
- concept-to-code mapping;
- modification, debugging, or verification consequence;
- natural transition to the next unresolved behavior.

Delete or merge a paragraph when it only:

- makes the scene more vivid;
- paraphrases the previous conclusion;
- announces that the teaching plan was followed;
- repeats a caveat already established;
- lists modules or files without explaining a relationship.

Paragraphs must also connect. Passing the information-gain check does not justify a sequence of isolated mechanism cards.

## 7. Show Operation Through Results

Demonstrate that a baseline or mechanism works through an observable result rather than an author announcement.

Weak:

> The asynchronous design works correctly.

Better:

> The upload request returns an operation identifier immediately. Parsing continues in a background process, and a later status request reads the same operation record to show the final result.

Weak:

> The synchronization has now converged.

Better:

> The next read returns the external value that was written into the local view, so the page no longer shows the earlier state.

Do not append “therefore the design works” after the result has already shown it.

## 8. Expand Unfamiliar Mechanisms

An unfamiliar mechanism normally needs more than a definition. Explain the smallest useful combination of:

- state before the mechanism runs;
- trigger and participant responsible for each material step;
- data or identity used to correlate steps;
- state after each important decision;
- process, transaction, or external boundary crossed;
- which representation is authoritative;
- observable finish;
- principal non-guarantee.

Weak:

> The system adds a queue so long work can run asynchronously.

Better:

> The request first creates an operation record and returns its identifier. A background executor receives that identifier, performs the long work, and updates the same record. Later requests read the record instead of waiting on the original connection. The queue separates request lifetime from work lifetime; it does not by itself decide the business result or recovery policy.

Do not expand every branch. Expand until the reader can run the requested behavior mentally and place its responsibility in the repository.

## 9. Explain Authority, Not Just Storage

Do not say only that state “is in the database.” Explain what the stored state means.

Example:

> The remote catalog remains authoritative for whether the resource is active. The local database stores the application's last observed view so reads do not contact the remote service every time. A refresh can therefore replace the local value, while an unrefreshed value may be temporarily stale.

If authority differs by field or phase, explain the difference. An external system can own runtime state while a local operation record owns workflow progress.

## 10. Failure Questions Must Start Near the Failure

When the user asks about retry, compensation, cancellation, or partial success, establish only the shortest successful baseline, then move to the requested interruption.

Weak structure:

```text
several articles of happy path
  -> optional failure appendix
```

Better structure:

```text
short baseline
  -> failure after an external side effect
  -> local and external states now disagree
  -> retry, idempotency, or compensation decision
  -> final state and remaining boundary
  -> current code and tests
```

Do not demote the user's core question because failures are less common than success.

## 11. Diagram Admission and Deletion Test

Before adding a diagram, answer internally:

```text
What flow, state transition, authority relation, or boundary is difficult to see from adjacent prose alone?
What information would be lost if the diagram were removed?
```

Useful diagrams may show:

- request lifetime versus background-work lifetime;
- a state transition and its trigger;
- external authority versus local view;
- partial success and compensation;
- control and data crossing process boundaries;
- conceptual mechanism steps projected into repository locations.

Remove a diagram when it only rearranges the same nouns or repeats a paragraph line by line. Use the smallest useful set of already explained nodes; do not impose or target a fixed node count.

State diagrams come after prose explains what the states mean. Sequence diagrams must distinguish control messages from important persisted state when that distinction matters.

## 12. Pseudocode and Tables

Use pseudocode only when it clarifies decisions, loops, state changes, idempotency checks, ordering, or side effects. Never transliterate source line by line.

Use tables for exact mappings or comparisons, such as:

- state to trigger and owner;
- conceptual step to code owner;
- change category to required and conditional impact;
- observation to diagnosis and next checkpoint.

Do not use a table to replace causal narrative. Introduce why the comparison matters before the table and explain the consequence afterward.

## 13. Natural Article Endings

End with one of:

1. the concrete state the mechanism has reached;
2. an important current boundary;
3. the next unresolved behavior;
4. the point where the established model now enters real code.

Result ending:

> The request can now finish while the work continues, and every later reader observes progress through the same operation record.

Boundary ending:

> That preserves the operation across one HTTP request. It does not yet show whether a new executor can resume after the original process stops halfway through.

Repository transition:

> The mechanism now has three stable responsibilities: accept the request, execute the work, and persist progress. The repository separates those responsibilities across its HTTP entrypoint, task processor, and shared operation store.

Do not append completion criteria, lesson objectives, review questions, reader-capability statements, or fixed summaries.

## 14. Keep Repository Navigation in the Same Voice

Repository landing is not permission to switch from teaching prose to an inventory.

Use this connected progression:

```text
responsibility already understood
  -> runtime or organization pressure
  -> current repository or directory choice
  -> representative entrypoint and state
  -> consequence for a concrete modification
  -> debugging evidence and verification
```

Weak:

> The flow uses `handlers/`, `services/`, `repositories/`, and `workers/`.

Better:

> The operation begins in HTTP but continues after that request ends, so its coordination cannot live only in the handler. The handler owns input validation, while the shared service owns the use case and the worker invokes that same responsibility later. A change to operation rules therefore starts in the service, then checks both callers and the persisted operation contract.

Trees and tables must answer a question introduced by prose. Explain why the reader needs the view before presenting it, and explain its modification or debugging consequence afterward.

## 15. Modification Prose

Do not promise that one requirement changes one module. Explain impact causally.

Weak:

> To add the field, update the schema, model, service, adapter, UI, and tests.

Better:

> The field starts in the domain model because its meaning belongs to the resource itself. The public schema changes only if callers can send or read it. The external adapter changes only if the remote system supplies or consumes it, and persistence changes only if the value must survive the process. These conditions determine which adjacent directories are required rather than merely nearby.

Name generated consumers after their source contract. Mark external repositories and unknown boundaries instead of implying they were inspected.

## 16. Debugging Prose

Make a debugging route a sequence of evidence-producing questions.

Weak:

> Check worker logs, database logs, API logs, and frontend logs.

Better:

> First confirm that the background executor received the operation identifier; this separates scheduling failure from later execution failure. Then inspect whether the external call returned a result with the expected identity. Only after both are true does a missing database update point to transformation or persistence. If the database is correct while the page remains old, move to the read or propagation path.

Every checkpoint should explain what its result proves and why the next checkpoint follows.

## 17. Generic Positive and Negative Examples

### Code identifier before concept

Weak:

> `IMPORT_DOC_42` enters `RETRY_WAIT` after `ParseWorker` fails.

Better:

> The file has been stored, but parsing stops before searchable content is produced. The system keeps the same operation identity, records that another attempt is allowed, and schedules the parser again. Only after this behavior is clear do the repository's retry state names help locate the implementation.

### Long setup versus mechanism pressure

Weak:

> A user opens the document page, selects a file, confirms the dialog, watches the progress bar, and waits for the browser to upload it.

Better:

> Uploading the bytes can finish in one HTTP request, while parsing and indexing may continue for minutes. The mechanism must therefore preserve progress beyond the request that started it.

### Abstract cache statement versus authority model

Weak:

> A local cache improves performance but creates consistency costs.

Better:

> Reads return the locally stored value without contacting the remote service. When the remote value changes elsewhere, the local copy remains old until a refresh replaces it. Faster reads are purchased with a period of possible staleness.

### Call-chain dump versus repository landing

Weak:

> `Handler -> Service -> Queue -> Worker -> Repository`.

Better:

> The HTTP entrypoint validates and records the request, then hands a durable identifier to the background executor. The executor invokes the same use-case service and writes progress through the repository. That split tells a maintainer to change business transitions in the service, request shape in the handler, and persistence only when stored state changes.

These examples demonstrate ordering and information density. Do not reuse their business domains or module names as a course template.

## 18. Narrative Cold-Read Audit

Before delivery, read all articles in order and check:

- Does the opening assume only ordinary programming knowledge?
- Is familiar setup shorter than the unfamiliar mechanism?
- Does every scenario detail affect control, data, state, authority, or failure understanding?
- Does every paragraph add information or a necessary transition?
- Does an arbitrary code identifier appear before it has navigation value?
- Does the prose show the baseline and result rather than announcing success?
- Does the requested mechanism receive enough process, state, identity, and boundary explanation?
- If the user asked about failure, does required prose reach the failure quickly?
- Would removing any diagram lose a relationship, transition, authority boundary, or flow?
- Did any internal card, concept budget, memory rule, or completion audit leak into the article?
- Does each article end naturally?
- Does repository navigation preserve the same connected voice?
- Can the reader move from responsibility to code owner, modification consequence, debugging observation, and verification without an unexplained gap?

If a core answer is no, compress, expand, merge, reorder, or rewrite. Do not repair weak prose with a glossary, longer summary, another visible checklist, or more code names.
