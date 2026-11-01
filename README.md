# dab-dev-cycle

Example Declarative Automation Bundle with a medallion architecture:

- **bronze**: Auto Loader ingest from a Unity Catalog volume (cron)
- **silver**: standardize and deduplicate (table update trigger)
- **gold**: SQL mart on top of silver (table update trigger)

Companion repository for an article on setting up a bundle that grows
with your team and closes the dev cycle.

## Prerequisites

- Databricks CLI 1.23.0
- [uv](https://docs.astral.sh/uv/)
- Java 17 for the local Spark tests
- Per target: schema `orders_<env>` in catalog `workspace` with the
  volumes `landing` (raw JSON in `sales_orders/`) and `checkpoints`

## Commands

```bash
uv sync
uv run pytest
databricks bundle validate --strict -t dev
databricks bundle plan -t dev
```
