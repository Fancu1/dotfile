---
name: xsky-cicd-debug
description: Use when debugging XSKY Jenkins or CI/CD failures, especially when a user provides a Jenkins build URL, build number, job name, failing Groovy pipeline, tag ancestry issue, or asks to map a Jenkins failure back to code in `platform/continuous-delivery` or a related business repo.
---

# XSKY CI/CD Debug

## Overview
Use this skill to localize XSKY Jenkins failures with a fixed evidence chain: build metadata, console snippets, pipeline code, repo ancestry, runtime ownership, and external artifact evidence. Default scope is diagnosis only. Do not mutate Jenkins jobs, tags, branches, or production systems unless the user explicitly asks.

## Hard Rules
1. Always fetch Jenkins `api/json` and `consoleText` first, then save them under `/tmp/xsky-cicd-debug/<job>/<build>/`.
2. Never load the full Jenkins console into context by default. Extract snippets from the saved file.
3. Prefer remote repo evidence over local worktrees. Local clones are optional fallbacks, not the primary source of truth.
4. When repo resolution is uncertain, search saved logs first, then inspect `meta.groovy` from `platform/continuous-delivery`.
5. When diagnosing tag or branch issues, prove ancestry with `git describe`, `git merge-base`, `git branch --contains`, `git tag --contains`, and `git show` before concluding.
6. Treat Jenkins success or failure as an observation, not proof of root cause. Compare parameters, checkout refs, and code paths before proposing fixes.
7. Do not stop at the first failing line. Continue until you can name the owning repo, owning file or function, and the failing input or external object.
8. Default output order is: conclusion, evidence, competing hypotheses ruled out, next step.
9. If a parent Jenkins job only reports a downstream job failure, recurse into the downstream build and continue until the root failing input is explicit.
10. If the console says `Obtained Jenkinsfile` or `Obtained .ci/Jenkinsfile-*`, treat the checked-out business repo as the CI owner first. `platform/continuous-delivery` may be irrelevant.
11. If the job is a freestyle or shell job with `Build step 'Execute shell'` and no meaningful pipeline source, treat the rendered shell commands, `Makefile`, or repo-local scripts as the wrapper boundary.
12. When logs come from browser or test frameworks, prefer assertion lines, stack traces, and failing spec names over generic browser noise such as Chromium `gpu_memory_buffer_support_x11` warnings.

## When To Use
- The user gives a Jenkins build URL and asks why it failed or succeeded.
- The user mentions jobs such as `tag-fetcher`, `sds-releaser`, `tag-releaser`, `installer-releaser`, or similar XSKY CI/CD pipelines.
- A pipeline failure must be mapped back to `platform/continuous-delivery`.
- The issue involves Git tags, stable/dev lineage, branch ancestry, or unexpected `git describe` results.
- The user wants to compare a successful build and a failed build.
- The user wants to know which business repo a Jenkins job actually checked out.

## Workflow

### 0) Capture The Build Evidence
1. Use `scripts/fetch_jenkins_build.py` to fetch both `api.json` and `console.txt`.
2. Save outputs under `/tmp/xsky-cicd-debug/<job>/<build>/`.
3. Read `api.json` first for parameters, upstream builds, result, and timestamps.
4. Run `scripts/extract_console_snippets.py` on `console.txt` before reading the log manually.

### 1) Resolve The Relevant Repos
1. Run `scripts/resolve_repo_url.py` with the saved `console.txt` and `api.json`.
2. Prefer explicit checkout URLs found in Jenkins output.
3. If only repo aliases appear, inspect `platform/continuous-delivery/meta.groovy`.
4. If the helper returns nothing useful, grep the saved `console.txt` for:
- `Checking out git`
- `Fetching upstream changes from`
- `git@gitlab.xsky.com:`
- `https://gitlab.xsky.com/`
- `build job:`
5. Discard GitLab API endpoints, merge request links, and commit detail URLs. Keep only canonical repo clone URLs.

### 2) Classify The Failure Boundary
Before reading code in depth, classify where the failure actually lives:
1. Jenkins orchestration:
- wrong parameters
- wrong upstream trigger
- wrong checkout ref
- missing credential
2. CI/CD wrapper:
- Groovy pipeline in `platform/continuous-delivery`
- shell wrapper like `.CD/*.sh`
3. Runtime boundary:
- container command
- Python or shell entrypoint in the business repo
4. Business repo logic:
- builder behavior
- tag logic
- release selection
- package graph
5. External dependency surface:
- Git tag topology
- GitBuilder artifacts
- release mirror drift
- package repository inconsistency
6. Downstream build chain:
- parent job failed because a child job failed
- child job succeeded only partially
- a grandchild job exposed the real missing artifact or config

Do not stop until the boundary is explicit.

### 3) Map Jenkins To Code
1. Use `references/xsky-job-map.md` for common job-to-file mappings.
2. For `platform/continuous-delivery`, prefer the local path `/Users/peixian/wpx/xsky/continuous-delivery` when present.
3. If the local repo is missing or stale, clone `platform/continuous-delivery` read-only.
4. Inspect the repo-local `Jenkinsfile`, `.ci/Jenkinsfile-*`, or repo-local Groovy helper when the console says they were obtained from the checked-out repo.
5. Inspect the `platform/continuous-delivery` Groovy file only when the job actually comes from that repo.
6. If the job is shell-driven, follow the console into `.CD/*.sh`, `Makefile`, `build.sh`, `build.py`, `go test`, or related repo-local entrypoints.
7. If the failing line is in a business repo, continue one more hop and identify whether the real cause is:
- repo logic
- repo data or config
- an external artifact fetched by that repo
8. If the current job triggered another Jenkins job that failed, treat the current job as a wrapper and follow the child build.

### 4) Clone Business Repos Read-Only
1. Default to remote-first clone via `scripts/clone_repo_readonly.py`.
2. Clone into `/tmp/xsky-cicd-debug/repos/<repo-name>/`.
3. Use branch, tag, or commit refs from Jenkins logs instead of guessing.
4. If the repo already exists locally in the temp area, fetch instead of recloning.

### 5) Prove Or Disprove Git Hypotheses
Use `scripts/git_lineage_probe.sh` or equivalent manual commands to gather:
- `git describe --tags --abbrev=0 <ref>`
- `git describe --debug --tags --abbrev=0 <ref>`
- `git merge-base --is-ancestor <a> <b>`
- `git branch -r --contains <commit>`
- `git tag --contains <commit>`
- `git show -s --format=... <commit-or-tag>`

Always separate these two questions:
1. Is a tag related to the branch or release line?
2. Is the tag commit actually in the branch ancestry?

### 6) Trace External Artifact Or Package Failures
When the business repo fails while downloading, sizing, or validating packages:
1. Enumerate all references to the failing artifact name inside the selected build config or distro set.
2. Record the exact source URLs, not just the filename.
3. Check live headers such as `Content-Length`, then download the competing artifacts if needed.
4. Compare file sizes and hashes first.
5. If file names match but bytes differ, inspect payload contents to determine whether the difference is:
- metadata only
- build-id or signature only
- actual payload drift
6. Tie the conflicting artifact back to:
- the build config that selected the distro
- the package file that referenced the source
- the commit that introduced or changed the reference

### 7) Compare Successful And Failed Builds
1. Fetch both builds into separate directories.
2. Compare:
- Jenkins parameters
- checkout commit or branch
- `git describe` result
- pipeline revision from `platform/continuous-delivery`
- business repo commit/tag topology
3. State which variable changed and why that change matters.

### 8) Follow Downstream Build Chains
When the parent job only shows downstream failures:
1. Extract every `Scheduling project:`, `Starting building:`, and `Build <job> #<id> completed: ...` line.
2. Follow failed child builds first.
3. If a child build reports only branch-level failure, continue into the failing grandchild build.
4. Keep descending until you reach a job that fails on:
- a concrete code path
- a concrete artifact URL
- a concrete tag or branch topology check
5. Distinguish these cases:
- wrapper failure: parent job is only reporting child status
- partial success: one child succeeded so the wrapper passed, but later jobs consumed missing outputs
- root failure: the deepest child failed on a concrete missing input or invariant
6. After a child build succeeds, keep reading the parent stages. A later reporting or notification step can still fail on an external system such as TestLink, GitLab, or Feishu.

## Diagnosis Standard
The skill is only finished when it can answer all four:
1. Which system actually failed: Jenkins, CI/CD wrapper, business repo, or external dependency?
2. Which repo and file own the failing decision?
3. Which concrete input, artifact, tag, or package triggered the failure?
4. What changed: parameter, code, topology, package source, or remote artifact?

For multi-job chains, also answer:
5. Which parent job treated a partial downstream success as acceptable?
6. Which later job consumed the missing or incomplete output?

For repo-native test jobs, also answer:
7. Does the failing test or spec live inside the changed file set, or does the evidence point to a likely pre-existing flaky test or unrelated regression?

## Quick Commands
- Fetch build evidence:
  - `python3 scripts/fetch_jenkins_build.py --build-url "https://jenkins.xsky.com/job/tag-fetcher/22309/"`
- Extract useful console lines:
  - `python3 scripts/extract_console_snippets.py /tmp/xsky-cicd-debug/tag-fetcher/22309/console.txt`
- Resolve repo URLs:
  - `python3 scripts/resolve_repo_url.py --console /tmp/xsky-cicd-debug/tag-fetcher/22309/console.txt --api /tmp/xsky-cicd-debug/tag-fetcher/22309/api.json`
- Clone a business repo read-only:
  - `python3 scripts/clone_repo_readonly.py https://gitlab.xsky.com/platform/xsky-installer.git`
- Probe ancestry:
  - `scripts/git_lineage_probe.sh /tmp/xsky-cicd-debug/repos/xsky-installer stable/6.4.301 XSCALEROS_6.4.300.1`

## Common Mistakes
- Treating `git describe` as “latest release tag” instead of “nearest reachable ancestor tag”.
- Reading the entire Jenkins console before extracting the useful lines.
- Assuming every Jenkins job is a Groovy pipeline when some jobs are shell wrappers around `.CD/*.sh`.
- Assuming every Jenkins job is owned by `platform/continuous-delivery` when some jobs use repo-local `Jenkinsfile`, `.ci/Jenkinsfile-*`, or freestyle shell steps.
- Stopping at the first Python stack trace without tracing whether the real cause is in repo config, build inputs, or an external artifact source.
- Stopping at the first parent-job failure without following child jobs such as `Build <job> #<id> completed: FAILURE`.
- Missing partial-success cases where one publisher build succeeds for one variant but leaves other variants broken.
- Treating Chromium or Electron warnings as root cause when the real failure is a Cypress assertion or missing visual snapshot.
- Assuming a tag is valid for a branch just because the tag name looks related.
- Trusting only one source for repo resolution when Jenkins logs already contain the checkout URL.
- Treating GitLab API endpoints, merge request links, or commit URLs as repository clone URLs.
- Treating a same-name package as identical without checking live size or hash across different `dependence/<alias>/...` sources.
- Cherry-picking a tag commit and expecting the original tag to become reachable from the branch.

## References
- Read `references/xsky-endpoints.md` for fixed endpoints, output layout, and credential lookup.
- Read `references/xsky-job-map.md` for common Jenkins job to pipeline file mappings.
- Read `references/diagnosis-chain.md` when the failure crosses multiple ownership boundaries, such as Jenkins -> `.CD` shell -> business repo -> external artifact.
- Read `references/grep-patterns.md` when the helper scripts do not produce enough context.
