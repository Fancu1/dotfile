# Tower Regression Example

Use this reference only when the target repository is Tower or when behaviorally validating `my-project-architecture-teacher`.

This is a regression oracle and a worked illustration of the teaching method. It is not a fixed template for other repositories.

## Boundaries

- The sequence below is a pedagogical reconstruction of pressures that make Tower's current responsibilities understandable. It is not a claim about Tower's actual historical origin.
- Treat current code, tests, manifests, deployment configuration, and maintained architecture documents as evidence of current behavior and boundaries.
- Claim an original design reason only when an ADR, RFC, issue, merge request, commit message, or explicit maintainer document supports it.
- A VM reorganizes physical capacity; it does not replace physical hardware.
- Tower manages more than VM lifecycle. The VM scenario is an entry thread, not the complete product map.
- Other repositories must discover their own goals, domains, pressures, runtime roles, organizing axes, and change routes. Do not load this reference for them.

## Expected Tower Course Spine

The `01` through `23` numbering is an expected Tower regression shape, not a universal quota. Equivalent splits are acceptable only when they preserve every architecture transition below.

The prose samples in chapters 01 and 02 calibrate pace and information density; generated articles need not copy them word for word. All pressure, responsibility, evidence, boundary, and acceptance notes in this reference are internal instructions. They must not appear as repeated headings, completion standards, or lesson-card footers in the generated course.

### 01. Why the backend needs a company-maintained environment

Start without VM, Cluster, Tower, or an arbitrary code-like service name. Assume the reader already understands frontend/backend development; use that shared context without explaining ordinary web behavior.

Style reference:

> 以一个电商系统为例。开发时，前端和后端都可以运行在开发人员自己的电脑上；正式上线后，后端却必须在开发人员关机以后继续处理用户的下单请求。
>
> 因此，正式环境需要运行在一台由公司持续供电、联网和维护的机器上。最直接的办法，是准备一台物理服务器，把电商后台部署在上面。
>
> 如果公司目前只有这一套正式环境，这个方案已经足够：用户访问网站时，请求由这台服务器处理，不再依赖某位开发人员的电脑。

Do not add a diagram merely to repeat "backend runs on physical server." The three short paragraphs already establish the necessary relationship. Do not append a lesson objective or reader-capability statement.

### 02. Why allocate a VM from existing hardware

Let the physical-server solution remain valid. Add one pressure: the team needs an isolated test environment without placing unfinished code in production. Spend little prose on ordinary release practice; spend the detail budget on why another whole server is costly and how software allocates existing hardware.

Style reference:

> 后来，团队准备上线新的结算功能。为了避免尚未完成的代码影响真实用户，他们需要先搭建一套独立的测试环境。
>
> 按照之前的办法，可以再准备一台物理服务器。这个方案能够工作，但准备硬件、安装操作系统和配置网络需要时间，而测试环境可能只使用几周。
>
> 与此同时，现有服务器的资源未必已经用满。例如，一台服务器拥有 32 核 CPU 和 128 GB 内存，正式环境可能只使用其中的 8 核和 32 GB。为了一个只需要 4 核和 16 GB 的测试环境，再准备整台服务器并不划算。
>
> 更合适的办法，是把一台物理服务器的资源划分成几个彼此独立的运行环境。每个环境拥有自己的操作系统、CPU、内存和磁盘，看起来就像一台独立的电脑。这种由软件创建的独立运行环境，就是虚拟机，也常写作 VM。

The diagram is useful because it shows allocation and remaining shared capacity rather than repeating object names:

```text
一台物理服务器：32 核 CPU、128 GB 内存

├─ 正式环境 VM：8 核、32 GB
│  └─ 运行正式业务
│
├─ 测试环境 VM：4 核、16 GB
│  └─ 测试新功能
│
└─ 尚未分配的资源
```

Natural ending reference:

> 虚拟机解决了“怎样从现有硬件中快速得到独立运行环境”的问题。但当公司拥有很多物理服务器和虚拟机以后，管理员又会遇到一个新问题：新的虚拟机究竟应该放在哪里？

Preserve the boundary that a VM reallocates real CPU, memory, disk, and power rather than creating resources from nothing, but explain it through the allocation example instead of attaching a formulaic boundary footer.

### 03. Why a VM belongs to a Cluster

Do not explain VM again. Begin from the next changed condition: several physical servers now have different remaining capacity and maintenance state, so an operator must repeatedly inspect them before choosing where a new VM belongs.

Explain a manageable compute-resource scope before naming Tower's `Cluster` term. Use a diagram only if it shows how a VM receives resources from that scope, rather than displaying a list of servers and VMs. Do not infer scheduling, high availability, or storage behavior merely from the name.

End by establishing that VM placement is manageable inside one Cluster while leaving the next concrete pressure visible: several Clusters must still be found and operated separately.

### 04. Why multiple compute environments need Tower

Let direct login to one platform work. With one Cluster, the operator can sign in, find the VM, and finish creation, inspection, or shutdown in one place.

Add a second compute environment and one compressed lookup incident: an alert identifies the order system's VM, but the operator no longer remembers which environment owns it and must search each platform separately. Do not add character history, emotion, or operational detail that does not change the architecture.

Explain the missing responsibility as one resource directory and operation entry point above the compute environments. Name Tower only after that responsibility is clear, then explain the management-plane term.

Do not add version, storage, authorization, audit, and recovery as a concern list. End by moving naturally into the smallest management loop Tower must complete.

### 05. Tower's minimal management loop

Teach one deliberately simple success. This diagram is useful because it assigns a different responsibility to each node:

```text
operator
  -> Tower: accept the request and show the managed result
      -> Cluster: provide real compute capacity
          -> order-system VM: run the backend
```

Keep fast work, one platform shape, success, no external drift, and one trusted operator as internal simplifying assumptions. Weave an assumption into prose only when it is needed to make the next pressure understandable. This is a checkpoint, not course completion, but do not say so through a visible lesson footer.

For chapters 06 through 17, the concise pressure and responsibility notes below specify content, not visible format. Generated articles must use connected paragraphs: show the current result, introduce the changed condition, explain the unfamiliar mechanism with enough process or state detail, and end on the new system state or next pressure. Do not copy `Pressure`, `Responsibility`, `Boundary`, or similar labels into every article.

### 06. Why a unified resource directory needs a local management view

Pressure: querying every external platform for every page makes page availability and latency depend on all platforms.

Responsibility: persist a queryable Tower-side management view and its relationships.

Current implementation evidence to investigate:

```text
packages/datamodel/
  -> packages/prisma-client/
      -> packages/orm/
          -> PostgreSQL
```

Explain Tower-side management state versus external resource facts. Do not claim cross-platform strong consistency.

### 07. Why creation needs an independent Task

Pressure: creation outlives one browser request; refresh or disconnect must not erase the operation.

Responsibility: give the long operation its own durable or observable record. Introduce `Task` and the current `ResolverTask` path without yet teaching its full state machine.

### 08. Why a not-yet-created VM still needs identity

Pressure: the Task exists, but UI updates, audit, failure handling, and later reconciliation need a shared resource identity before the external VM exists.

Responsibility: create a placeholder `Vm` and later replace its temporary external identity with the real one.

Keep operation identity and resource identity distinct.

### 09. Why unsupported combinations must be rejected before execution

Pressure: product form, version, storage shape, hardware, state, and capability differ across environments.

Responsibility: maintain request contracts, operation validation, and capability gates before external side effects.

Investigate:

```text
packages/graphql-schema/
packages/graphql-types/
packages/validation/
packages/server/src/resolvers/<domain>/
```

Do not turn a current gate into a permanent domain invariant without evidence.

### 10. Why external platform differences need Provider and Connector boundaries

Pressure: the same product action requires different request shapes, jobs, errors, and returned identities across platforms.

Responsibility: express an upper-level capability and isolate concrete transport/data translation.

Investigate:

```text
packages/provider-interface/
packages/connector/
packages/*-connector/
```

Boundary: abstraction does not erase real capability and lifecycle differences.

### 11. Why external state needs continuing synchronization

Pressure: a VM can be powered, changed, or deleted outside Tower; write-time updates alone become stale.

Responsibility: workers periodically read external facts, normalize them, and converge the local view.

Investigate:

```text
packages/worker/
packages/task/src/tasks/
packages/sync-engine/
packages/db-observer/
```

Distinguish external polling/upsert from local derived observers.

### 12. Why some operations need durable Workflow execution

Let existing `ResolverTask`, scheduler, and local mechanisms remain valid for the paths they currently own. Add pressure from cross-process lifecycle, durable history, restart recovery, retries, or compensation.

Introduce Temporal workflow responsibility and the current coexistence:

```text
existing resolver paths -> ResolverTask / local scheduler
new durable lifecycle paths -> packages/task/src/workflows/ -> Temporal -> worker activities
```

Do not claim all Tower background work uses one queue or that current VM creation already uses Temporal unless the inspected path proves it.

### 13. Why shared operations need identity, authorization, and audit

Pressure: several people or API clients act on shared resources.

Responsibilities:

- establish the initiating identity;
- enforce final allow/deny decisions at the server boundary;
- attribute accepted and terminal outcomes where the path supports it.

UI visibility is not final authorization.

### 14. Why frontend growth produces Host and Islands

Let one UI application work. Add pressure from independently developed and delivered product regions.

Introduce:

```text
Tower UI host
  -> RegionRenderer
      -> island registry / sea-map
          -> remote Island export
```

Investigate `packages/ui/`, `packages/ui-components/`, `packages/island-runtime/`, `packages/island-ipc/`, registry code, and verified external island mappings.

### 15. Why source artifacts still need a delivery boundary

Pressure: server, static UI, Helm, and external Island artifacts must be selected, assembled, installed, and registered before users can run them.

Introduce the current delivery boundary:

```text
Tower release artifacts
  -> external cloudtower-builder selection and bundle
      -> installer boundary
          -> Helm roles and Island upload hooks
```

Label unverified installer behavior and independent artifact-version compatibility honestly.

### 16. Tower product-domain map

Correct the center-scenario simplification: Tower is not only VM creation.

At minimum map currently evidenced domain groups such as:

```text
Tower management plane
  |- compute and VM lifecycle
  |- storage and data services
  |- networking
  |- backup, replication, and disaster recovery
  |- Kubernetes and application services
  |- SFS and image/registry surfaces
  `- observability and related platform services
```

Do not claim equal investigation depth for all domains. Separate verified scope from deliberately skipped domain lifecycles.

### 17. Complete current architecture and representative flows

Introduce few or no new durable concepts. Assemble at least:

1. product-domain and shared-responsibility map;
2. runtime/deployment topology;
3. state owner and source-of-truth map;
4. representative overlays for VM query, VM creation, external-state convergence, and Island discovery/loading.

The runtime view should account for the currently evidenced UI host, GraphQL server, PostgreSQL/data access, main or conditional workers, ResolverTask/local mechanisms, Temporal, Provider/Connector boundary, external platforms, Island runtime, and delivery boundary.

Every major node needs a responsibility card.

Use those cards to verify completeness internally. The visible assembly should read as the convergence of the preceding articles, supported by a small number of comparative maps or tables rather than a stack of repeated forms.

### 18. Why Tower's repository is organized this way

This is the bridge from architecture to code. Do not begin with a directory dump.

Preserve the course's connected voice: the reader has already learned that each VM operation crosses UI, contracts, state, asynchronous work, synchronization, and external systems. Begin by asking how maintainers can place these different responsibilities in one directory tree, then compare alternatives and reveal the current hybrid organization.

First compare two genuinely viable alternatives:

```text
Alternative A: product-domain-first
packages/vm/{ui,server,task,provider}
packages/storage/{...}

Alternative B: one technical-layer tree
src/{ui,api,services,database,tasks,integrations}
```

Then explain the verified current pattern:

```text
top-level packages: runtime roles, shared technical responsibilities,
                    contracts, integration and delivery boundaries
inside large packages: VM, storage, network, backup, and other product domains
```

Use a matrix:

| Responsibility | VM example |
| --- | --- |
| Frontend | `packages/ui/src/modules/vm/` or verified external `vm-island` surface |
| API | `packages/server/src/resolvers/vm/` |
| Validation | `packages/validation/src/vm.ts` |
| Background work | `packages/task/src/tasks/vm/`, `packages/task/src/workflows/vm/` |
| Data | `packages/datamodel/`, `packages/prisma-client/`, `packages/orm/` |
| External capability | `packages/provider-interface/`, `packages/connector/` |

Explain the consequence: a VM feature is a vertical slice across responsibility-oriented packages, not one `packages/vm/` folder.

Label the rationale as architectural inference unless explicit evidence exists. Explain evolutionary seams such as legacy/new Prisma, ResolverTask/Temporal, Host/Island, and general/specialized connectors rather than presenting the tree as a frictionless ideal.

The matrix supports the explanation; it must not replace the paragraphs that connect architecture responsibility to organization pressure and modification consequence.

### 19. How the current directory tree carries Tower architecture

Explain why a responsibility-oriented tree is now useful, then show an annotated, verified tree at responsibility-relevant depth. Include:

```text
tower/
|- packages/
|  |- ui/ and ui-components/              # host and shared frontend/runtime
|  |- island-runtime/ and island-ipc/      # host/remote contract
|  |- server/                              # GraphQL/HTTP control plane
|  |- graphql-schema/ and graphql-types/   # generated contract boundary
|  |- validation/                          # input and capability validation
|  |- datamodel/ -> prisma-client/ -> orm/ # data boundary
|  |- task/ and worker/                    # task/workflow definitions and execution role
|  |- sync-engine/ and db-observer/        # convergence and derived reactions
|  |- provider-interface/ and connector/   # external platform boundary
|  `- specialized *-connector packages
|- helm/                                   # deployment
`- contributing/                           # current architecture/domain/change guidance
```

Mark generated directories, tests, external repositories, executable/build/deployment roles, and first-pass skip areas. Verify every local path against the inspected revision.

After the tree, explain how to use its two axes: choose the product domain first, then the runtime or shared responsibility. Do not end with an inventory recap or completion standard.

### 20. How four core flows traverse real directories

Begin from the conceptual flows the reader already knows, then project them into current code:

- VM list query;
- representative VM creation;
- external VM state convergence;
- Island discovery/loading and, when relevant, artifact delivery.

For VM creation, investigate a route resembling:

```text
host or external VM UI
  -> GraphQL operation and generated consumer
  -> server request context / middleware
  -> packages/server/src/resolvers/vm/
  -> validation and data access
  -> ResolverTask or the path actually used
  -> provider-interface / connector
  -> external platform
  -> ORM writeback
  -> task notification and later synchronization
  -> representative tests
```

Use actual inspected files and label special storage/template branches that were not followed.

Paths must be introduced as answers to flow questions, not as a sequence of unexplained file names.

### 21. How a feature request selects modification directories

Use at least three change cases. One must be the cross-layer example: add a VM creation hardware capability.

Conditional impact map:

```text
actual user surface
  -> packages/ui/ or external vm-island

contract changes, if input/output changes
  -> packages/graphql-schema/
  -> packages/graphql-types/
  -> generated consumers

business behavior and allow/deny rules
  -> packages/server/src/resolvers/vm/
  -> packages/validation/src/vm.ts

persistence, only if state must be stored
  -> packages/datamodel/
  -> packages/prisma-client/
  -> packages/orm/
  -> packages/db-migrations/

external payload/capability, only for affected providers
  -> packages/provider-interface/
  -> packages/connector/ or target specialized connector

async lifecycle, only if steps or terminal behavior change
  -> ResolverTask and/or packages/task/src/tasks/ or workflows/

readback/convergence, only if external state must return to Tower
  -> packages/task/src/tasks/vm/
  -> packages/sync-engine/
  -> packages/db-observer/
```

Finish with a table separating primary owner, required checks, conditional changes, generated consumers, external repositories, explicit non-impact, verification, and unknowns.

Introduce the table through the concrete decision a maintainer faces. Explain afterward why architecture ownership, rather than keyword search alone, determines the primary edit and conditional neighbors.

### 22. Which code is outside the Tower repository

Teach how to locate actual ownership when Tower only hosts, contracts with, registers, or delivers a feature.

At minimum distinguish:

```text
Tower repository
  |- UI host and Region mount points
  |- Island runtime and registry contracts
  |- GraphQL server and shared contracts
  `- Tower release/Helm artifacts

external Island repositories
  `- actual remote product implementations such as verified vm-island exports

external cloudtower-builder
  `- artifact/version selection and installation-bundle assembly
```

Do not infer repository ownership from a runtime Island name. Label inaccessible external code as unverified.

Keep the narrative anchored in a maintainer following ownership beyond the current checkout; do not present external names as a standalone catalog.

### 23. How to prove a change is complete

Map changed responsibility to evidence:

```text
resolver and validation behavior -> server/validation tests
GraphQL contract -> generation review and consumer type/build checks
provider mapping -> connector tests
task/workflow terminal behavior -> task/workflow tests
state convergence -> worker/upsert tests
host behavior -> Tower UI tests
external Island behavior -> target repository tests/build
runtime/config/artifact change -> Helm or delivery checks
```

Distinguish focused tests, type checks, build checks, static document checks, integration tests, and actual runtime validation. Do not claim real cluster, PostgreSQL, Temporal, subscription, Island, installer, or Helm behavior unless it ran.

End the course on the verification path that closes a real change, not on a generic course summary or reader-capability checklist.

## Tower Behavioral Acceptance

A generated Tower course passes only when:

- `00-阅读指南.md` marks architecture construction and repository landing as required;
- the prose assumes ordinary software-development knowledge and does not reteach basic frontend/backend or HTTP behavior;
- familiar setup is compressed while Tower-specific domain and architecture mechanisms receive enough process, state, relationship, or allocation detail;
- the first article contains no arbitrary code-like service name, VM, Cluster, or Tower;
- previous-system success is normally visible through an observable result rather than a repeated formulaic announcement;
- no article exposes admission cards, pressure/responsibility labels, exit capabilities, completion standards, lesson objectives, or fixed summaries;
- every paragraph adds information or a necessary transition, rather than atmosphere or repeated conclusions;
- every diagram shows allocation, change, flow, state, authority, boundary, or architecture-to-code projection that surrounding prose does not show equally well;
- articles end naturally on the current system state or the next concrete pressure;
- the first need contains no VM, Cluster, or Tower;
- physical server, VM, Cluster, and Tower appear through separate successful-system/pressure transitions;
- local management view, Task, placeholder identity, validation, Provider/Connector, Worker convergence, Temporal coexistence, authorization/audit, Host/Island, and delivery are required architecture material;
- the product-domain map makes clear that VM is not the whole product;
- complete architecture views and representative flows contain only taught nodes;
- the maintainer-organization bridge identifies Tower's hybrid two-axis structure and compares viable alternatives;
- chapters 18 through 23 preserve the same connected voice and introduce trees, matrices, paths, and tests through the questions they answer;
- the annotated tree uses current verified paths and marks generated/external boundaries;
- the change cases distinguish primary, required, conditional, unaffected, external, verification, and unknown areas;
- current facts, documented intent, inference, pedagogical reconstruction, and unknowns are not conflated;
- Tower source and any existing formal course remain unchanged.

## Anti-Template Check

When validating the skill on a non-Tower repository, ensure the output does not contain Tower, VM, Cluster, physical-server, Provider/Connector, or Island steps unless that repository independently requires and evidences them. The non-Tower course must derive its own domain runway, architecture responsibilities, organizing axes, and directory/change map.
