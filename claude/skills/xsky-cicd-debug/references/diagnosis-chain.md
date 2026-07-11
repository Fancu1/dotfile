# Diagnosis Chain

Use this reference when a failure crosses multiple ownership boundaries.

## Boundary Model
Always classify the failing path as a chain, not a single log line.

Typical chain:

```text
Jenkins job
-> upstream parameters
-> checkout repo
-> CI/CD wrapper
-> runtime command
-> business repo code
-> external artifact or topology
```

The owning cause is often one hop deeper than the first visible exception.

For Jenkins pipelines, there is often another layer:

```text
parent Jenkins job
-> child Jenkins job
-> grandchild Jenkins job
-> business repo code
-> external artifact
```

Do not treat the parent job status as the owning cause.

## Questions To Answer
1. Which repo did Jenkins actually check out?
2. Is the job pipeline-driven or shell-driven?
3. What exact command ran at the failure boundary?
4. Which repo owns that command?
5. Is the failure caused by code logic, config, Git topology, or an external fetched object?

## Failure Families

### 1) Jenkins Orchestration
- Wrong parameter values
- Wrong upstream build
- Wrong branch or tag checkout
- Credential or workspace issues

Evidence:
- `api.json`
- console checkout lines
- upstream build lines

### 2) CI/CD Wrapper Logic
- Groovy pipeline condition or branch selection
- `.CD/*.sh` argument construction
- repo-native `Jenkinsfile` or `.ci/Jenkinsfile-*`
- wrong build config file or release mode

Evidence:
- `platform/continuous-delivery` Groovy or shell files
- business repo `Jenkinsfile`, `.ci/Jenkinsfile-*`, or repo-local Groovy helpers
- rendered shell command in Jenkins console

### 3) Business Repo Logic
- Python or shell builder behavior
- package graph or version parsing
- tag selection logic
- repo-local test harness behavior such as `pytest`, `Cypress`, or `go test`

Evidence:
- checked out business repo ref
- stack trace file and line
- repo-local config such as `VERSION`, `build_conf/*.yaml`, distro lists

### 4) External Artifact Or Topology
- Git tag ancestry mismatch
- remote release mirror drift
- GitBuilder artifact inconsistency
- same-name package from multiple aliases with different bytes
- external reporting or bookkeeping systems such as TestLink or GitLab status APIs

Evidence:
- `git describe`, `merge-base`, `tag --contains`
- live artifact headers
- downloaded file size and hash
- payload comparison when necessary

### 5) Downstream Build Chains
- Parent job only reports `Build <job> #<id> completed: FAILURE`
- Publisher job reports branch failures but not the real code path
- Earlier partial success later causes missing outputs in another job

Evidence:
- `Scheduling project:`
- `Starting building:`
- `Build <job> #<id> completed: ...`
- `Failed in branch ...`
- child build `api.json` and `console.txt`

## Example Chain: Installer Builder

Observed chain:

```text
installer-builder Jenkins job
-> xsky-installer checkout
-> .CD/installer-builder.sh
-> ./build.sh
-> ./build.py
-> builder/builder.py::download_packages
-> GitBuilder dependence artifacts
```

In this class of issue, do not stop at the Python exception. Continue until you know:
- which build config selected the distro set
- which distro files reference the artifact
- which source aliases produce the same file name
- whether the remote artifacts are actually identical

## Example Chain: SDDC Publisher

Observed chain:

```text
sddc-releaser
-> sddc-publisher
-> sddc-installer-builder
-> sddc-installer builder code
-> release.xsky.com or gitbuilder.xsky.com artifacts
```

Typical trap:
- one publisher run succeeds for only one variant
- the parent job treats that as success
- a later publisher or installer build consumes a version that is only partially published

In this class of issue, answer:
- which child jobs failed
- whether the parent tolerated partial success
- which artifact variant was still missing later

## Example Chain: XT Suite AT

Observed chain:

```text
xt-suite-at Jenkins job
-> repo-native .ci/Jenkinsfile-AT
-> downstream xt-suite/<branch> test job
-> .ci/at-cli.py
-> TestLink API
```

Typical trap:
- the downstream test rerun eventually succeeds
- the parent job still fails later while reporting results to TestLink
- the real failing object is a missing test-plan association or other external test-management config

In this class of issue, answer:
- whether the child xt-suite job actually failed or only retried
- which repo-local reporting script made the failing API call
- which TestLink plan, case, or release name caused the rejection

## Example Chain: Wizard E2E

Observed chain:

```text
wizard-e2e-test Jenkins job
-> repo-native Jenkinsfile
-> build/cypress.groovy
-> scripts/e2e.sh
-> Cypress spec
-> UI assertion, request wait, or visual snapshot failure
```

Typical trap:
- Chromium prints many `ERROR:` warnings that are not the owning cause
- the real failure is one or more Cypress assertions inside specific spec files
- commit-scope and failing-spec scope may not overlap, which can indicate a flaky test or broad UI regression

In this class of issue, answer:
- which stage failed: E2E or E2E-vt
- which spec files produced the first concrete Cypress assertions
- whether the failing specs overlap with the changed files

## Example Chain: PR Check Shell Job

Observed chain:

```text
GitLab merge request
-> Jenkins shell or freestyle job
-> make / repo-local build script
-> language test runner
-> failing package and test case
```

Typical trap:
- the console has no pipeline file from `platform/continuous-delivery`
- the real owner is the checked-out business repo and its native build/test entrypoints
- the failing test can be outside the touched files, so causality may remain uncertain

In this class of issue, answer:
- which repo-local command failed
- which package and test name failed first
- whether the failure overlaps the MR diff or looks flaky/unrelated

## Example Chain: Tag Fetcher

Observed chain:

```text
tag-fetcher Jenkins pipeline
-> tag-fetcher.groovy precheck
-> xsky-installer checkout
-> git describe / stable_tag logic
-> Git tag topology
```

In this class of issue, separate:
- tag naming relationship
- branch ancestry relationship
- whether the tag ref moved over time

## Output Standard
A good diagnosis should say:
- where the failure first appeared
- where the owning cause actually lives
- which evidence ruled out the nearby but incorrect explanation
- what concrete object changed: tag ref, package source, build config, or wrapper logic
