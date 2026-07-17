# Pulp CLI Workflow Plugin

A pulp-cli plugin for managing [Pulp workflows](https://github.com/pulp/pulp_workflow).

## Usage

```bash
pulp workflow list
pulp workflow show --name <name>
pulp workflow create --name <name> --task '<json>'
pulp workflow create --name <name> --task '<json>' --dispatch-interval '1 00:00:00'
pulp workflow cancel --name <name>
pulp workflow label set --name <name> --key <key> --value <value>

# Inspect the individual runs (executions) of workflows
pulp workflow run list --workflow <name>
pulp workflow run show --href <href>
pulp workflow run cancel --href <href>
```

A workflow is a definition plus a schedule. Each time its schedule fires, a
`WorkflowRun` records that execution. Set `--dispatch-interval` to re-run a
workflow on a recurring schedule; otherwise it runs once at `--start-time`.
`pulp workflow cancel` stops a workflow (removes its schedule and cancels any
in-flight runs), while `pulp workflow run cancel` cancels a single run.
