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
    show_command,
)

from pulp_glue.common.i18n import get_translation
from pulp_glue.workflow.context import PulpWorkflowContext

from pulpcore.cli.workflow.workflow import cancel, create

translation = get_translation(__package__)
_ = translation.gettext

__version__ = "0.0.1.dev0"

lookup_options = [href_option, name_option]
filter_options = [
    click.option("--name"),
    click.option(
        "--state",
        type=click.Choice(
            ["waiting", "skipped", "running", "completed", "failed", "canceled"],
            case_sensitive=False,
        ),
    ),
    label_select_option,
]


@pulp_group(name="workflow")
@pass_pulp_context
@click.pass_context
def workflow_group(ctx: click.Context, pulp_ctx: PulpCLIContext, /) -> None:
    ctx.obj = PulpWorkflowContext(pulp_ctx)


def mount(main: click.Group, **kwargs: t.Any) -> None:
    workflow_group.add_command(list_command(decorators=filter_options))
    workflow_group.add_command(show_command(decorators=lookup_options))
    workflow_group.add_command(label_command(decorators=lookup_options))
    workflow_group.add_command(create)
    workflow_group.add_command(cancel)
    main.add_command(workflow_group)
