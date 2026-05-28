"""Pick a representative subset of cells for the heavy tier.

The heavy tier is expensive — every cell deploys a real agent against a k3d
snapshot, hits the API, polls the observer. So we run a sample, not the full
matrix.

**Heavy is a pipeline test, not a per-framework test.** It deploys one
representative agent (`samples/customer-support-agent`, a LangChain/LangGraph
app) and asks: *do its spans survive the full deployed path —
auto-instrumentation → gateway → collector → OpenSearch → traces-observer —
and arrive well-formed?* That path is framework-agnostic, so a single agent
proves it. Per-framework span *shape* is the emission tier's job (it runs each
`cells/<framework>_sample.py` in-process), so heavy does NOT vary the framework
or assert framework-specific span kinds — doing so would only be meaningful
with a deployable agent per framework, which we don't have yet (see
FINDINGS / RUNBOOK §7).

The one axis that *does* change what gets deployed is the
**instrumentation/Traceloop version** (it pins the init-container). So the
subset is one cell per Traceloop version, on the default framework + python —
i.e. the representative agent re-validated against each init-container version.
"""
from __future__ import annotations

from harness.manifest import Cell, Manifest


def select_heavy_subset(cells: list[Cell], manifest: Manifest) -> list[Cell]:
    default = manifest.default_cell

    # One cell per Traceloop/provider version, pinned to the default framework
    # + framework_version + python. Each maps to a distinct init-container
    # (instrumentation) version — the only axis that changes the deployed
    # agent. The framework is fixed to the default (which matches the deployed
    # sample), so the cell's label reflects what actually runs.
    per_version: list[Cell] = []
    seen: set[str] = set()
    for c in cells:
        if (
            c.provider_name == default.provider
            and c.framework_name == default.framework
            and c.framework_version == default.framework_version
            and c.python == default.python
            and c.id not in seen
        ):
            seen.add(c.id)
            per_version.append(c)
    return per_version
