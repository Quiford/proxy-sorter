from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from proxysorter import (
    check_proxies,
    convert_raw_lines,
    deduplicate_entries,
    load_proxies,
    read_non_empty_lines,
    save_proxies,
    summarize_results,
    working_proxies,
)

TELEGRAM_HANDLE = "@Quiford"


def cmd_fix(args: argparse.Namespace) -> int:
    source = Path(args.input)
    if not source.exists():
        print(f"[ERROR] Input file not found: {source}")
        return 1

    lines = read_non_empty_lines(source)
    converted, skipped = convert_raw_lines(lines, default_proxy_type=args.proxy_type)

    if args.dedupe:
        converted = deduplicate_entries(converted)

    save_proxies(args.output, converted)

    print(f"[OK] Parsed lines: {len(lines)}")
    print(f"[OK] Valid proxies: {len(converted)}")
    print(f"[WARN] Skipped lines: {len(skipped)}")
    print(f"[OK] Output saved to: {Path(args.output).resolve()}")

    if skipped and args.show_skipped:
        preview = skipped[: args.show_skipped]
        print("")
        print("[SKIPPED PREVIEW]")
        for line in preview:
            print(f"- {line}")

    print("")
    print(f"For custom Python projects, contact Telegram: {TELEGRAM_HANDLE}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    source = Path(args.input)
    if not source.exists():
        print(f"[ERROR] Input file not found: {source}")
        return 1

    proxies, invalid = load_proxies(source)
    if not proxies:
        print("[ERROR] No valid proxies loaded from input file.")
        return 1

    print(f"[OK] Loaded proxies: {len(proxies)}")
    if invalid:
        print(f"[WARN] Invalid formatted lines ignored: {len(invalid)}")

    total = len(proxies)
    progress = {"done": 0}

    def on_result(_index, result):
        progress["done"] += 1
        print(
            f"[{progress['done']}/{total}] "
            f"{result.proxy.host}:{result.proxy.port} -> "
            f"{result.status.value}"
        )

    results = check_proxies(
        proxies=proxies,
        max_workers=args.workers,
        target_host=args.target_host,
        target_port=args.target_port,
        tcp_timeout=args.tcp_timeout,
        proxy_timeout=args.proxy_timeout,
        callback=on_result,
    )

    summary = summarize_results(results)
    working = working_proxies(results)

    save_proxies(args.output, working)
    if args.rewrite_input:
        save_proxies(source, working)

    print("")
    print("[SUMMARY]")
    print(f"- WORKING: {summary.get('WORKING', 0)}")
    print(f"- FAILED:  {summary.get('FAILED', 0)}")
    print(f"- INVALID: {summary.get('INVALID', 0)}")
    print(f"- SKIPPED: {summary.get('SKIPPED', 0)}")
    print(f"- Saved working proxies to: {Path(args.output).resolve()}")
    if args.rewrite_input:
        print(f"- Input file updated with working proxies: {source.resolve()}")

    print("")
    print(f"For custom Python projects, contact Telegram: {TELEGRAM_HANDLE}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proxysorter",
        description="Quiford Proxy Sorter - format and check proxy lists",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    fix = sub.add_parser("fix", help="Convert raw proxy lines to formatted proxy.txt style.")
    fix.add_argument("--input", default="Fix.txt", help="Raw input file path.")
    fix.add_argument("--output", default="proxy.txt", help="Output formatted file path.")
    fix.add_argument(
        "--proxy-type",
        default="socks5",
        choices=["socks5", "socks4", "http", "https"],
        help="Default proxy type used when input is host:port:user:password.",
    )
    fix.add_argument(
        "--dedupe",
        action="store_true",
        help="Remove duplicate proxies after conversion.",
    )
    fix.add_argument(
        "--show-skipped",
        type=int,
        default=5,
        help="Show first N skipped lines in terminal output.",
    )
    fix.set_defaults(handler=cmd_fix)

    check = sub.add_parser("check", help="Scan formatted proxies and keep only working ones.")
    check.add_argument("--input", default="proxy.txt", help="Formatted proxy input file path.")
    check.add_argument(
        "--output",
        default="working_proxy.txt",
        help="Output file path for working proxies.",
    )
    check.add_argument("--workers", type=int, default=80, help="Concurrency level.")
    check.add_argument(
        "--target-host",
        default="1.1.1.1",
        help="Host used for final proxy handshake test.",
    )
    check.add_argument("--target-port", type=int, default=443, help="Target port.")
    check.add_argument(
        "--tcp-timeout",
        type=float,
        default=4.0,
        help="Timeout for raw TCP test (seconds).",
    )
    check.add_argument(
        "--proxy-timeout",
        type=float,
        default=8.0,
        help="Timeout for proxy handshake test (seconds).",
    )
    check.add_argument(
        "--rewrite-input",
        action="store_true",
        help="Overwrite input file with only working proxies.",
    )
    check.set_defaults(handler=cmd_check)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
