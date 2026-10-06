from __future__ import annotations

import argparse
import json
from pathlib import Path

from .lease import issue_lease, verify_lease
from .release import install_release, rollback, verify_release, write_signed_manifest
from .signing import generate_keypair, load_private, load_public


def main() -> int:
    parser = argparse.ArgumentParser(description="Signed release and device trust demo")
    commands = parser.add_subparsers(dest="command", required=True)
    keys = commands.add_parser("keys")
    keys.add_argument("directory", type=Path)
    sign = commands.add_parser("sign-release")
    sign.add_argument("package", type=Path); sign.add_argument("version"); sign.add_argument("private_key", type=Path)
    verify = commands.add_parser("verify-release")
    verify.add_argument("package", type=Path); verify.add_argument("public_key", type=Path)
    install = commands.add_parser("install")
    install.add_argument("package", type=Path); install.add_argument("root", type=Path); install.add_argument("public_key", type=Path)
    back = commands.add_parser("rollback"); back.add_argument("root", type=Path)
    lease = commands.add_parser("lease")
    lease.add_argument("device_id"); lease.add_argument("private_key", type=Path); lease.add_argument("public_key", type=Path)
    args = parser.parse_args()
    if args.command == "keys":
        generate_keypair(args.directory / "private.pem", args.directory / "public.pem")
        print(f"Demo key pair created in {args.directory}")
    elif args.command == "sign-release":
        print(write_signed_manifest(args.package, args.version, args.private_key))
    elif args.command == "verify-release":
        valid, errors = verify_release(args.package, args.public_key); print(json.dumps({"valid": valid, "errors": errors}, indent=2)); return 0 if valid else 2
    elif args.command == "install":
        print(json.dumps(install_release(args.package, args.root, args.public_key), indent=2))
    elif args.command == "rollback":
        print(json.dumps(rollback(args.root), indent=2))
    elif args.command == "lease":
        payload = issue_lease(args.device_id, load_private(args.private_key)); print(json.dumps(payload, indent=2)); print(verify_lease(payload, load_public(args.public_key), args.device_id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
