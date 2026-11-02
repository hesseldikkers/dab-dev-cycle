# Cluster policies

Example policy for classic job clusters. This bundle does not deploy
it: policies belong to the platform team and live in the workspace
bundle (part 2 of the article).

| File | Purpose |
| --- | --- |
| `orders_job_compute.json` | Limits and defaults for `orders` jobs |

The `orders_silver_backfill` job finds its policy by name through the
`job_policy` lookup variable, which uses the built-in `Job Compute`
policy. To use the example policy, create it in the workspace and
change the lookup name in `databricks.yml`. Passing
`--var job_policy=<value>` skips the lookup and sets the policy ID
directly.

The built-in policy has no autoscale defaults, so the job keeps its
`autoscale` block. With the example policy the job could drop it.

The JSON has not been applied in a workspace. The node types are
Azure examples (`Standard_D4ds_v5`, general purpose, 4 vCPU); adjust
them for your cloud and check quota in your region. The job asks for
2 to 4 workers. The policy sets the same defaults and caps autoscale
at 8 workers.
