"""Core package for the Quiford Proxy Sorter project."""

from .checker import check_proxies, check_single_proxy, summarize_results, working_proxies
from .io_utils import load_proxies, read_non_empty_lines, save_proxies
from .models import ProxyCheckResult, ProxyEntry, ProxyStatus
from .parser import convert_raw_lines, deduplicate_entries, parse_formatted_proxy_line, parse_raw_proxy_line

__all__ = [
    "ProxyCheckResult",
    "ProxyEntry",
    "ProxyStatus",
    "check_proxies",
    "check_single_proxy",
    "convert_raw_lines",
    "deduplicate_entries",
    "load_proxies",
    "parse_formatted_proxy_line",
    "parse_raw_proxy_line",
    "read_non_empty_lines",
    "save_proxies",
    "summarize_results",
    "working_proxies",
]
