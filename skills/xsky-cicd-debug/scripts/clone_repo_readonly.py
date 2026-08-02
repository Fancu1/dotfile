#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from common import DEFAULT_REPOS_ROOT, build_gitlab_clone_url, ensure_dir, load_credentials, repo_name_from_url, run


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone a GitLab repo read-only into the temp debug area.")
    parser.add_argument("repo_url", help="HTTPS or SSH GitLab repo URL")
    parser.add_argument("--dest-root", default=str(DEFAULT_REPOS_ROOT), help="Destination root directory")
    args = parser.parse_args()

    creds = load_credentials()
    repo_name = repo_name_from_url(args.repo_url)
    dest_root = ensure_dir(Path(args.dest_root))
    dest = dest_root / repo_name

    clone_url = build_gitlab_clone_url(args.repo_url, creds)
    if dest.exists():
        run(["git", "-C", str(dest), "fetch", "--tags", "origin"], check=True)
    else:
        run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                clone_url,
                str(dest),
            ],
            check=True,
        )
    print(str(dest))


if __name__ == "__main__":
    main()
