from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def generate_keypair(private_path: Path, public_path: Path) -> None:
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_key = Ed25519PrivateKey.generate()
    private_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def load_private(path: Path) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(path.read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError("Expected an Ed25519 private key")
    return key


def load_public(path: Path) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(path.read_bytes())
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError("Expected an Ed25519 public key")
    return key


def sign_payload(payload: dict, private_key: Ed25519PrivateKey) -> dict:
    body = dict(payload)
    body.pop("signature", None)
    body["signature"] = base64.b64encode(private_key.sign(canonical_json(body))).decode("ascii")
    return body


def verify_payload(payload: dict, public_key: Ed25519PublicKey) -> bool:
    body = dict(payload)
    encoded = body.pop("signature", None)
    if not isinstance(encoded, str):
        return False
    try:
        signature = base64.b64decode(encoded, validate=True)
        public_key.verify(signature, canonical_json(body))
        return True
    except (InvalidSignature, ValueError):
        return False
