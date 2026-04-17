from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import ProxyEntry
from .parser import parse_formatted_proxy_line


def read_non_empty_lines(path: Path | str) -> list[str]:
    target = Path(path)
    with target.open("r", encoding="utf-8") as infile:
        return [line.strip() for line in infile if line.strip()]


def save_proxies(path: Path | str, proxies: Iterable[ProxyEntry]) -> None:
    target = Path(path)
    with target.open("w", encoding="utf-8", newline="\n") as outfile:
        for proxy in proxies:
            outfile.write(proxy.to_line() + "\n")


def load_proxies(path: Path | str) -> tuple[list[ProxyEntry], list[str]]:
    """
    Load already-formatted proxy lines (type,host,port,user,password).
    Returns: (valid_proxies, invalid_lines)
    """
    proxies: list[ProxyEntry] = []
    invalid: list[str] = []

    for line in read_non_empty_lines(path):
        proxy = parse_formatted_proxy_line(line)
        if proxy is None:
            invalid.append(line)
        else:
            proxies.append(proxy)

    return proxies, invalid
