import unittest

from proxysorter.models import ProxyEntry
from proxysorter.parser import (
    convert_raw_lines,
    deduplicate_entries,
    parse_formatted_proxy_line,
    parse_raw_proxy_line,
)


class ParserTests(unittest.TestCase):
    def test_parse_raw_line(self):
        proxy = parse_raw_proxy_line("example.com:1080:user:pass")
        self.assertIsNotNone(proxy)
        assert proxy is not None
        self.assertEqual(proxy.proxy_type, "socks5")
        self.assertEqual(proxy.host, "example.com")
        self.assertEqual(proxy.port, 1080)

    def test_parse_formatted_line(self):
        proxy = parse_formatted_proxy_line("socks5,example.com,1080,user,pass")
        self.assertIsNotNone(proxy)
        assert proxy is not None
        self.assertEqual(proxy.proxy_type, "socks5")
        self.assertEqual(proxy.username, "user")

    def test_convert_raw_lines_with_skips(self):
        converted, skipped = convert_raw_lines(
            ["host1:1080:user:pass", "badline", "host2:70000:user:pass"]
        )
        self.assertEqual(len(converted), 1)
        self.assertEqual(len(skipped), 2)

    def test_deduplicate_entries(self):
        entries = [
            ProxyEntry("socks5", "a.com", 1080, "u", "p"),
            ProxyEntry("socks5", "a.com", 1080, "u", "p"),
            ProxyEntry("socks5", "b.com", 1080, "u", "p"),
        ]
        deduped = deduplicate_entries(entries)
        self.assertEqual(len(deduped), 2)


if __name__ == "__main__":
    unittest.main()
