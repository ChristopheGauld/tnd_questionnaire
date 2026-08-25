#!/usr/bin/env python3
"""Genere ou cree le questionnaire myHCL TND dans Formbricks."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from questionnaire.formbricks_payload import (  # noqa: E402
    DUMMY_WORKSPACE_ID,
    build_payload,
    logical_question_count,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.getenv("FORMBRICKS_URL", "https://app.formbricks.com"))
    parser.add_argument("--workspace-id", default=os.getenv("FORMBRICKS_WORKSPACE_ID"))
    parser.add_argument("--api-key", default=os.getenv("FORMBRICKS_API_KEY"))
    parser.add_argument("--output", type=Path, help="Ecrit aussi le JSON genere dans ce fichier.")
    parser.add_argument("--publish", action="store_true", help="Publie le questionnaire immediatement.")
    parser.add_argument("--upload", action="store_true", help="Cree le questionnaire dans Formbricks.")
    return parser.parse_args()


def write_payload(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def request_json(request: urllib.request.Request) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Formbricks a refuse la requete ({error.code}) :\n{detail}") from error
    except urllib.error.URLError as error:
        raise SystemExit(f"Impossible de joindre Formbricks : {error.reason}") from error


def get_workspace_id(base_url: str, api_key: str) -> str:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/v1/me",
        headers={"x-api-key": api_key},
        method="GET",
    )
    result = request_json(request)
    data = result.get("data", result)
    workspace = data.get("workspace", {}) if isinstance(data, dict) else {}
    workspace_id = workspace.get("id") if isinstance(workspace, dict) else None
    if not workspace_id:
        raise SystemExit("Cle valide, mais identifiant du workspace introuvable dans la reponse Formbricks.")
    return workspace_id


def upload_payload(base_url: str, api_key: str, payload: dict) -> dict:
    endpoint = f"{base_url.rstrip('/')}/api/v3/surveys?createdFrom=blank"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        method="POST",
    )
    return request_json(request)


def main() -> None:
    args = parse_args()
    api_key = args.api_key
    workspace_id = args.workspace_id

    if args.upload:
        if not api_key:
            api_key = getpass.getpass("Collez la cle API Formbricks (elle restera masquee) : ").strip()
        if not api_key:
            raise SystemExit("Une cle API Formbricks est requise pour creer le questionnaire.")
        if not workspace_id:
            print("Verification de la cle et detection du workspace...")
            workspace_id = get_workspace_id(args.base_url, api_key)

    workspace_id = workspace_id or DUMMY_WORKSPACE_ID
    payload = build_payload(workspace_id, publish=args.publish)

    if args.output:
        write_payload(args.output, payload)
        print(f"JSON ecrit dans {args.output}")

    print(f"{len(payload['blocks'])} blocs, {logical_question_count(payload)} questions logiques.")

    if not args.upload:
        return

    result = upload_payload(args.base_url, api_key, payload)
    data = result.get("data", result)
    survey_id = data.get("id") if isinstance(data, dict) else None
    if not survey_id:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit("Questionnaire cree, mais identifiant de questionnaire introuvable dans la reponse.")

    public_url = f"{args.base_url.rstrip('/')}/s/{survey_id}?offlineSupport=true"
    print(f"Questionnaire cree : {survey_id}")
    if args.publish:
        print(f"Lien public avec reprise de progression : {public_url}")
    else:
        print("Le questionnaire est en brouillon. Relisez-le dans Formbricks avant de le publier.")


if __name__ == "__main__":
    main()
