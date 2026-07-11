#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from urllib.request import Request, urlopen

from common import build_dir_for, parse_build_url, require_credentials, write_json


def fetch(url: str, user: str, token: str) -> bytes:
    auth = base64.b64encode(f"{user}:{token}".encode()).decode()
    request = Request(url, headers={"Authorization": f"Basic {auth}"})
    with urlopen(request) as response:
        return response.read()


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Jenkins build metadata and console.")
    parser.add_argument("--build-url", required=True, help="Full Jenkins build URL.")
    args = parser.parse_args()

    creds = require_credentials("jenkins_user", "jenkins_token")
    job, build, base, build_path = parse_build_url(args.build_url)
    out_dir = build_dir_for(job, build)

    api_url = f"{base}/{build_path}/api/json"
    console_url = f"{base}/{build_path}/consoleText"

    api_bytes = fetch(api_url, creds["jenkins_user"], creds["jenkins_token"])
    console_bytes = fetch(console_url, creds["jenkins_user"], creds["jenkins_token"])

    api_path = out_dir / "api.json"
    console_path = out_dir / "console.txt"
    meta_path = out_dir / "meta.json"

    api_path.write_bytes(api_bytes)
    console_path.write_bytes(console_bytes)

    api_payload = json.loads(api_bytes.decode())
    parameters = {}
    for action in api_payload.get("actions", []):
        for param in action.get("parameters", []) or []:
            parameters[param["name"]] = param.get("value")

    meta = {
        "job": job,
        "build": build,
        "build_url": args.build_url,
        "api_url": api_url,
        "console_url": console_url,
        "result": api_payload.get("result"),
        "timestamp": api_payload.get("timestamp"),
        "parameters": parameters,
        "output_dir": str(out_dir),
    }
    write_json(meta_path, meta)
    print(str(out_dir))


if __name__ == "__main__":
    main()
