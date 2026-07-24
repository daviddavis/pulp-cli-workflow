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

## Examples

The examples below assume `$REPO_HREF`, `$REPO_PK`, and `$REMOTE_PK` for a
[pulp_file](https://github.com/pulp/pulp_file) repository are already set.

### Run a sync once at a specific time

Use `--start-time` with an ISO 8601 datetime to schedule a single run in the future.
Omit `--dispatch-interval` so the workflow runs exactly once.

```bash
pulp workflow create \
  --name nightly-sync-once \
  --start-time "2026-08-01T02:00:00" \
  --task '{
    "task_name": "pulp_file.app.tasks.synchronizing.synchronize",
    "reserved_resources": ["'"$REPO_HREF"'"],
    "task_kwargs": [
      {"kwarg_key": "repository_pk", "value": "'"$REPO_PK"'"},
      {"kwarg_key": "remote_pk",     "value": "'"$REMOTE_PK"'"},
      {"kwarg_key": "mirror",        "value": false}
    ]
  }'
```

### Run a sync every day

Add `--dispatch-interval '1 00:00:00'` (1 day) to re-run the workflow on a schedule,
creating a new run each interval. Without `--start-time` the first run starts now.

```bash
pulp workflow create \
  --name daily-sync \
  --dispatch-interval '1 00:00:00' \
  --task '{
    "task_name": "pulp_file.app.tasks.synchronizing.synchronize",
    "reserved_resources": ["'"$REPO_HREF"'"],
    "task_kwargs": [
      {"kwarg_key": "repository_pk", "value": "'"$REPO_PK"'"},
      {"kwarg_key": "remote_pk",     "value": "'"$REMOTE_PK"'"},
      {"kwarg_key": "mirror",        "value": false}
    ]
  }'
```

### Run a sync and publish every day

Pass `--task` twice to chain steps. The publish task's `repository_version_pk` is a
dynamic arg (`content_type: core.repositoryversion`) that the workflow engine resolves
at dispatch time from the repository version the sync creates.

```bash
pulp workflow create \
  --name daily-sync-and-publish \
  --dispatch-interval '1 00:00:00' \
  --task '{
    "task_name": "pulp_file.app.tasks.synchronizing.synchronize",
    "reserved_resources": ["'"$REPO_HREF"'"],
    "task_kwargs": [
      {"kwarg_key": "repository_pk", "value": "'"$REPO_PK"'"},
      {"kwarg_key": "remote_pk",     "value": "'"$REMOTE_PK"'"},
      {"kwarg_key": "mirror",        "value": false}
    ]
  }' \
  --task '{
    "task_name": "pulp_file.app.tasks.publish",
    "reserved_resources": ["'"$REPO_HREF"'"],
    "task_kwargs": [
      {"kwarg_key": "manifest", "value": "PULP_MANIFEST"},
      {"kwarg_key": "repository_version_pk", "content_type": "core.repositoryversion"}
    ]
  }'
```

