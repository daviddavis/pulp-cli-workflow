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
