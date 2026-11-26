"""Supply network model: suppliers -> plants -> distribution centers -> markets."""
from dataclasses import dataclass, field

TIERS = ("supplier", "plant", "dc", "market")


@dataclass
class Node:
    name: str
    tier: str
    capacity: float = 0.0   # max throughput (ignored for markets)
    demand: float = 0.0     # only for markets


@dataclass
class Edge:
    src: str
    dst: str
    capacity: float
    lead_time: float = 1.0  # days


@dataclass
class SupplyNetwork:
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)

    def add_node(self, name, tier, capacity=0.0, demand=0.0):
        assert tier in TIERS, f"unknown tier {tier}"
        self.nodes[name] = Node(name, tier, capacity, demand)

    def add_edge(self, src, dst, capacity, lead_time=1.0):
        self.edges.append(Edge(src, dst, capacity, lead_time))

    @property
    def total_demand(self):
        return sum(n.demand for n in self.nodes.values() if n.tier == "market")

    def copy(self):
        net = SupplyNetwork()
        net.nodes = {k: Node(**vars(v)) for k, v in self.nodes.items()}
        net.edges = [Edge(**vars(e)) for e in self.edges]
        return net

    def flow_graph(self, disruptions=None):
        """Build capacity dict for max-flow.

        disruptions: {node_name: remaining_capacity_fraction}  (0.0 = total failure)
        Each node is split into name#in -> name#out to enforce node capacity.
        """
        disruptions = disruptions or {}
        cap = {}
        for n in self.nodes.values():
            frac = disruptions.get(n.name, 1.0)
            if n.tier == "supplier":
                cap[("SOURCE", f"{n.name}#in")] = float("inf")
                cap[(f"{n.name}#in", f"{n.name}#out")] = n.capacity * frac
            elif n.tier == "market":
                cap[(f"{n.name}#in", "SINK")] = n.demand
            else:
                cap[(f"{n.name}#in", f"{n.name}#out")] = n.capacity * frac
        for e in self.edges:
            src_out = f"{e.src}#out"
            dst_in = f"{e.dst}#in"
            cap[(src_out, dst_in)] = cap.get((src_out, dst_in), 0.0) + e.capacity
        return cap


def sample_network():
    """A small illustrative network (units/day)."""
    net = SupplyNetwork()
    for name, c in [("S1", 100), ("S2", 80), ("S3", 60)]:
        net.add_node(name, "supplier", capacity=c)
    for name, c in [("P1", 150), ("P2", 120)]:
        net.add_node(name, "plant", capacity=c)
    for name, c in [("D1", 130), ("D2", 130)]:
        net.add_node(name, "dc", capacity=c)
    for name, d in [("M1", 60), ("M2", 50), ("M3", 70), ("M4", 40)]:
        net.add_node(name, "market", demand=d)

    for s, p, c, lt in [("S1", "P1", 100, 3), ("S2", "P1", 50, 4), ("S2", "P2", 50, 5),
                        ("S3", "P2", 60, 6)]:
        net.add_edge(s, p, c, lt)
    for p, d, c, lt in [("P1", "D1", 100, 2), ("P1", "D2", 50, 3),
                        ("P2", "D1", 50, 3), ("P2", "D2", 80, 2)]:
        net.add_edge(p, d, c, lt)
    for d, m, c, lt in [("D1", "M1", 60, 1), ("D1", "M2", 50, 1), ("D1", "M3", 40, 2),
                        ("D2", "M3", 50, 1), ("D2", "M4", 40, 1), ("D2", "M2", 30, 2)]:
        net.add_edge(d, m, c, lt)
    return net
