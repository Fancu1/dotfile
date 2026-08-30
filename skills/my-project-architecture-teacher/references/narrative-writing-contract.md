# Narrative Writing Contract

Read this reference before generating or rewriting any course article. It governs the prose the learner sees. The course-design cards in `SKILL.md` and `course-design-contract.md` remain internal authoring tools.

## 1. Default Reader

Write for a programmer who understands ordinary software development but has not read this repository and does not know its domain.

By default, the reader already recognizes:

- frontend and backend roles;
- development, test, and production environments;
- HTTP requests, processes, databases, and ordinary deployment;
- source files, modules, tests, and build outputs.

Do not reteach those foundations merely because the reader does not know a domain mechanism. Explain a lower-level software concept only when the user requests it or when the project-specific idea cannot be understood without it.

Before drafting, record internally:

```text
Familiar to a general programmer:
Unfamiliar project or domain concepts:
Code identifiers that should appear only later:
Concepts that genuinely require a concrete example:
```

## 2. Allocate Detail Where It Teaches

Use two speeds:

```text
familiar context -> establish it quickly
new pressure -> make the change concrete
unfamiliar mechanism -> slow down and explain how it works
project term -> name it after recognition
code location -> introduce it after the architecture responsibility is clear
```

Do not impose a fixed word ratio. A familiar background normally needs no more than one short paragraph. If the background is longer than the unfamiliar mechanism, review whether the article is telling a story instead of teaching the project.

"Beginner-friendly" does not mean low information density. It means that every necessary intermediate idea is present and ordered so the reader does not need unstated domain knowledge.

## 3. Scenarios Are Compressed Problem Setups

A scenario earns its place only by making the current pressure easier to see.

Keep:

- the actor or role whose goal remains stable;
- the current system and the result it provides;
- the one changed condition that exposes a cost or failure;
- concrete quantities when they explain scale, allocation, latency, or waste.

Remove:

- atmosphere and character detail;
- a walkthrough of ordinary web or application behavior;
- business facts that do not affect the architecture;
- repeated reminders of the stable goal;
- names invented only to make the scenario feel realistic.

The scenario is a pressure-delivery mechanism, not a short story.

## 4. Keep Internal Scaffolding Invisible

Admission cards, concept budgets, reader state, exit capability, responsibility cards, and causal steps guide the author. They are not a visible article format.

Do not mechanically render headings or endings such as:

```text
本篇只讨论……
本篇暂不讨论……
当前方案已经能够工作……
完成标准……
读者现在应该能够……
本章小结……
```

The phrases are not forbidden in every possible sentence. They are forbidden as repeated structural boilerplate. If removing the sentence does not remove a fact, relationship, boundary, or necessary reading instruction, remove it.

Do not require every article to expose benefit, cost, boundary, remaining problem, and evidence as separate labels. Weave only the items needed for the current explanation into connected prose.

## 5. Terminology and Code Names

Establish recognition before naming.

- Use an ordinary description before a domain or project term.
- Do not use an arbitrary code-like identifier as the subject of an opening scenario.
- Prefer "the billing backend" to `billing-api-v2` until the code name helps locate implementation.
- Introduce official domain terms after the reader understands the responsibility or relationship they name.
- Introduce file paths, types, functions, generated symbols, and internal status names mainly in the repository-navigation spine.
- A user-visible official name may appear earlier after a short ordinary-language explanation.

Necessary technical terms are not noise. Unearned terms are.

## 6. Paragraph Information Gain

Each paragraph must add at least one of these:

- a necessary fact about the current system;
- a concrete changed condition;
- a causal relationship;
- an explanation of how an unfamiliar concept works;
- a boundary that prevents a likely misunderstanding;
- an architecture-to-code mapping;
- a modification or verification consequence;
- a natural transition to the next unresolved pressure.

Delete or merge a paragraph when it only:

- makes the scene more vivid;
- paraphrases the previous conclusion;
- announces that the article followed the teaching plan;
- repeats a caveat already established;
- lists names without explaining a relationship.

Paragraphs should connect. Passing the information-gain check does not justify a sequence of disconnected teaching cards.

## 7. Show Success Through Results

The previous system must remain genuinely viable, but the prose should normally demonstrate that viability through an observable outcome.

Weak:

> 对当前场景，这个方案已经能够工作。

Better:

> 从此以后，即使开发人员关闭自己的电脑，用户仍然可以访问系统并提交请求。

Weak:

> 直接登录单个平台仍然是可行方案。

Better:

> 公司只有一套运行环境时，管理员登录它的管理页面，就能完成创建、查看和关闭操作。

In English, prefer the same result-first form:

> With one environment, the operator can sign in, find the resource, and finish the operation in one place.

Do not append "therefore the old solution works" after the result has already proved it.

## 8. Expand Unfamiliar Mechanisms, Not Familiar Background

An unfamiliar mechanism normally needs more than a definition. Explain the smallest useful combination of:

- what existed before;
- what is being divided, recorded, translated, synchronized, or owned;
- which participants see different views;
- one concrete value, state change, or example;
- what remains shared or unchanged;
- the boundary of what the mechanism does not solve.

Weak:

> The system adds a queue so long work can run asynchronously.

Better:

> The request first creates an operation record and returns its identifier. A background executor then processes the work, while later requests read the same record for progress and the final result. The queue separates request lifetime from work lifetime; it does not by itself define the business result or recovery policy.

Do not expand every implementation branch. Expand only until the reader can place the mechanism correctly in the architecture and understand why its responsibility exists.

## 9. Diagram Admission and Deletion Test

Before adding a diagram, answer internally:

```text
What relationship is difficult to see from the adjacent prose alone?
What information would the reader lose if this diagram were removed?
```

A useful diagram may show:

- before-and-after structure;
- resource allocation or sharing;
- request, data, operation, or state flow;
- collaboration between several modules;
- an authority or source-of-truth boundary;
- runtime or deployment topology;
- architecture responsibility projected into repositories and directories.

Remove the diagram when it only rearranges the same nouns into a tree or repeats a paragraph line by line.

Weak:

```text
System
|- API
|- Worker
`- Database
```

Useful when the question is asynchronous state ownership:

```text
HTTP request
  -> create operation record in database
  -> enqueue operation id
  -> return id to caller

background worker
  -> read operation id
  -> perform external work
  -> update the same operation record

later status request
  -> read operation record
  -> show progress or result
```

## 10. Natural Article Endings

End with either:

1. the concrete state the system has now reached; or
2. the next unresolved pressure that follows naturally from that state.

Example result ending:

> Requests can now finish quickly while the operation continues in the background, and the user can return later to inspect the same operation record.

Example pressure ending:

> That solves work that outlives one request. It does not yet explain how the operation resumes after the executor restarts halfway through.

Do not append a completion criterion, lesson objective, review question, reader-capability statement, or fixed summary.

## 11. Keep Repository Navigation in the Same Narrative

Repository landing is not permission to switch from teaching prose to an inventory.

Use this connected progression:

```text
responsibility already understood
  -> organization pressure faced by maintainers
  -> current repository or directory choice
  -> representative entrypoint
  -> consequence for a concrete modification
  -> relevant verification
```

Weak:

> The repository contains `handlers/`, `services/`, `repositories/`, and `workers/`.

Better:

> The same import operation can start from HTTP and continue in a background executor, so its business coordination cannot live only in the HTTP handler. The handler accepts and validates the request, while the shared service owns the use case. That is why a change to import rules starts in the service, then checks the handler contract and worker consumer instead of editing every directory equally.

Trees and tables should answer a question introduced by the prose. Explain why the reader needs the view before presenting it, and explain its modification consequence afterward.

Module responsibility cards and repository decision cards remain internal. A visible comparative table is appropriate when it helps the reader see several mappings at once; repeated per-module forms are not.

## 12. Positive and Negative Style Examples

### Code-name opening versus ordinary-language opening

Weak:

> The team needs to deploy `invoice-worker-prod` so it can process invoices continuously.

Better:

> Invoice processing must continue after the developer who started it closes their computer. The program therefore needs a company-maintained runtime before its repository-specific process name matters.

### Overdeveloped background versus compressed shared context

Weak:

> A user opens the site, clicks the navigation item, chooses a file, confirms the dialog, and waits while the browser uploads it to the backend.

Better:

> Uploading one small file can be handled inside a normal request. The design changes when parsing and indexing continue for minutes after the upload finishes.

### Abstract definition versus concrete operation

Weak:

> A local cache improves performance but creates consistency costs.

Better:

> Reads now return the locally stored value without calling the remote service. When that remote value changes elsewhere, the local copy remains old until a refresh process reads and replaces it. Faster reads are purchased with a period of possible staleness.

### Directory dump versus change navigation

Weak:

> API code is in `api/`, domain code is in `domain/`, and integrations are in `adapters/`.

Better:

> A new field first changes the domain meaning. It reaches `api/` only when callers can send or receive it, and reaches `adapters/` only when an external system must translate it. The directory boundary therefore tells the maintainer which changes are required and which are conditional.

These examples demonstrate information density and ordering. Do not reuse their business domains as a course template.

## 13. Narrative Cold-Read Audit

Before delivery, read the articles in order and check:

- Does the first paragraph assume only ordinary programming knowledge?
- Is familiar context shorter than the unfamiliar concept it introduces?
- Does every scene detail affect the architecture explanation?
- Does each paragraph add new information or a necessary transition?
- Does an arbitrary code identifier appear before it has navigation value?
- Does the result demonstrate that the previous system works without a formulaic announcement?
- Does each unfamiliar mechanism have enough process, state, relationship, or example to be placed correctly?
- Would removing any diagram lose a relationship, change, boundary, allocation, or flow?
- Did any internal card, concept budget, or exit capability leak into the article?
- Does each article end naturally rather than with a standard lesson footer?
- Does the repository-navigation spine preserve the same connected voice?
- Can the reader continue from architecture responsibility to code ownership without crossing an unexplained gap?

If a core answer is no, compress, expand, merge, reorder, or rewrite. Do not repair low-information prose with a glossary, a longer summary, or another visible checklist.
