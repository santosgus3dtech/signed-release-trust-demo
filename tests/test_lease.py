from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from trustdemo.lease import issue_lease, verify_lease


def test_device_bound_lease():
    private = Ed25519PrivateKey.generate()
    lease = issue_lease("device-demo-01", private)
    assert verify_lease(lease, private.public_key(), "device-demo-01") == (True, "valid")
    assert verify_lease(lease, private.public_key(), "another-device") == (False, "device mismatch")


def test_expired_lease_is_rejected():
    private = Ed25519PrivateKey.generate()
    lease = issue_lease("device-demo-01", private, lifetime_minutes=1)
    later = datetime.now(timezone.utc) + timedelta(minutes=2)
    assert verify_lease(lease, private.public_key(), "device-demo-01", later) == (False, "lease expired")
