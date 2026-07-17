#!/bin/bash

set -eu

# shellcheck source=tests/scripts/config.source
. "$(dirname "$(dirname "$(realpath "$0")")")/config.source"

WORKFLOW_NAME="test_cli_workflow_$$"
CANCEL_NAME="test_cli_workflow_cancel_$$"
FUTURE_NAME="test_cli_workflow_future_$$"
PERIODIC_NAME="test_cli_workflow_periodic_$$"

cleanup() {
  pulp workflow cancel --name "${WORKFLOW_NAME}" 2>/dev/null || true
  pulp workflow cancel --name "${CANCEL_NAME}" 2>/dev/null || true
  pulp workflow cancel --name "${FUTURE_NAME}" 2>/dev/null || true
  pulp workflow cancel --name "${PERIODIC_NAME}" 2>/dev/null || true
}
trap cleanup EXIT

# Test: list workflows (should succeed even if empty)
expect_succ pulp workflow list
assert "$OUTPUT" != "null"

# Test: create a minimal workflow
expect_succ pulp workflow create \
  --name "${WORKFLOW_NAME}" \
  --task '{"task_name": "pulpcore.app.tasks.base.general_create", "task_args": [], "task_kwargs": []}' \
  --label "test_key=test_value"
assert "$OUTPUT" != ""

# Test: show the created workflow
expect_succ pulp workflow show --name "${WORKFLOW_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.name')" = "${WORKFLOW_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.pulp_labels.test_key')" = "test_value"

# Test: list with name filter returns our workflow
expect_succ pulp workflow list --name "${WORKFLOW_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.[0].name')" = "${WORKFLOW_NAME}"

# Test: label set
expect_succ pulp workflow label set --name "${WORKFLOW_NAME}" --key "env" --value "ci"
expect_succ pulp workflow show --name "${WORKFLOW_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.pulp_labels.env')" = "ci"

# Test: label unset
expect_succ pulp workflow label unset --name "${WORKFLOW_NAME}" --key "env"
expect_succ pulp workflow show --name "${WORKFLOW_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.pulp_labels | has("env")')" = "false"

# Test: list the runs of a workflow (may be empty, but must be valid JSON)
expect_succ pulp workflow run list --workflow "${WORKFLOW_NAME}"
assert "$OUTPUT" != "null"

# Test: create a periodic workflow with --dispatch-interval
expect_succ pulp workflow create \
  --name "${PERIODIC_NAME}" \
  --dispatch-interval "01:00:00" \
  --task '{"task_name": "pulpcore.app.tasks.base.general_create", "task_args": [], "task_kwargs": []}'
expect_succ pulp workflow show --name "${PERIODIC_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.name')" = "${PERIODIC_NAME}"

# Test: inspect an individual run via its (nested) href. A periodic workflow starts at
# start-time (now), so the scheduler creates a run shortly after creation; poll briefly.
RUN_HREF=""
for _ in $(seq 1 10); do
  expect_succ pulp workflow run list --workflow "${PERIODIC_NAME}"
  RUN_HREF="$(echo "$OUTPUT" | jq -r '.[0].pulp_href // empty')"
  [ -n "${RUN_HREF}" ] && break
  sleep 1
done
if [ -n "${RUN_HREF}" ]; then
  # 'run show' must resolve the nested run href against the correct read operation.
  expect_succ pulp workflow run show --href "${RUN_HREF}"
  assert "$(echo "$OUTPUT" | jq -r '.pulp_href')" = "${RUN_HREF}"
fi

# Stopping a periodic workflow halts its schedule.
expect_succ pulp workflow cancel --name "${PERIODIC_NAME}"

# Test: stop a workflow scheduled in the future
expect_succ pulp workflow create \
  --name "${CANCEL_NAME}" \
  --task '{"task_name": "pulpcore.app.tasks.base.general_create", "task_args": [], "task_kwargs": []}' \
  --start-time "2099-01-01T00:00:00"
expect_succ pulp workflow cancel --name "${CANCEL_NAME}"
# Stopping is idempotent: a second stop still succeeds.
expect_succ pulp workflow cancel --name "${CANCEL_NAME}"
# The workflow definition is still readable after being stopped.
expect_succ pulp workflow show --name "${CANCEL_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.name')" = "${CANCEL_NAME}"

# Test: create with --start-time in the future
FUTURE_NAME="test_cli_workflow_future_$$"
expect_succ pulp workflow create \
  --name "${FUTURE_NAME}" \
  --task '{"task_name": "pulpcore.app.tasks.base.general_create", "task_args": [], "task_kwargs": []}' \
  --start-time "2099-01-01T00:00:00"
expect_succ pulp workflow show --name "${FUTURE_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.name')" = "${FUTURE_NAME}"

# Clean up the future workflow
expect_succ pulp workflow cancel --name "${FUTURE_NAME}"

# Test: create without required --name should fail
expect_fail pulp workflow create

# Test: show non-existent workflow should fail
expect_fail pulp workflow show --name "nonexistent_workflow_$$"
