# Signed Release Trust Demo

🇧🇷 [Leia este README em Português (Brasil)](README.pt-BR.md).

A focused security demo for Ed25519-signed release manifests, verified installation, atomic activation, rollback and short-lived device leases.

![Signed release trust flow](docs/images/trust-flow.svg)

## What it demonstrates

- Canonical JSON before signing.
- Ed25519 key generation, signing and verification.
- Per-file SHA-256 and size validation.
- Rejection of missing, modified and path-escaping payloads.
- Versioned installation with atomic state updates.
- One-step rollback to the previous verified release.
- Device-bound leases with audience, nonce and expiration checks.

## Quick start

```bash
python -m pip install -e .
python -m trustdemo.cli keys demo-workspace/keys
```

Create a package directory containing at least one file, then:

```bash
python -m trustdemo.cli sign-release demo-workspace/package 1.0.0 demo-workspace/keys/private.pem
python -m trustdemo.cli verify-release demo-workspace/package demo-workspace/keys/public.pem
python -m trustdemo.cli install demo-workspace/package demo-workspace/install demo-workspace/keys/public.pem
```

## Test

```bash
python -m pip install pytest
pytest -q
```

## Security boundary

This repository is an independent implementation around a fictional application. It contains no game automation, injection code, bypass logic, detection indicators, production signing keys, customer accounts, payment code or proprietary release material. Demo private keys and workspaces are ignored by Git.

## License

MIT
