#!/usr/bin/env python3
"""Genere ou cree le questionnaire myHCL TND dans Formbricks."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
USER_AGENT = "tnd-questionnaire-import/1.0"

from questionnaire.formbricks_payload import (  # noqa: E402
    DUMMY_WORKSPACE_ID,
    build_payload,
    logical_question_count,
)

try:
    import certifi
except ImportError:  # pragma: no cover - depends on the local Python installation
    certifi = None


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


def get_ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def request_json(request: urllib.request.Request) -> dict:
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(request, timeout=60, context=get_ssl_context()) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Formbricks a refuse la requete ({error.code}) :\n{detail}") from error
    except urllib.error.URLError as error:
        raise SystemExit(f"Impossible de joindre Formbricks : {error.reason}") from error


def get_workspace_id(base_url: str, api_key: str) -> str:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/v2/me",
        headers={"x-api-key": api_key},
        method="GET",
    )
    result = request_json(request)
    data = result.get("data", result)
    workspaces = data.get("workspacePermissions", []) if isinstance(data, dict) else []
    if not workspaces and isinstance(data, dict):
        workspaces = data.get("workspaces", [])
    if not workspaces and isinstance(data, dict):
        workspaces = data.get("environmentPermissions", []) or data.get("environments", [])

    unique_workspaces: dict[str, dict] = {}
    for workspace in workspaces:
        workspace_id = workspace.get("workspaceId") or workspace.get("projectId")
        if workspace_id:
            unique_workspaces[workspace_id] = workspace

    if not unique_workspaces:
        raise SystemExit("Cle valide, mais aucun workspace accessible n'a ete trouve dans Formbricks.")
    if len(unique_workspaces) == 1:
        return next(iter(unique_workspaces))

    choices = list(unique_workspaces.items())
    print("Plusieurs workspaces sont accessibles :")
    for index, (_, workspace) in enumerate(choices, start=1):
        name = workspace.get("workspaceName") or workspace.get("projectName") or workspace.get("workspaceId")
        print(f"  {index}. {name}")

    while True:
        selection = input("Numero du workspace a utiliser : ").strip()
        if selection.isdigit() and 1 <= int(selection) <= len(choices):
            return choices[int(selection) - 1][0]
        print("Choix invalide.")


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
