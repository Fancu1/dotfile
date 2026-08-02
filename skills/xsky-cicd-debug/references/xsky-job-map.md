# XSKY Job Map

Use this file as a fast starting point. If Jenkins logs disagree, trust the live logs.

## CI/CD Repo Naming
- Jenkins logs may show `git@gitlab.xsky.com:platform/CD.git`.
- Treat it as the CI/CD repo alias for `https://gitlab.xsky.com/platform/continuous-delivery.git`.
- Prefer the canonical local path `/Users/peixian/wpx/xsky/continuous-delivery`.

## Common Jenkins Jobs
- `tag-fetcher`
  - pipeline: `tag-fetcher.groovy`
  - repo: `platform/continuous-delivery`
  - likely business repo source: `platform/xsky-installer`
- `sds-releaser`
  - pipeline: `sds-releaser.groovy`
  - repo: `platform/continuous-delivery`
  - often triggers `tag-fetcher`, `installer-releaser`, `sds-publisher`
- `tag-releaser`
  - pipeline: `tag-releaser.groovy`
  - repo: `platform/continuous-delivery`
  - often triggers `installer-releaser`
- `repo-releaser`
  - pipeline: `repo-releaser.groovy`
  - repo: `platform/continuous-delivery`
- `sddc-tag-fetcher`
  - pipeline: `sddc-tag-fetcher.groovy`
  - repo: `platform/continuous-delivery`
  - likely business repo source: `Overlord/sddc-installer`
- `sddc-releaser`
  - pipeline: `sddc-releaser.groovy`
  - repo: `platform/continuous-delivery`
  - often triggers `sddc-tag-fetcher`, `sddc-installer-releaser`, `sddc-publisher`
  - follow downstream jobs when parent only reports child status
- `sddc-publisher`
  - pipeline: `sddc-publisher.groovy`
  - repo: `platform/continuous-delivery`
  - often triggers multiple `sddc-installer-builder` jobs in parallel
  - may report partial success via `successJobs` and `failedJobs`
- `sddc-installer-builder`
  - primary business repo: `Overlord/sddc-installer`
  - typical failure boundary: business repo builder logic or missing artifacts from `release.xsky.com` / `gitbuilder.xsky.com`
- `installer-builder`
  - shell entry: `.CD/installer-builder.sh`
  - CI/CD source file: `installer-builder.sh`
  - primary business repo: `platform/xsky-installer`
  - typical code path: `installer-builder.sh -> build.sh -> build.py -> builder/cli.py -> builder/builder.py`
  - note: this is often a shell-driven Jenkins job, not a Groovy pipeline job
- `xt-suite-at`
  - repo-native pipeline: `.ci/Jenkinsfile-AT` in `platform/xt-suite`
  - often triggers downstream `xt-suite/<branch>` jobs, then reports results to TestLink via `.ci/at-cli.py`
  - typical failure boundary: repo-local pipeline logic or external TestLink plan/config, not `platform/continuous-delivery`
- `wizard-e2e-test`
  - repo-native pipeline: `Jenkinsfile` -> `build/cypress.groovy` in `front-end/xsky-wizard`
  - typical failure boundary: Cypress spec under `cypress/e2e` or `cypress/vt/tests`
  - common noise: Chromium `gpu_memory_buffer_support_x11` warnings; prefer `CypressError`, `AssertionError`, spec path, and report URL
- `afs-pr-check`
  - MR-triggered freestyle or shell job for `overlord/afs-adm`
  - typical code path: workspace checkout -> `make binary` -> `go test`
  - locate the failing package and test case from `--- FAIL:` / `FAIL` output before inferring whether the MR caused it

## Repo Alias Sources
When a job uses `SDSRepoGitMap["alias"]`, inspect `meta.groovy` in `platform/continuous-delivery`.

Examples:
- `installer` -> `platform/xsky-installer`
- `xsky-demon` -> `platform/xsky-demon`
- `object-routing` -> `platform/object-routing`
- `xmd-api` -> `front-end/agw`
- `sddc-installer` -> `Overlord/sddc-installer`

## Typical Failure Surfaces
- Jenkins parameter mismatch
- wrong branch or tag checkout
- `git describe` / tag ancestry mismatch
- remote script behavior from `lib/cli.sh`
- shell job behavior from `.CD/*.sh`
- repo-native pipeline behavior from `Jenkinsfile`, `.ci/Jenkinsfile-*`, or repo-local Groovy helpers
- business repo runtime behavior from `build.sh`, `build.py`, or repo-local builders
- repo-local test harness behavior from `pytest`, `Cypress`, `go test`, or repo-local reporting scripts
- external artifact drift from `gitbuilder.xsky.com` or release mirrors
- external reporting drift from TestLink, GitLab commit status, or chat notification hooks
- same-name package collisions across `dependence/<alias>/...`
- downstream-job failure propagation or partial-success masking
- repo alias resolving to an unexpected business repo
