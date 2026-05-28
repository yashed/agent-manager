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

Two axes *do* change what gets deployed, so the subset crosses both:

1. **instrumentation/Traceloop version** — pins the init-container image.
2. **python version** — the buildpack builds (and the instrumentation runs)
   the agent on that interpreter, so a py-version-specific break surfaces
   through the deployed pipeline.

So the subset is one cell per (Traceloop version × python), on the default
framework + framework_version — the representative agent re-validated against
each init-container version and each python. (Unlike the framework axis,
varying python deploys a genuinely different agent build.)
"""
from __future__ import annotations

from harness.manifest import Cell, Manifest


def select_heavy_subset(cells: list[Cell], manifest: Manifest) -> list[Cell]:
    default = manifest.default_cell

    # One cell per (Traceloop/provider version × python), pinned to the default
    # framework + framework_version. The framework is fixed to the default
    # (which matches the deployed sample), so the cell's label reflects what
    # actually runs; the provider version and python are the two axes that
    # change the deployed agent (init-container image, buildpack interpreter).
    out: list[Cell] = []
    seen: set[str] = set()
    for c in cells:
        if (
            c.provider_name == default.provider
            and c.framework_name == default.framework
            and c.framework_version == default.framework_version
            and c.id not in seen
        ):
            seen.add(c.id)
            out.append(c)
    return out
