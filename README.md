# dab-dev-cycle

Example Declarative Automation Bundle (`orders`) with a medallion
architecture and four jobs. Companion repository for an article on
setting up a bundle that grows with your team and closes the dev
cycle.

| Job | What it does | Starts on |
| --- | --- | --- |
| `orders_bronze` | Auto Loader ingest from a volume | cron, daily 06:00 |
| `orders_silver` | Standardize types, keep latest order version | update of `orders_bronze` |
| `orders_gold` | SQL mart `orders_daily` | update of `orders_silver` |
| `orders_silver_backfill` | Silver on a classic job cluster | manual only |

`orders_silver_backfill` needs classic compute and does not run on
Databricks Free Edition. Its cluster settings come from a cluster
policy; see `platform/cluster_policies/`.

## Prerequisites

- Databricks CLI 1.23.0
- [uv](https://docs.astral.sh/uv/)
- Java 17 for the local Spark tests
- Per target: schema `orders_<env>` in catalog `workspace`, with the
  volumes `landing` (raw JSON in `sales_orders/`) and `checkpoints`

## Quick start

```bash
uv sync
uv run pytest
databricks bundle validate --strict -t dev -p <profile>
databricks bundle plan -t dev -p <profile>
```

## Project structure

```
databricks.yml          # bundle, variables, targets
resources/              # <name>.<type>.yml, one file per resource
mutators.py             # deploy-time standards (Python mutators)
src/orders/             # all logic; tasks only call it
tests/                  # pytest unit tests
platform/               # examples managed outside this bundle
```

## Targets

| Target | Mode | Schema | Runs as | Deployed by |
| --- | --- | --- | --- | --- |
| `dev` | development | `orders_dev` | you | you |
| `acc` | production | `orders_acc` | deploy principal | pipeline |
| `prd` | production | `orders_prd` | run-as principal | pipeline, `main` only |

Principals and groups are placeholders (`<deploy-sp-id>`,
`<run-as-sp-id>`, `<data-engineers>`). The pipeline sets the real
values.

The bundle has no `workspace.host`. Locally pass `-p <profile>`; in
CI set `DATABRICKS_HOST`. The CLI fails when a profile host differs
from a host set in the YAML, and `workspace.host` does not accept
variables.

## Common tasks

| Task | Command |
| --- | --- |
| Unit tests | `JAVA_HOME=$(brew --prefix openjdk@17) uv run pytest` |
| Lint | `uv run ruff check . && uv run ruff format --check .` |
| Validate | `databricks bundle validate --strict -t <target>` |
| Preview changes | `databricks bundle plan -t <target>` |

## Troubleshooting

- **Triggers do not fire in `dev`.** Development mode pauses
  schedules and triggers. Run the jobs by hand, in order.
- **Nothing downstream runs on a new target.** The silver and gold
  triggers watch tables that the earlier jobs create. Run bronze
  first.
- **`validate -t acc` fails on the root path.** The path belongs to
  the deploy principal. Locally pass
  `--var deploy_sp=<your-user-name>`.
