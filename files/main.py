"""Run the supply chain resilience analysis on the sample network."""
from scm.network import sample_network
from scm.simulation import fill_rate, monte_carlo, resilience_score, single_failure_scan


def report(title, net):
    print(f"\n=== {title} ===")
    print(f"Total demand: {net.total_demand:.0f} units/day | Baseline fill rate: {fill_rate(net):.1%}")

    print("\nSingle-node failure scan (100% outage):")
    print(f"  {'Node':<6}{'Tier':<10}{'Fill rate':>10}{'Drop':>9}")
    for r in single_failure_scan(net):
        flag = "  <-- high impact" if r["drop"] >= 0.25 else ""
        print(f"  {r['node']:<6}{r['tier']:<10}{r['fill_rate']:>10.1%}{r['drop']:>9.1%}{flag}")

    mc = monte_carlo(net)
    print("\nMonte Carlo (2000 random disruption scenarios):")
    print(f"  Expected fill rate : {mc['expected_fill_rate']:.1%}")
    print(f"  5th percentile     : {mc['p05_fill_rate']:.1%}")
    print(f"  Worst case         : {mc['worst_fill_rate']:.1%}")
    print(f"  P(full service)    : {mc['prob_full_service']:.1%}")
    print(f"\nResilience score: {resilience_score(net)} / 100")


def main():
    base = sample_network()
    report("Baseline network", base)

    # Mitigation: add a backup supplier connected to both plants
    improved = base.copy()
    improved.add_node("S4", "supplier", capacity=70)
    improved.add_edge("S4", "P1", 40, lead_time=7)
    improved.add_edge("S4", "P2", 40, lead_time=7)
    report("With backup supplier S4", improved)

    print(f"\nScore change: {resilience_score(base)} -> {resilience_score(improved)}")


if __name__ == "__main__":
    main()
