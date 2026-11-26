# Supply Chain Resilience (base project)

Models a multi-tier supply network (suppliers -> plants -> DCs -> markets) and measures how well it
keeps serving demand when nodes are disrupted.

## What it does
- **Max-flow fill rate**: how much demand can still be met given node/edge capacities.
- **Single-point-of-failure scan**: fails each node and ranks by impact.
- **Monte Carlo**: random disruptions by tier -> expected / 5th-percentile / worst fill rate.
- **Resilience score (0-100)** and a **what-if mitigation** (backup supplier).

## Run
    python main.py
    python -m unittest discover tests

## Structure
    scm/maxflow.py      Edmonds-Karp max flow
    scm/network.py      Node/Edge/SupplyNetwork + sample network
    scm/simulation.py   fill rate, failure scan, Monte Carlo, score
    main.py             report + mitigation comparison

## Extend
Load your own network from CSV, add edge disruptions, inventory buffers, cost/lead-time
objectives, or plot results with matplotlib.
