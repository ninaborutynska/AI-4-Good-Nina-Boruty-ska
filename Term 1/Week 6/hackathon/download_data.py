"""Read-only GitHub download into a separate snapshot; never alters the collector."""
import argparse
import json
import os
import re
from pathlib import Path
import requests

BASE = Path(__file__).resolve().parent

def download(repository, ref, destination, token):
    if not token:
        raise ValueError("Set GITHUB_TOKEN locally; a GitHub connector connection does not provide a token to Python")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError("Invalid repository name")
    session = requests.Session()
    session.headers.update(Authorization=f"Bearer {token}", Accept="application/vnd.github+json", **{"X-GitHub-Api-Version": "2022-11-28"})
    def get(url, raw=False, optional=False):
        response = session.get(url, headers={"Accept": "application/vnd.github.raw+json" if raw else "application/vnd.github+json"}, timeout=30)
        if optional and response.status_code == 404: return None
        if not response.ok:
            raise ValueError(f"GitHub access failed (HTTP {response.status_code}); check account, repository permission, and request limits")
        return response.content if raw else response.json()
    from urllib.parse import quote
    api = f"https://api.github.com/repos/{repository}"
    sha = get(f"{api}/commits/{quote(ref, safe='')}")["sha"]
    if not re.fullmatch(r"[a-f0-9]{40}", sha): raise ValueError("Invalid GitHub commit response")
    folder = destination / sha
    data = folder / "data"
    data.mkdir(parents=True, exist_ok=True)
    files = ["youtube_comments.csv", "collection_log.csv", "monitoring_started.txt", "sentiment_results.csv", "processing_status.csv", "manual_labels.csv", "evaluation.json"]
    for name in files:
        content = get(f"{api}/contents/{quote('Hackathon 6/data/' + name, safe='/')}?ref={sha}", raw=True, optional=name != "youtube_comments.csv")
        if content is None: continue
        target = data / name
        if target.exists():
            if target.read_bytes() != content: raise ValueError("Snapshot content differs from existing file; refusing to overwrite")
        else:
            with target.open("xb") as handle: handle.write(content)
    workflows = get(f"{api}/contents/.github/workflows?ref={sha}", optional=True) or []
    for entry in workflows:
        name = entry.get("name", "")
        if not re.fullmatch(r"[\w .-]+\.ya?ml", name): continue
        content = get(f"{api}/contents/.github/workflows/{quote(name)}?ref={sha}", raw=True)
        target = folder / "workflows" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            with target.open("xb") as handle: handle.write(content)
    manifest = dict(repository=repository, commit=sha, data_directory=str(data), collector_workflows_directory=str(folder / "workflows"))
    (destination / "latest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default="LuukAalders/Hackathons")
    parser.add_argument("--ref", default="main")
    parser.add_argument("--destination", type=Path, default=BASE / "snapshots")
    args = parser.parse_args()
    try: download(args.repository, args.ref, args.destination, os.environ.get("GITHUB_TOKEN", ""))
    except (ValueError, requests.RequestException) as error: raise SystemExit(f"Data download stopped safely: {error}")
