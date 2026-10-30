# Elpis terminal-failure recovery reference

Historical implementation installed on 30 October 2026, published on 31 October.
This copy comes from the original production-source snapshot preserved during
31 October stage-3 preparation, not the modified, undeployed stage-3 watchdog.
The only publication changes are importing `os` and replacing the private recipe
directory with the required `LLMRIG_RECIPE_DIR` environment variable.

This is a Linux/systemd/Docker integration reference, not a standalone installer.
It expects the existing router, its telemetry contract, two named lane containers,
and the same shared GPU ownership lock used by every competing workload.

Required private `router.json` fields are `api_key_file`, `media_lock`, and the
ordered two-element `ports` array; `port` defaults to 11446. Set
`LLMRIG_RECIPE_DIR` to the directory containing that private configuration.
The API key stays in a separate local file. No real configuration or key is shipped.
The persistent attempt history is stored below the operator's local state directory.

The monitor polls every ten seconds and requires three observations of the exact
sticky native failure. Healthy/busy lanes, active GPU ownership, maintenance stops,
and unknown/transient errors do not authorize a restart. It rechecks under the
shared lock, persists its attempt budget before restarting only the failed lane,
and holds the lock until readiness or the bounded recovery wait expires. The limit
is three attempts per lane per hour with at least five minutes between attempts.
It never replays a generation request. This is not OOM prevention or a guarantee
of full-context or arbitrary concurrency safety.

The original 30 October report records 11 passing mocked tests. Publication checks
parse this sanitized source and verify that its only differences from the retained
snapshot are the directory substitution and import. The historical 11-test suite
was not rerun for this publication; no live Docker/systemd or GPU work was run.

See [the dated results](../../docs/elpis-operations-2026-10-30.md).
