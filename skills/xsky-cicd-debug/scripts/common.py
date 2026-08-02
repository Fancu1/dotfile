#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_OUTPUT_ROOT = Path("/tmp/xsky-cicd-debug")
DEFAULT_REPOS_ROOT = DEFAULT_OUTPUT_ROOT / "repos"
DEFAULT_CREDENTIALS_PATH = Path.home() / ".config" / "xsky-cicd-debug" / "credentials.json"
DEFAULT_CD_REPO = Path("/Users/peixian/wpx/xsky/continuous-delivery")
GITLAB_NON_REPO_SEGMENTS = {
    "-",
    "api",
    "blob",
    "commits",
    "compare",
    "issues",
    "jobs",
    "merge_requests",
    "pipelines",
    "raw",
    "repository",
    "snippets",
    "tree",
    "wikis",
}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_credentials() -> dict[str, str]:
    data: dict[str, str] = {}
    if DEFAULT_CREDENTIALS_PATH.exists():
        data.update(json.loads(DEFAULT_CREDENTIALS_PATH.read_text()))
    env_map = {
        "jenkins_user": "XSKY_JENKINS_USER",
        "jenkins_token": "XSKY_JENKINS_TOKEN",
        "gitlab_user": "XSKY_GITLAB_USER",
        "gitlab_token": "XSKY_GITLAB_TOKEN",
    }
    for key, env_key in env_map.items():
        value = os.getenv(env_key)
        if value:
            data[key] = value
    data.setdefault("gitlab_user", "clawbot")
    return data


def require_credentials(*keys: str) -> dict[str, str]:
    creds = load_credentials()
    missing = [key for key in keys if not creds.get(key)]
    if missing:
        raise SystemExit(
            "Missing credentials: {}. Set env vars or create {}.".format(
                ", ".join(missing), DEFAULT_CREDENTIALS_PATH
            )
        )
    return creds


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=capture_output,
        check=check,
    )


def parse_build_url(build_url: str) -> tuple[str, int, str, str]:
    parsed = urlparse(build_url)
    parts = [part for part in parsed.path.split("/") if part]
    if "job" not in parts:
        raise ValueError(f"Unsupported Jenkins build URL: {build_url}")
    job_parts: list[str] = []
    build: int | None = None
    i = 0
    while i < len(parts):
        if parts[i] == "job" and i + 1 < len(parts):
            job_parts.append(parts[i + 1])
            i += 2
            continue
        if parts[i].isdigit():
            build = int(parts[i])
            break
        i += 1
    if not job_parts or build is None:
        raise ValueError(f"Unsupported Jenkins build URL: {build_url}")
    job = "__".join(job_parts)
    base = f"{parsed.scheme}://{parsed.netloc}"
    build_path = "/".join(parts[: i + 1])
    return job, build, base, build_path


def build_dir_for(job: str, build: int) -> Path:
    return ensure_dir(DEFAULT_OUTPUT_ROOT / job / str(build))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n")


def normalize_repo_url(url: str) -> str:
    url = url.strip().strip("'\"),];")
    if url.endswith(".git."):
        url = url[:-1]
    if url.startswith("git@gitlab.xsky.com:"):
        suffix = url.split(":", 1)[1]
        url = f"https://gitlab.xsky.com/{suffix}"
    parsed = urlparse(url)
    if parsed.netloc != "gitlab.xsky.com":
        return url

    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return ""
    if parts[:2] == ["platform", "CD"] or parts[:2] == ["platform", "CD.git"]:
        return "https://gitlab.xsky.com/platform/continuous-delivery.git"
    if any(part in GITLAB_NON_REPO_SEGMENTS for part in parts):
        return ""

    repo_path = "/".join(parts)
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    if not repo_path:
        return ""
    return f"https://gitlab.xsky.com/{repo_path}.git"


def build_gitlab_clone_url(repo_url: str, creds: dict[str, str]) -> str:
    normalized = normalize_repo_url(repo_url)
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"Unsupported repo URL: {repo_url}")
    if creds.get("gitlab_user") and creds.get("gitlab_token"):
        return (
            f"{parsed.scheme}://{creds['gitlab_user']}:{creds['gitlab_token']}"
            f"@{parsed.netloc}{parsed.path}"
        )
    return normalized


def repo_name_from_url(repo_url: str) -> str:
    path = urlparse(normalize_repo_url(repo_url)).path
    name = Path(path).name
    return name[:-4] if name.endswith(".git") else name


def load_meta_repo_map(cd_repo: Path | None = None) -> dict[str, str]:
    repo = cd_repo or DEFAULT_CD_REPO
    meta = repo / "meta.groovy"
    if not meta.exists():
        return {}
    text = meta.read_text()
    mapping: dict[str, str] = {}
    pattern = re.compile(r'"([^"]+)":\s*"([^"]+)"')
    for alias, path in pattern.findall(text):
        mapping[alias] = f"https://gitlab.xsky.com/{path}.git"
    return mapping
