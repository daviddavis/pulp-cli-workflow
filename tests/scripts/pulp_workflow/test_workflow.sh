#!/bin/bash

set -eu

# shellcheck source=tests/scripts/config.source
. "$(dirname "$(dirname "$(realpath "$0")")")/config.source"

WORKFLOW_NAME="test_cli_workflow_$$"
CANCEL_NAME="test_cli_workflow_cancel_$$"
FUTURE_NAME="test_cli_workflow_future_$$"

cleanup() {
  pulp workflow cancel --name "${WORKFLOW_NAME}" 2>/dev/null || true
  pulp workflow cancel --name "${CANCEL_NAME}" 2>/dev/null || true
  pulp workflow cancel --name "${FUTURE_NAME}" 2>/dev/null || true
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

# Test: list with state filter
expect_succ pulp workflow list --state waiting

# Test: label set
expect_succ pulp workflow label set --name "${WORKFLOW_NAME}" --key "env" --value "ci"
expect_succ pulp workflow show --name "${WORKFLOW_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.pulp_labels.env')" = "ci"

# Test: label unset
expect_succ pulp workflow label unset --name "${WORKFLOW_NAME}" --key "env"
expect_succ pulp workflow show --name "${WORKFLOW_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.pulp_labels | has("env")')" = "false"

# Test: cancel a waiting workflow
expect_succ pulp workflow create \
  --name "${CANCEL_NAME}" \
  --task '{"task_name": "pulpcore.app.tasks.base.general_create", "task_args": [], "task_kwargs": []}' \
  --start-time "2099-01-01T00:00:00"
expect_succ pulp workflow cancel --name "${CANCEL_NAME}"
expect_succ pulp workflow show --name "${CANCEL_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.state')" = "canceled"

# Test: canceling an already-canceled workflow should fail
expect_fail pulp workflow cancel --name "${CANCEL_NAME}"

# Test: create with --start-time in the future
FUTURE_NAME="test_cli_workflow_future_$$"
expect_succ pulp workflow create \
  --name "${FUTURE_NAME}" \
  --task '{"task_name": "pulpcore.app.tasks.base.general_create", "task_args": [], "task_kwargs": []}' \
  --start-time "2099-01-01T00:00:00"
expect_succ pulp workflow show --name "${FUTURE_NAME}"
assert "$(echo "$OUTPUT" | jq -r '.state')" = "waiting"

# Clean up the future workflow
expect_succ pulp workflow cancel --name "${FUTURE_NAME}"

# Test: create without required --name should fail
expect_fail pulp workflow create

# Test: show non-existent workflow should fail
expect_fail pulp workflow show --name "nonexistent_workflow_$$"
