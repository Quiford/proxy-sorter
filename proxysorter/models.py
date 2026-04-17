from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProxyStatus(str, Enum):
    PENDING = "PENDING"
    WORKING = "WORKING"
    FAILED = "FAILED"
    INVALID = "INVALID"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class ProxyEntry:
    proxy_type: str
    host: str
    port: int
    username: str
    password: str

    @property
    def id(self) -> str:
        return f"{self.proxy_type}:{self.host}:{self.port}:{self.username}:{self.password}"

    def to_line(self) -> str:
        return ",".join(
            [self.proxy_type, self.host, str(self.port), self.username, self.password]
        )


@dataclass
class ProxyCheckResult:
    proxy: ProxyEntry
    status: ProxyStatus
    latency_ms: Optional[int] = None
    error: str = ""
