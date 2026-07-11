# Jenkins Grep Patterns

Use these patterns against the saved `console.txt` before reading the full console.

## Repo Discovery
- `Checking out git`
- `Fetching upstream changes from`
- `git@gitlab.xsky.com:`
- `https://gitlab.xsky.com/`

## Pipeline Routing
- `build job:`
- `Started by upstream project`
- `originally caused by`
- `Load params`
- `Collect repos`
- `Fetch tags`

## Git Evidence
- `git describe`
- `git checkout`
- `git fetch`
- `git rev-parse`
- `git rev-list`
- `Commit message:`

## Failure Markers
- `ERROR:`
- `Finished: FAILURE`
- `Stage .* skipped due to earlier failure`
- `error '`
- `hudson.AbortException`

## Example Commands

```bash
rg -n "Checking out git|Fetching upstream changes from|git@gitlab.xsky.com:|https://gitlab.xsky.com/" console.txt
rg -n "git describe|git checkout|ERROR:|Finished: FAILURE|error '" console.txt
rg -n "Started by upstream project|build job:" console.txt
```
