import unittest

from proxysorter.checker import summarize_results, working_proxies
from proxysorter.models import ProxyCheckResult, ProxyEntry, ProxyStatus


class CheckerTests(unittest.TestCase):
    def test_working_proxy_filter(self):
        proxy_a = ProxyEntry("socks5", "a.com", 1080, "u", "p")
        proxy_b = ProxyEntry("socks5", "b.com", 1080, "u", "p")
        results = [
            ProxyCheckResult(proxy=proxy_a, status=ProxyStatus.WORKING, latency_ms=10),
            ProxyCheckResult(proxy=proxy_b, status=ProxyStatus.FAILED, latency_ms=40),
        ]
        filtered = working_proxies(results)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].host, "a.com")

    def test_summary_counts(self):
        proxy = ProxyEntry("socks5", "a.com", 1080, "u", "p")
        results = [
            ProxyCheckResult(proxy=proxy, status=ProxyStatus.WORKING),
            ProxyCheckResult(proxy=proxy, status=ProxyStatus.FAILED),
            ProxyCheckResult(proxy=proxy, status=ProxyStatus.INVALID),
        ]
        summary = summarize_results(results)
        self.assertEqual(summary["WORKING"], 1)
        self.assertEqual(summary["FAILED"], 1)
        self.assertEqual(summary["INVALID"], 1)


if __name__ == "__main__":
    unittest.main()
