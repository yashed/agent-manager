# CrewAI Agent Sample

A buildpack-deployable chat agent built on [CrewAI](https://github.com/crewAIInc/crewAI),
exposing `POST /chat` via FastAPI. A researcher agent (with a capital-lookup
tool) and an editor agent run two sequential tasks, so each request emits
`llm`, `agent`, and `crewaitask` spans.

This sample exists so the instrumentation-matrix **heavy tier** can deploy a
real CrewAI app and validate CrewAI auto-instrumentation through the full
pipeline (auto-instrumentation → gateway → collector → OpenSearch → observer).
See `test/instrumentation-matrix/RUNBOOK.md` §7.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python main.py    # serves on http://localhost:8000
```

```bash
curl -s localhost:8000/chat \
  -H 'content-type: application/json' \
  -d '{"session_id": "s1", "message": "What is the capital of France?"}'
```

## Notes

- Pinned to `crewai==1.1.0` (1.14 is unresolvable against the matrix's
  `traceloop-sdk 0.60`; see `test/instrumentation-matrix/FINDINGS.md` F-004).
- The app sets `CREWAI_TRACING_ENABLED=false`,
  `CREWAI_DISABLE_TRACING_PROMPT=true`, and `LITELLM_LOCAL_MODEL_COST_MAP=True`
  so it runs non-interactively and avoids cold-start network fetches.
