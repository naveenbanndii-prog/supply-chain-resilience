import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scm.network import sample_network
from scm.simulation import fill_rate, single_failure_scan


class TestResilience(unittest.TestCase):
    def test_baseline_service_is_high(self):
        self.assertGreater(fill_rate(sample_network()), 0.8)

    def test_total_failure_of_all_suppliers(self):
        net = sample_network()
        self.assertEqual(fill_rate(net, {"S1": 0, "S2": 0, "S3": 0}), 0.0)

    def test_scan_sorted_by_drop(self):
        drops = [r["drop"] for r in single_failure_scan(sample_network())]
        self.assertEqual(drops, sorted(drops, reverse=True))


if __name__ == "__main__":
    unittest.main()
