from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .challenge import DEFAULT_NAMESPACE, DEFAULT_TTL_SECONDS, create_challenge
from .signer import OpenSSHError, sign_message, verify_signature


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except OpenSSHError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ssh-challenge-safe-vps-login",
        description="Create, sign, and verify OpenSSH login challenges.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(required=True)

    create_parser = subparsers.add_parser("create-challenge", help="create a canonical challenge")
    create_parser.add_argument("--service", required=True)
    create_parser.add_argument("--origin", required=True)
    create_parser.add_argument("--username", required=True)
    create_parser.add_argument("--operation", default="login")
    create_parser.add_argument("--client-ip")
    create_parser.add_argument("--ttl", type=int, default=DEFAULT_TTL_SECONDS)
    create_parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    create_parser.add_argument("--json", action="store_true")
    create_parser.set_defaults(func=_create_challenge)

    sign_parser = subparsers.add_parser("sign", help="sign a challenge message")
    sign_parser.add_argument("--key", required=True, type=Path)
    sign_parser.add_argument("--message-file", required=True, type=Path)
    sign_parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    sign_parser.set_defaults(func=_sign)

    verify_parser = subparsers.add_parser("verify", help="verify a challenge signature")
    verify_parser.add_argument("--allowed-signers", required=True, type=Path)
    verify_parser.add_argument("--identity", required=True)
    verify_parser.add_argument("--message-file", required=True, type=Path)
    verify_parser.add_argument("--signature-file", required=True, type=Path)
    verify_parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    verify_parser.set_defaults(func=_verify)

    return parser


def _create_challenge(args: argparse.Namespace) -> int:
    challenge = create_challenge(
        service=args.service,
        origin=args.origin,
        username=args.username,
        operation=args.operation,
        client_ip=args.client_ip,
        ttl_seconds=args.ttl,
        namespace=args.namespace,
        now=datetime.now(UTC),
    )
    if args.json:
        print(
            json.dumps(
                {
                    **challenge.to_dict(),
                    "message": challenge.message(),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(challenge.message())
    return 0


def _sign(args: argparse.Namespace) -> int:
    message = args.message_file.read_text(encoding="utf-8")
    print(sign_message(key_path=args.key, message=message, namespace=args.namespace), end="")
    return 0


def _verify(args: argparse.Namespace) -> int:
    message = args.message_file.read_text(encoding="utf-8")
    signature = args.signature_file.read_text(encoding="utf-8")
    valid = verify_signature(
        allowed_signers_path=args.allowed_signers,
        identity=args.identity,
        message=message,
        signature=signature,
        namespace=args.namespace,
    )
    print("valid" if valid else "invalid")
    return 0 if valid else 1

