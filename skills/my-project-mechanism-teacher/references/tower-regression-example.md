# Tower Mechanism Regression Example

Read this reference only when the target repository is Tower or when validating `my-project-mechanism-teacher`.

This file is a behavioral example, not a universal course template.

- The sequence below is a pedagogical reconstruction, not a verified account of Tower's historical development.
- Current Tower code and focused tests outrank architecture-course simplifications and older documentation.
- Original design intent requires explicit ADR, RFC, issue, comment, or history evidence.
- Other repositories must discover their own domain, runtime roles, authority boundaries, code route, and tests. Do not copy the VM synchronization sequence.

## 1. Regression Request

Use a request equivalent to:

```text
使用 $my-project-mechanism-teacher，解释 Tower 中一台 VM
在底层平台被直接关机后，Tower 页面怎样最终显示新状态；
并说明如果新增一个需要同步回 Tower 的 VM 字段，
应该从哪里修改、检查哪些相邻契约和测试。
读者有普通前后端经验，但不了解 Tower。保持源码只读。
```

The request combines an external-convergence mechanism with repository change and debugging navigation. Both the code-free mechanism spine and the repository-landing spine are required.

## 2. Opening and Shortest Baseline

Do not open with:

```text
UPSERT_VM
Worker
upsertVmMapper
SyncEngine
packages/task/
```

Begin with the smallest state distinction the question needs:

1. Tower lets an administrator operate and inspect a VM through a management view.
2. When every change starts in Tower, Tower can update its local record as part of the operation it already knows about.
3. The underlying virtualization platform can also be operated directly.
4. If a VM is powered off there, the platform's runtime fact changes before Tower's local record does.

Keep ordinary frontend and HTTP background brief. Spend the explanation on external authority, local view, identity matching, convergence, and the stale interval.

## 3. Required Mechanism Construction

Use one VM throughout. The prose should establish this execution before naming internal code:

1. The underlying platform reports that the VM is powered off.
2. Tower still has the last state it observed, so its page may temporarily show the VM as running.
3. A periodic background role asks the relevant external environment for current VM data.
4. The returned resource must be matched to the same Tower VM through a stable external or provider identity; matching by a display name alone would be unsafe.
5. External fields are translated into Tower's local model.
6. Tower writes the new state into its local management view.
7. A later query, subscription, or other verified propagation route reads that local value, allowing the page to show the VM as powered off.

Only after this mental execution is stable should the course introduce Tower's Worker, `UPSERT_VM`, transformer or mapper names, persistence, and page read path.

Do not claim immediate consistency. Explain the verified trigger or polling interval and its consequence. Do not claim which query or subscription updates the page until the current code route is traced.

## 4. Useful Authority Diagram

A diagram is useful when it distinguishes the external runtime fact from Tower's last observed management view:

```text
underlying virtualization platform
  `- authoritative VM runtime state
          | periodic read
          v
Tower synchronization work
  `- match identity, translate fields, write local record
          |
          v
Tower local management view
          | verified query or propagation route
          v
page displays the refreshed state
```

The adjacent prose must explain:

- why the platform is authoritative for runtime state;
- why Tower deliberately keeps a local view;
- what identity links the two representations;
- why the page can be stale between refreshes.

Remove any additional diagram that only rearranges Worker, Task, Mapper, Database, and UI names.

## 5. Current Code Evidence to Reverify

At the revision used when this regression file was written, these paths existed and were relevant starting points:

```text
packages/worker/src/index.ts
packages/task/src/tasks/sequence.ts
packages/task/src/tasks/vm/upsert-vm.ts
packages/shared-service/src/transformers/vm.ts
packages/task/__tests__/tasks/upsert-vm.spec.ts
packages/task/src/sync-engine/index.ts
packages/task/src/sync-engine/check-vm.ts
```

Every course run must reverify them and follow current imports, registrations, calls, and tests. Do not preserve a path or responsibility merely because this file lists it.

Expected evidence questions include:

- Where does the Worker register and schedule tasks with an interval?
- Where is the VM upsert task added to the active task set?
- Which code reads the provider stream, chooses full or targeted synchronization, invokes field mapping, writes records, and handles deletion or garbage collection?
- Which transformer maps external VM attributes to Tower create or update inputs?
- Which tests prove normal upsert, targeted behavior, full-sync cleanup, and provider-error behavior?
- Does `sync-engine` participate directly in the exact requested route, or is it an adjacent mechanism with a different trigger or responsibility?

The last question prevents an architecture-level “Worker / SyncEngine” simplification from replacing the current implementation route.

## 6. Evidence Still Required for the Visible Finish

The course must continue tracing before claiming how the page updates:

- the datamodel or ORM representation that persists the relevant VM field;
- the write operation used by the mapper or task;
- the GraphQL or other server read contract that exposes the field;
- generated types and consumers;
- query, subscription, observer, or cache propagation actually used by the UI;
- whether the relevant VM UI is local to Tower or belongs to an external Island repository.

If a boundary is external, inaccessible, generated, or not proven at the inspected revision, label it. Do not fill the gap with a plausible generic frontend path.

## 7. Required Repository Narrative

The repository article should preserve this causal line:

```text
periodic execution responsibility
  -> Worker entry and task registration
external VM read and synchronization coordination
  -> VM upsert task
external-to-local field meaning
  -> shared VM transformer or mapper
durable local management view
  -> verified datamodel and ORM write path
visible page result
  -> verified server contract and UI propagation
behavioral proof
  -> focused task, mapper, server, and UI tests
```

Introduce paths after each responsibility is understood. Explain why a change begins in one path and only conditionally reaches another.

## 8. Change Case: Add a VM Field Synchronized into Tower

The case must separate these conditions.

### External value is not yet available

Inspect the Provider or Connector output contract and the concrete external-platform adapter. This is required only if the external field is absent from the data Tower already receives.

### External value exists but is not mapped

Inspect the VM transformer or mapper and the upsert task's selected attributes. This is normally the primary behavior owner for translating an external field into Tower's local meaning.

### The value must be persisted

Inspect the datamodel, ORM or Prisma source schema, migrations, and write inputs. Edit schema sources, not generated clients. Persistence work is unnecessary for a transient value that is deliberately not stored.

### API callers need the value

Inspect the GraphQL schema or other public contract, its source types, and generated consumers. This is required only when clients can send or receive the field.

### The page must display the value

Inspect the current UI implementation or mark the owning Island as an external repository. Do not pretend the local Tower repository owns an external UI.

### The field changes synchronization semantics

Inspect identity selection, comparison, full-sync behavior, deletion or garbage collection, and the VM synchronization tests. A passive field mapping does not automatically require workflow changes.

### Areas normally unaffected

ResolverTask, Temporal, scheduler configuration, Helm, and delivery repositories are normally unaffected when the change only maps, stores, exposes, or displays another field. They become conditional only if operation lifecycle, runtime role, configuration, or deployment artifacts change.

The visible impact view must distinguish:

```text
Primary owner
Required checks or contracts
Conditional changes
Generated consumers
External repositories
Explicitly unaffected areas
Unknown or unverified boundaries
Verification paths
```

Do not render empty categories merely to complete a form. Explain why each included category applies.

## 9. Required Debugging Case

Use the symptom “the VM is powered off in the underlying platform, but Tower still shows it as running.”

Follow evidence in this order, adjusting to current code:

```text
Worker process is running and polling is registered
  -> UPSERT_VM is included and triggered for the relevant environment
      -> Provider or Connector returns the current state
          -> returned identity matches the intended local VM
              -> transformer maps the state correctly
                  -> database write commits the new value
                      -> observer, query, subscription, or cache path exposes it
                          -> current UI reads and renders the field
```

For every checkpoint explain what the observation proves:

- no polling narrows the problem to process liveness, registration, or scheduling;
- no external result narrows it to environment selection, adapter, connectivity, or provider behavior;
- correct external data with no match narrows it to identity or scope;
- correct match with a wrong local input narrows it to transformation;
- correct write input with old persisted data narrows it to persistence or transaction handling;
- correct persisted data with an old API result narrows it to server read, observer, or cache propagation;
- correct API data with an old page narrows it to the current UI or external Island.

Use actual logs, metrics, tests, or debug entrypoints only when the repository proves they exist. Otherwise describe the missing observability as a limitation.

## 10. Optional Branches

Unless the user asks about them or they decide the visible result, keep these outside the required route:

- full-sync garbage collection;
- targeted synchronization versus full synchronization;
- strict versus non-strict Provider errors;
- concurrent executions;
- stream completion details;
- complete deletion and disconnected-resource behavior;
- exhaustive retry or compatibility paths;
- complete historical evolution.

If the requested field affects full-sync comparison or deletion behavior, the relevant branch becomes required for that change case.

## 11. Tower Cold-Read Acceptance

The generated course passes only when:

- the opening uses ordinary management and state language rather than code names;
- external runtime authority and Tower's local view are unmistakably different;
- the reader can follow one complete convergence run before seeing paths;
- stable identity, state transformation, persistence, and visible readback are explained;
- current source determines whether `sync-engine` participates;
- the page propagation path is verified or marked unknown;
- the repository route maps responsibilities to current paths and tests;
- the new-field case distinguishes required, conditional, generated, external, unaffected, and unknown areas;
- the debugging route explains what each checkpoint proves;
- optional branches do not displace the user's requested mechanism;
- no visible concept budget, exit ability, memory rule, or completion footer appears;
- Tower source, existing formal courses, and external repositories remain unchanged.
