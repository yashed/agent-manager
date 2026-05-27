"""Trace-observer query helpers for the heavy-tier driver.

`GET /api/v1/traces` requires `(namespace, project, component, environment,
startTime, endTime)` — these are recorded on DeployedAgent at deploy time so
the driver can form a valid query without re-discovering them.

Plan note: the plan's `_poll_traces` used `?agent=<id>&limit=50` which is
not the real query shape (verified against
`traces-observer-service/handlers/handlers.go` and corresponding tests).
This module fixes that, but the actual implementation is deferred to
Phase 8 — there's no live observer to point at until the snapshot workflow
publishes its first artifact.
"""
from __future__ import annotations

from heavy.amp_client import DeployedAgent


def poll_traces(deployed: DeployedAgent, timeout_s: int = 120) -> list[dict]:
    """Block until the observer has spans for the deployed agent's component,
    then return them as a flat list of span dicts (`name`, `kind`,
    `attributes`, `traceId`, `spanId`, `parentSpanId`, `resource`).

    The polling window starts at deploy time and ends at `now + timeout_s`,
    which is the same shape the e2e tests use. Empty result after timeout =
    "no spans captured" — driver maps that to FailureCategory.NO_SPANS_CAPTURED.
    """
    raise NotImplementedError(
        "Heavy-tier observer poll is a scaffold. The query shape is "
        "(namespace, project, component, environment, startTime, endTime); "
        "see traces-observer-service/handlers/handlers.go and "
        "test/e2e/operations/trace/list_traces.go for the call pattern (Phase 8)."
    )
