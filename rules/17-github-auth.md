---
description: GitHub auth for gh/PR operations (secure token handling, least privilege, no secret leaks)
globs: ["**/*"]
alwaysApply: false
---

## Scope
- Applies when: 涉及 GitHub（读取 PR/Issues、评论、创建 PR、CI 日志、`gh`/`git` 远端操作）
- Does NOT apply when: 仅本地编码/本地测试，不触发任何远端调用

## Non-Negotiable (Security)
- **禁止把 token/密钥写入仓库**：包括 `.env`、源码、测试数据、docs、日志、commit message。
- **禁止在终端输出/回显 token**：不要 `echo $GH_TOKEN`，不要开启 `set -x` 执行包含 token 的脚本。
- **默认使用 GitHub CLI 的 keyring 登录态**（最安全、最少人工干预）；只有在确实需要时才使用环境变量 token。

## Recommended Setup (One-time, Safe)
优先用 `gh` 的登录态（macOS Keychain / keyring），让 Codex 直接调用 `gh` 即可访问私有 repo/PR：

1) 检查登录状态：
   - `gh auth status -h github.com`
2) 如未登录（或权限不足），用“细粒度/最小权限”的 PAT：
   - 建议创建 Fine-grained PAT（设置到期时间），只授予需要的仓库与权限（通常至少 `Contents` + `Pull requests`，按需加 `Issues`）。
   - 安全登录（token 不进 shell 历史、不落盘）：
     - `read -s GH_TOKEN; echo "$GH_TOKEN" | gh auth login -h github.com --git-protocol ssh --with-token; unset GH_TOKEN`

> 说明：`gh` 会优先使用 keyring/Keychain 存储凭证，后续 Codex 使用 `gh pr view` / `gh api` 不需要你再手动设置环境变量。

## How Codex Should Fetch PR Content (Private Repos)
- 优先使用 `gh`，不要用网页抓取（私有仓库会 404）：
  - `gh pr view <PR_NUMBER> --repo OWNER/REPO`
  - `gh pr view <PR_NUMBER> --repo OWNER/REPO --json title,body,files,commits`
  - `gh api repos/OWNER/REPO/pulls/<PR_NUMBER>`（必要时）
- 如果不在目标仓库目录，显式带 `--repo OWNER/REPO`（或设置 `GH_REPO=OWNER/REPO`）。

## Env Vars (Fallback; Avoid Persisting Secrets)
`gh` 支持 `GH_TOKEN` / `GITHUB_TOKEN`，并且它们会覆盖已存储凭证；除非你明确要求“强制用某个 token”，否则不要长期 export。

如确实需要为“当前一次命令”注入 token，推荐从系统安全存储读取（示例用占位符，你自行填）：

1) 把 token 放进 macOS Keychain（一次性）：
   - `security add-generic-password -a "$USER" -s "codex-gh-token" -w "<YOUR_GH_TOKEN>" -U`
2) 运行命令时临时注入（不打印 token）：
   - `GH_TOKEN="$(security find-generic-password -a "$USER" -s "codex-gh-token" -w)" gh pr view <PR_NUMBER> --repo OWNER/REPO`

注意：
- 这类写法会让 token 出现在子进程环境变量里；不要在共享机器上使用。
- 不要把上述命令（含真实 token）放进脚本仓库或文档；只写占位符。
