"""Thin wrappers around k3d + kubectl. Used only by the heavy-tier driver in CI.

These functions are intentionally narrow: they shell out, check exit codes,
and return strings. The driver composes them; tests at the harness level
don't import this module, so it stays out of the unit-test surface.

References:
- The snapshot artifact is built by `.github/workflows/heavy-tier-snapshot.yaml`
  and contains a tarball of all node images required for the AMP stack.
- AMP-on-k3d operational notes are in MEMORY.md (host.k3d.internal DNS,
  Colima restart crash-loop).
"""
from __future__ import annotations

import subprocess


def restore_snapshot(snapshot_path: str, cluster_name: str = "amp-heavy") -> None:
    """Load the pre-baked image set into the named k3d cluster.

    The cluster must already exist (created from the snapshot workflow's
    saved cluster spec). `k3d cluster import-images` is the supported path
    for restoring an image cache without re-pulling from a registry.
    """
    subprocess.run(
        ["k3d", "cluster", "import-images", "--cluster", cluster_name, snapshot_path],
        check=True,
    )


def wait_ready(timeout_s: int = 300) -> None:
    """Block until the AMP stack's core pods are Ready.

    The set covered is: opensearch (span storage), the observability gateway
    (OTel ingress), agent-manager-service (control plane), and
    traces-observer-service (query API the driver polls). Labels follow the
    Helm chart's standard `app=<name>` convention.
    """
    for selector in (
        "app=opensearch",
        "app=obs-gateway",
        "app=agent-manager-service",
        "app=traces-observer-service",
    ):
        subprocess.run(
            [
                "kubectl",
                "wait",
                "--for=condition=ready",
                "pod",
                "-l",
                selector,
                f"--timeout={timeout_s}s",
            ],
            check=True,
        )


def reset_opensearch_indices() -> None:
    """Delete the spans-* indices so each cell starts from a clean slate."""
    subprocess.run(
        [
            "kubectl",
            "exec",
            "deploy/opensearch",
            "--",
            "curl",
            "-s",
            "-X",
            "DELETE",
            "http://localhost:9200/spans-*",
        ],
        check=False,
    )
