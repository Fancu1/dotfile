# XSKY CI/CD Endpoints

## Jenkins
- Base URL: `https://jenkins.xsky.com`
- Build JSON API:
  - `<build-url>api/json`
- Build console text:
  - `<build-url>consoleText`

## GitLab
- Base URL: `https://gitlab.xsky.com`
- CI/CD repo:
  - `https://gitlab.xsky.com/platform/continuous-delivery`
- Common HTTPS clone form:
  - `https://gitlab.xsky.com/<group>/<repo>.git`

## Preferred Local CI/CD Repo
- `/Users/peixian/wpx/xsky/continuous-delivery`

Use this local repo for fast pipeline code lookup when it exists. Business repos should still default to remote-first read-only clone.

## Output Layout
Store fetched evidence under:

```text
/tmp/xsky-cicd-debug/
  <job>/
    <build>/
      api.json
      console.txt
      meta.json
      snippets.txt
      summary.json
```

Store cloned repos under:

```text
/tmp/xsky-cicd-debug/repos/<repo-name>/
```

## Credential Lookup
The scripts should read credentials in this order:
1. Environment variables
2. `~/.config/xsky-cicd-debug/credentials.json`

Supported keys:
- Jenkins:
  - `XSKY_JENKINS_USER`
  - `XSKY_JENKINS_TOKEN`
  - config keys: `jenkins_user`, `jenkins_token`
- GitLab:
  - `XSKY_GITLAB_USER`
  - `XSKY_GITLAB_TOKEN`
  - config keys: `gitlab_user`, `gitlab_token`

## Suggested Private Config Shape

```json
{
  "jenkins_user": "your-user",
  "jenkins_token": "your-token",
  "gitlab_user": "clawbot",
  "gitlab_token": "your-pat"
}
```

Do not put secrets into the skill files themselves.
