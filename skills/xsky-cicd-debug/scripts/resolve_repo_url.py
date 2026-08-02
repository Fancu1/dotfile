#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import DEFAULT_CD_REPO, load_meta_repo_map, normalize_repo_url


CHECKOUT_RE = re.compile(r"(git@gitlab\.xsky\.com:[^\s]+|https://gitlab\.xsky\.com/[^\s]+)")
SDS_REPO_RE = re.compile(r'SDSRepoGitMap\["([^"]+)"\]')


def parse_console(console_text: str) -> dict[str, object]:
    urls = sorted(
        {
            repo_url
            for match in CHECKOUT_RE.finditer(console_text)
            if (repo_url := normalize_repo_url(match.group(1)))
        }
    )
    aliases = sorted({match.group(1) for match in SDS_REPO_RE.finditer(console_text)})
    return {"repo_urls": urls, "aliases": aliases}


def parse_api(api_path: Path) -> dict[str, object]:
    payload = json.loads(api_path.read_text())
    params = {}
    for action in payload.get("actions", []):
        for param in action.get("parameters", []) or []:
            params[param["name"]] = param.get("value")
    return {"parameters": params, "result": payload.get("result")}


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve likely repo URLs from Jenkins evidence.")
    parser.add_argument("--console", help="Path to console.txt")
    parser.add_argument("--api", help="Path to api.json")
    parser.add_argument("--repo-alias", help="Explicit repo alias to resolve through meta.groovy")
    parser.add_argument("--cd-repo", default=str(DEFAULT_CD_REPO), help="Path to continuous-delivery repo")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args()

    meta_map = load_meta_repo_map(Path(args.cd_repo))
    result: dict[str, object] = {"repo_urls": [], "aliases": [], "resolved_alias_urls": {}}

    if args.console:
        result.update(parse_console(Path(args.console).read_text(errors="replace")))

    if args.api:
        result["api"] = parse_api(Path(args.api))

    aliases = set(result.get("aliases", []))
    if args.repo_alias:
        aliases.add(args.repo_alias)

    resolved = {}
    for alias in sorted(aliases):
        if alias in meta_map:
            resolved[alias] = meta_map[alias]
    result["resolved_alias_urls"] = resolved

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return

    for repo_url in result.get("repo_urls", []):
        print(repo_url)
    for alias, repo_url in resolved.items():
        print(f"{alias} -> {repo_url}")


if __name__ == "__main__":
    main()
