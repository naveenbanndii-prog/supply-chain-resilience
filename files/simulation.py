"""Resilience analysis: fill rate, single-point-of-failure scan, Monte Carlo."""
import random
from statistics import mean

from .maxflow import max_flow


def fill_rate(net, disruptions=None):
    """Share of total demand that can be served (0..1)."""
    if net.total_demand == 0:
        return 1.0
    delivered = max_flow(net.flow_graph(disruptions), "SOURCE", "SINK")
    return min(1.0, delivered / net.total_demand)


def single_failure_scan(net, severity=1.0):
    """Fail each non-market node in turn. Returns list sorted by worst impact."""
    base = fill_rate(net)
    rows = []
    for n in net.nodes.values():
        if n.tier == "market":
            continue
        fr = fill_rate(net, {n.name: 1.0 - severity})
        rows.append({"node": n.name, "tier": n.tier, "fill_rate": fr, "drop": base - fr})
    return sorted(rows, key=lambda r: r["drop"], reverse=True)


def monte_carlo(net, fail_prob=None, severity=(0.5, 1.0), runs=2000, seed=42):
    """Randomly disrupt nodes by tier probability; severity ~ U(low, high) capacity loss."""
    fail_prob = fail_prob or {"supplier": 0.10, "plant": 0.05, "dc": 0.05}
    rng = random.Random(seed)
    results = []
    for _ in range(runs):
        d = {}
        for n in net.nodes.values():
            if rng.random() < fail_prob.get(n.tier, 0.0):
                d[n.name] = 1.0 - rng.uniform(*severity)
        results.append(fill_rate(net, d))
    results.sort()
    return {
        "expected_fill_rate": mean(results),
        "p05_fill_rate": results[int(0.05 * len(results))],
        "worst_fill_rate": results[0],
        "prob_full_service": sum(r >= 0.999 for r in results) / len(results),
    }


def resilience_score(net):
    """Simple 0-100 score: 50% avg single-failure fill rate + 50% Monte Carlo expectation."""
    scan = single_failure_scan(net)
    avg_single = mean(r["fill_rate"] for r in scan)
    mc = monte_carlo(net)["expected_fill_rate"]
    return round(100 * (0.5 * avg_single + 0.5 * mc), 1)
