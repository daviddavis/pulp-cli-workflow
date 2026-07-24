import typing as t

import click
from pulp_cli.generic import (
    PulpCLIContext,
    href_option,
    label_command,
    label_select_option,
    list_command,
    name_option,
    pass_pulp_context,
    pulp_group,
    resource_option,
    show_command,
)

from pulp_glue.common.i18n import get_translation
from pulp_glue.workflow.context import PulpWorkflowContext, PulpWorkflowRunContext

from pulpcore.cli.workflow.workflow import cancel, create, run_cancel

translation = get_translation(__package__)
_ = translation.gettext

__version__ = "0.2.0.dev"

lookup_options = [href_option, name_option]
filter_options = [
    click.option("--name"),
    label_select_option,
]

state_choice = click.Choice(
    ["waiting", "skipped", "running", "completed", "failed", "canceled"],
    case_sensitive=False,
)

workflow_option = resource_option(
    "--workflow",
    default_plugin="workflow",
    default_type="workflow",
    context_table={"workflow:workflow": PulpWorkflowContext},
    href_pattern=PulpWorkflowContext.HREF_PATTERN,
    help=_("Workflow to filter runs by, in the form <name> or by href."),
)
run_filter_options = [
    workflow_option,
    click.option("--state", type=state_choice),
]
run_lookup_options = [href_option]


@pulp_group(name="workflow")
@pass_pulp_context
@click.pass_context
def workflow_group(ctx: click.Context, pulp_ctx: PulpCLIContext, /) -> None:
    ctx.obj = PulpWorkflowContext(pulp_ctx)


@pulp_group(name="run")
@pass_pulp_context
@click.pass_context
def run_group(ctx: click.Context, pulp_ctx: PulpCLIContext, /) -> None:
    ctx.obj = PulpWorkflowRunContext(pulp_ctx)


run_group.add_command(list_command(decorators=run_filter_options))
run_group.add_command(show_command(decorators=run_lookup_options))
run_group.add_command(run_cancel)


def mount(main: click.Group, **kwargs: t.Any) -> None:
    workflow_group.add_command(list_command(decorators=filter_options))
    workflow_group.add_command(show_command(decorators=lookup_options))
    workflow_group.add_command(label_command(decorators=lookup_options))
    workflow_group.add_command(create)
    workflow_group.add_command(cancel)
    workflow_group.add_command(run_group)
    main.add_command(workflow_group)
