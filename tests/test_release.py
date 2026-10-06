from pathlib import Path

import pytest

from trustdemo.release import active_version, install_release, rollback, verify_release, write_signed_manifest
from trustdemo.signing import generate_keypair


def package(root: Path, version: str, content: str, private_key: Path) -> Path:
    path = root / f"package-{version}"
    path.mkdir()
    (path / "app.txt").write_text(content, encoding="utf-8")
    write_signed_manifest(path, version, private_key)
    return path


def test_signed_install_and_rollback(tmp_path: Path):
    keys = tmp_path / "keys"; generate_keypair(keys / "private.pem", keys / "public.pem")
    install_root = tmp_path / "install"
    first = package(tmp_path, "1.0.0", "first", keys / "private.pem")
    second = package(tmp_path, "1.1.0", "second", keys / "private.pem")
    install_release(first, install_root, keys / "public.pem")
    install_release(second, install_root, keys / "public.pem")
    assert active_version(install_root) == "1.1.0"
    assert rollback(install_root)["active"] == "1.0.0"


def test_tampered_payload_is_rejected(tmp_path: Path):
    keys = tmp_path / "keys"; generate_keypair(keys / "private.pem", keys / "public.pem")
    release = package(tmp_path, "1.0.0", "original", keys / "private.pem")
    (release / "app.txt").write_text("tampered", encoding="utf-8")
    valid, errors = verify_release(release, keys / "public.pem")
    assert valid is False
    assert errors == ["hash mismatch: app.txt"]
    with pytest.raises(ValueError, match="Release rejected"):
        install_release(release, tmp_path / "install", keys / "public.pem")
