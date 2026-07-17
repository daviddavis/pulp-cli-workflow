import typing as t

from pulp_glue.common.context import (
    EntityDefinition,
    PluginRequirement,
    PulpEntityContext,
)
from pulp_glue.common.i18n import get_translation

translation = get_translation(__package__)
_ = translation.gettext


class PulpWorkflowContext(PulpEntityContext):
    ENTITY = _("workflow")
    ENTITIES = _("workflows")
    HREF = "workflow_workflow_href"
    HREF_PATTERN = r"workflow/workflows/[^/]+/"
    ID_PREFIX = "workflow_workflows"
    NEEDS_PLUGINS = [PluginRequirement("workflow")]
    NULLABLES: t.ClassVar[set[str]] = set()

    CANCEL_ID = "workflows_cancel"

    def cancel(self) -> t.Any:
        return self.call(
            "cancel",
            parameters={self.HREF: self.pulp_href},
            body={"state": "canceled"},
        )

    def preprocess_entity(self, body: EntityDefinition, partial: bool = False) -> EntityDefinition:
        body = super().preprocess_entity(body, partial=partial)
        return body


class PulpWorkflowRunContext(PulpEntityContext):
    ENTITY = _("workflow run")
    ENTITIES = _("workflow runs")
    # Runs are canonically served from the nested route
    # (/workflow/workflows/<workflow_pk>/runs/<pk>/), which is what a run's pulp_href points to
    # and where retrieve/cancel live. ID_PREFIX and HREF therefore follow the nested viewset.
    HREF = "workflow_workflows_workflow_run_href"
    HREF_PATTERN = r"workflow/workflows/[^/]+/runs/[^/]+/"
    ID_PREFIX = "workflow_workflows_runs"
    # Listing uses the flat, list-only collection (/workflow/workflow-runs/) so runs can be
    # scoped across workflows via the `workflow` query filter rather than a path parameter.
    LIST_ID = "workflow_workflow_runs_list"
    NEEDS_PLUGINS = [PluginRequirement("workflow")]
    NULLABLES: t.ClassVar[set[str]] = set()

    CANCEL_ID = "workflow_runs_cancel"

    def cancel(self) -> t.Any:
        return self.call(
            "cancel",
            parameters={self.HREF: self.pulp_href},
            body={"state": "canceled"},
        )
