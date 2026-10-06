from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .signing import load_private, load_public, sign_payload, verify_payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(package_dir: Path, version: str) -> dict:
    files = []
    for path in sorted(item for item in package_dir.rglob("*") if item.is_file()):
        files.append({"path": path.relative_to(package_dir).as_posix(), "size": path.stat().st_size, "sha256": sha256(path)})
    if not files:
        raise ValueError("Release package is empty")
    return {
        "schema": 1,
        "product": "trust-demo-app",
        "version": version,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "files": files,
    }


def write_signed_manifest(package_dir: Path, version: str, private_key_path: Path) -> Path:
    signed = sign_payload(build_manifest(package_dir, version), load_private(private_key_path))
    destination = package_dir / "release-manifest.json"
    destination.write_text(json.dumps(signed, indent=2), encoding="utf-8")
    return destination


def verify_release(package_dir: Path, public_key_path: Path) -> tuple[bool, list[str]]:
    manifest_path = package_dir / "release-manifest.json"
    if not manifest_path.exists():
        return False, ["manifest missing"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not verify_payload(manifest, load_public(public_key_path)):
        return False, ["signature invalid"]
    errors = []
    for entry in manifest.get("files", []):
        path = (package_dir / entry["path"]).resolve()
        if package_dir.resolve() not in path.parents:
            errors.append(f"unsafe path: {entry['path']}")
        elif not path.is_file():
            errors.append(f"missing: {entry['path']}")
        elif path.stat().st_size != entry["size"] or sha256(path) != entry["sha256"]:
            errors.append(f"hash mismatch: {entry['path']}")
    return not errors, errors


def install_release(package_dir: Path, install_root: Path, public_key_path: Path) -> dict:
    valid, errors = verify_release(package_dir, public_key_path)
    if not valid:
        raise ValueError("Release rejected: " + "; ".join(errors))
    manifest = json.loads((package_dir / "release-manifest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    versions = install_root / "versions"
    destination = versions / version
    if destination.exists():
        raise ValueError(f"Version {version} is already installed")
    versions.mkdir(parents=True, exist_ok=True)
    previous = active_version(install_root)
    shutil.copytree(package_dir, destination)
    state = {"active": version, "previous": previous, "activated_at": datetime.now(timezone.utc).isoformat()}
    _write_state(install_root, state)
    return state


def active_version(install_root: Path) -> str | None:
    state_path = install_root / "state.json"
    return json.loads(state_path.read_text(encoding="utf-8"))["active"] if state_path.exists() else None


def rollback(install_root: Path) -> dict:
    state_path = install_root / "state.json"
    if not state_path.exists():
        raise ValueError("No installation state found")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not state.get("previous"):
        raise ValueError("No previous version is available")
    state["active"], state["previous"] = state["previous"], state["active"]
    state["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
    _write_state(install_root, state)
    return state


def _write_state(install_root: Path, state: dict) -> None:
    install_root.mkdir(parents=True, exist_ok=True)
    temporary = install_root / "state.json.tmp"
    temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temporary.replace(install_root / "state.json")
