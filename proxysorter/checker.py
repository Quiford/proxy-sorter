from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter
from typing import Callable, Optional

from .models import ProxyCheckResult, ProxyEntry, ProxyStatus

try:
    import socks  # type: ignore
except ImportError:  # pragma: no cover - optional dependency at runtime
    socks = None

SOCKS_TYPES = {"socks5", "socks4"}
SUPPORTED_TYPES = SOCKS_TYPES | {"http", "https"}


def _tcp_probe(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_single_proxy(
    proxy: ProxyEntry,
    target_host: str = "1.1.1.1",
    target_port: int = 443,
    tcp_timeout: float = 4.0,
    proxy_timeout: float = 8.0,
    stop_event=None,
) -> ProxyCheckResult:
    started = perf_counter()
    if stop_event is not None and stop_event.is_set():
        return ProxyCheckResult(
            proxy=proxy,
            status=ProxyStatus.SKIPPED,
            latency_ms=0,
            error="Scan stopped by user",
        )

    if proxy.proxy_type not in SUPPORTED_TYPES:
        return ProxyCheckResult(
            proxy=proxy,
            status=ProxyStatus.INVALID,
            latency_ms=0,
            error=f"Unsupported proxy type: {proxy.proxy_type}",
        )

    if not _tcp_probe(proxy.host, proxy.port, tcp_timeout):
        elapsed = int((perf_counter() - started) * 1000)
        return ProxyCheckResult(
            proxy=proxy,
            status=ProxyStatus.FAILED,
            latency_ms=elapsed,
            error="TCP connection failed",
        )

    if proxy.proxy_type in {"http", "https"}:
        elapsed = int((perf_counter() - started) * 1000)
        return ProxyCheckResult(proxy=proxy, status=ProxyStatus.WORKING, latency_ms=elapsed)

    if socks is None:
        elapsed = int((perf_counter() - started) * 1000)
        return ProxyCheckResult(
            proxy=proxy,
            status=ProxyStatus.INVALID,
            latency_ms=elapsed,
            error="PySocks is not installed",
        )

    socks_type = socks.SOCKS5 if proxy.proxy_type == "socks5" else socks.SOCKS4
    try:
        sock = socks.socksocket()
        sock.set_proxy(
            proxy_type=socks_type,
            addr=proxy.host,
            port=proxy.port,
            username=proxy.username or None,
            password=proxy.password or None,
        )
        sock.settimeout(proxy_timeout)
        sock.connect((target_host, target_port))
        sock.close()
        elapsed = int((perf_counter() - started) * 1000)
        return ProxyCheckResult(proxy=proxy, status=ProxyStatus.WORKING, latency_ms=elapsed)
    except OSError as exc:
        elapsed = int((perf_counter() - started) * 1000)
        return ProxyCheckResult(
            proxy=proxy,
            status=ProxyStatus.FAILED,
            latency_ms=elapsed,
            error=str(exc),
        )


def check_proxies(
    proxies: list[ProxyEntry],
    max_workers: int = 80,
    target_host: str = "1.1.1.1",
    target_port: int = 443,
    tcp_timeout: float = 4.0,
    proxy_timeout: float = 8.0,
    callback: Optional[Callable[[int, ProxyCheckResult], None]] = None,
    stop_event=None,
) -> list[ProxyCheckResult]:
    if not proxies:
        return []

    max_workers = max(1, min(max_workers, 500))
    results: list[Optional[ProxyCheckResult]] = [None] * len(proxies)

    def _run(index: int, entry: ProxyEntry) -> tuple[int, ProxyCheckResult]:
        result = check_single_proxy(
            entry,
            target_host=target_host,
            target_port=target_port,
            tcp_timeout=tcp_timeout,
            proxy_timeout=proxy_timeout,
            stop_event=stop_event,
        )
        return index, result

    pool = ThreadPoolExecutor(max_workers=max_workers)
    future_map = {
        pool.submit(_run, index, proxy): index for index, proxy in enumerate(proxies)
    }

    try:
        for future in as_completed(future_map):
            if stop_event is not None and stop_event.is_set():
                for pending in future_map:
                    pending.cancel()
                break

            index, result = future.result()
            results[index] = result
            if callback is not None:
                callback(index, result)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    final: list[ProxyCheckResult] = []
    for index, result in enumerate(results):
        if result is None:
            final.append(
                ProxyCheckResult(
                    proxy=proxies[index],
                    status=ProxyStatus.SKIPPED,
                    latency_ms=0,
                    error="No result",
                )
            )
        else:
            final.append(result)
    return final


def working_proxies(results: list[ProxyCheckResult]) -> list[ProxyEntry]:
    return [result.proxy for result in results if result.status == ProxyStatus.WORKING]


def summarize_results(results: list[ProxyCheckResult]) -> dict[str, int]:
    summary = {
        ProxyStatus.WORKING.value: 0,
        ProxyStatus.FAILED.value: 0,
        ProxyStatus.INVALID.value: 0,
        ProxyStatus.SKIPPED.value: 0,
    }
    for result in results:
        summary[result.status.value] = summary.get(result.status.value, 0) + 1
    return summary
