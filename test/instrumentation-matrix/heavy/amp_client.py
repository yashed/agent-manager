"""Thin client for agent-manager-service REST API — used by the heavy-tier
driver to provision an agent per cell against the snapshot cluster.

This module is a scaffold. The full client mirrors what
`test/e2e/framework/shared_agent.go` does in Go: create project, create agent
(with the right instrumentation_version), trigger build, poll until ready,
collect the endpoint URL + API key. Implementing the full flow in Python is
deferred — Phase 7 commits the structure; Phase 8 fills in bodies once a
heavy-tier snapshot exists to validate against.

Cross-reference for the Go reference flow:
- `test/e2e/framework/shared_agent.go` — SharedAgent struct + provisioning
- `test/e2e/operations/agent/*.go` — per-step calls
- `agent-manager-service/instrumentation/baseline.json` — the catalog of
  instrumentation versions the server accepts on build requests
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DeployedAgent:
    project_name: str
    agent_name: str
    endpoint_url: str
    api_key: str

    # Observer query keys. The observer's GET /api/v1/traces requires
    # (namespace, project, component, environment, startTime, endTime).
    # The driver records these at deploy time so observer.poll_traces can
    # form a valid query without re-discovering them.
    namespace: str
    component: str
    environment: str


class AmpClient:
    """REST client. Initialised with an API base URL + admin token.

    `base_url` is the in-cluster URL of agent-manager-service (resolved by
    the heavy-tier workflow to the cluster service DNS), and `admin_token`
    is minted by the snapshot bootstrap step. Both are passed in as env
    vars (`AMP_API_BASE_URL`, `AMP_ADMIN_TOKEN`); see HEAVY-TIER-DEPLOY.md.
    """

    def __init__(self, base_url: str, admin_token: str):
        self.base_url = base_url.rstrip("/")
        self.admin_token = admin_token

    def deploy_agent(
        self,
        *,
        cell_id: str,
        instrumentation_version: str,
        framework_package: str,
        framework_version: str,
        python_version: str,
    ) -> DeployedAgent:
        """Create a project + agent + build with the cell's pins; return the
        endpoint URL and API key.

        The build request carries the matrix cell's pinned versions:
        - `instrumentation_version` → controls which init-container image
          ships traceloop_version.
        - `framework_package==framework_version` → patched into the agent's
          requirements.txt before build.
        - `python_version` → picks the Python base image for the build.

        Returns once the build reports `Ready`. Raises on timeout.
        """
        raise NotImplementedError(
            "Heavy-tier deploy is a scaffold. See HEAVY-TIER-DEPLOY.md and "
            "test/e2e/framework/shared_agent.go for the REST-API flow this "
            "needs to implement (Phase 8)."
        )

    def teardown_agent(self, deployed: DeployedAgent) -> None:
        """Delete the agent + project. Called from a finally block per cell."""
        raise NotImplementedError(
            "Heavy-tier teardown — see HEAVY-TIER-DEPLOY.md (Phase 8)."
        )
