from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .signing import sign_payload, verify_payload


def issue_lease(device_id: str, private_key: Ed25519PrivateKey, lifetime_minutes: int = 15) -> dict:
    if lifetime_minutes < 1 or lifetime_minutes > 1440:
        raise ValueError("Lease lifetime must be between 1 and 1440 minutes")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return sign_payload(
        {
            "schema": 1,
            "audience": "trust-demo-app",
            "device_id": device_id,
            "nonce": str(uuid4()),
            "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(minutes=lifetime_minutes)).isoformat(),
        },
        private_key,
    )


def verify_lease(lease: dict, public_key: Ed25519PublicKey, expected_device_id: str, now: datetime | None = None) -> tuple[bool, str]:
    if not verify_payload(lease, public_key):
        return False, "signature invalid"
    if lease.get("audience") != "trust-demo-app":
        return False, "audience mismatch"
    if lease.get("device_id") != expected_device_id:
        return False, "device mismatch"
    current = now or datetime.now(timezone.utc)
    expires_at = datetime.fromisoformat(lease["expires_at"])
    if current >= expires_at:
        return False, "lease expired"
    return True, "valid"
