import json
import typing as t
from datetime import datetime

import click
from pulp_cli.generic import (
    PulpCLIContext,
    href_option,
    name_option,
    pass_entity_context,
    pass_pulp_context,
    pulp_command,
)

from pulp_glue.common.context import DATETIME_FORMATS, PulpEntityContext
from pulp_glue.common.i18n import get_translation
from pulp_glue.workflow.context import PulpWorkflowContext, PulpWorkflowRunContext

translation = get_translation(__name__)
_ = translation.gettext


@pulp_command()
@click.option("--name", required=True)
@click.option(
    "--start-time",
    "start_time",
    default=None,
    type=click.DateTime(formats=DATETIME_FORMATS),
    help=_("ISO 8601 datetime for when the workflow should first run. Defaults to now."),
)
@click.option(
    "--dispatch-interval",
    "dispatch_interval",
    default=None,
    type=click.STRING,
    help=_(
        "If set, the interval on which the workflow re-runs, creating a new run each time "
        "(e.g. '1 00:00:00' for daily or '01:00:00' for hourly). If omitted, the workflow "
        "runs exactly once at start-time."
    ),
)
@click.option(
    "--task",
    "tasks",
    multiple=True,
    type=click.STRING,
    help=_(
        "JSON object describing a workflow task. Can be specified multiple times. "
        "Each object should have 'task_name' and optionally 'task_args', 'task_kwargs', "
        "and 'reserved_resources'."
    ),
)
@click.option(
    "--label",
    "pulp_labels",
    multiple=True,
    type=click.STRING,
    help=_("Label in the form key=value. Can be specified multiple times."),
)
@pass_entity_context
@pass_pulp_context
def create(
    pulp_ctx: PulpCLIContext,
    entity_ctx: PulpEntityContext,
    /,
    name: str,
    start_time: t.Optional[datetime],
    dispatch_interval: t.Optional[str],
    tasks: tuple[str, ...],
    pulp_labels: tuple[str, ...],
) -> None:
    """Create a workflow."""
    assert isinstance(entity_ctx, PulpWorkflowContext)

    body: dict[str, t.Any] = {"name": name}

    if start_time is not None:
        body["start_time"] = start_time

    if dispatch_interval is not None:
        body["dispatch_interval"] = dispatch_interval

    if tasks:
        parsed_tasks = []
        for task_json in tasks:
            try:
                parsed_tasks.append(json.loads(task_json))
            except json.JSONDecodeError as e:
                raise click.ClickException(_("Invalid JSON for --task: {err}").format(err=str(e)))
        body["tasks"] = parsed_tasks

    if pulp_labels:
        labels: dict[str, str] = {}
        for label in pulp_labels:
            if "=" not in label:
                raise click.ClickException(
                    _("Label must be in the form key=value, got: {label}").format(label=label)
                )
            key, value = label.split("=", 1)
            labels[key] = value
        body["pulp_labels"] = labels

    result = entity_ctx.create(body=body)
    pulp_ctx.output_result(result)


@pulp_command()
@name_option
@href_option
@pass_entity_context
@pass_pulp_context
def cancel(
    pulp_ctx: PulpCLIContext,
    entity_ctx: PulpEntityContext,
    /,
) -> None:
    """Stop a workflow.

    Removes the workflow's schedule so no further runs are created and cancels any of its
    runs that are still in progress. This is idempotent.
    """
    assert isinstance(entity_ctx, PulpWorkflowContext)

    result = entity_ctx.cancel()
    pulp_ctx.output_result(result)


@pulp_command(name="cancel")
@href_option
@pass_entity_context
@pass_pulp_context
def run_cancel(
    pulp_ctx: PulpCLIContext,
    entity_ctx: PulpEntityContext,
    /,
) -> None:
    """Cancel a waiting or running workflow run."""
    assert isinstance(entity_ctx, PulpWorkflowRunContext)

    entity = entity_ctx.entity
    if entity["state"] not in ("waiting", "running"):
        raise click.ClickException(
            _("Workflow run '{href}' is in state '{state}' and cannot be canceled.").format(
                href=entity["pulp_href"], state=entity["state"]
            )
        )
    result = entity_ctx.cancel()
    pulp_ctx.output_result(result)
