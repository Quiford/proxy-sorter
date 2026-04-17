from __future__ import annotations

from typing import Iterable, Optional

from .models import ProxyEntry

SUPPORTED_PROXY_TYPES = {"socks5", "socks4", "http", "https"}


def normalize_proxy_type(proxy_type: str) -> str:
    return proxy_type.strip().lower()


def _parse_port(raw_port: str) -> Optional[int]:
    try:
        port = int(raw_port)
    except ValueError:
        return None
    if not 1 <= port <= 65535:
        return None
    return port


def _build_entry(
    proxy_type: str, host: str, port: str, username: str, password: str
) -> Optional[ProxyEntry]:
    parsed_port = _parse_port(port.strip())
    if parsed_port is None:
        return None

    host = host.strip()
    if not host:
        return None

    proxy_type = normalize_proxy_type(proxy_type)
    if proxy_type not in SUPPORTED_PROXY_TYPES:
        return None

    return ProxyEntry(
        proxy_type=proxy_type,
        host=host,
        port=parsed_port,
        username=username.strip(),
        password=password.strip(),
    )


def parse_formatted_proxy_line(line: str) -> Optional[ProxyEntry]:
    """
    Parse lines in this format:
    socks5,host,port,user,password
    """
    parts = [part.strip() for part in line.strip().split(",")]
    if len(parts) != 5:
        return None
    return _build_entry(*parts)


def parse_raw_proxy_line(line: str, default_proxy_type: str = "socks5") -> Optional[ProxyEntry]:
    """
    Parse either:
    host:port:user:password
    or:
    type:host:port:user:password
    """
    parts = [part.strip() for part in line.strip().split(":")]
    if len(parts) == 4:
        host, port, username, password = parts
        return _build_entry(default_proxy_type, host, port, username, password)
    if len(parts) == 5:
        proxy_type, host, port, username, password = parts
        return _build_entry(proxy_type, host, port, username, password)
    return None


def convert_raw_lines(
    lines: Iterable[str], default_proxy_type: str = "socks5"
) -> tuple[list[ProxyEntry], list[str]]:
    converted: list[ProxyEntry] = []
    skipped: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        proxy = parse_raw_proxy_line(stripped, default_proxy_type=default_proxy_type)
        if proxy is None:
            skipped.append(stripped)
        else:
            converted.append(proxy)
    return converted, skipped


def deduplicate_entries(entries: Iterable[ProxyEntry]) -> list[ProxyEntry]:
    unique: dict[str, ProxyEntry] = {}
    for entry in entries:
        unique[entry.id] = entry
    return list(unique.values())
