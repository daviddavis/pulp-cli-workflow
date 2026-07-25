# Changelog

[//]: # (You should *NOT* be adding new change log entries to this file, this)
[//]: # (file is managed by towncrier. You *may* edit previous change logs to)
[//]: # (fix problems like typo corrections or such.)
[//]: # (To add a new change log entry, please see)
[//]: # (https://docs.pulpproject.org/contributing/git.html#changelog-update)

[//]: # (WARNING: Don't drop the towncrier directive!)

[//]: # (towncrier release notes start)

## 0.1.0 (2026-07-24) {: #0.1.0 }



#### Features {: #0.1.0-feature }

- Added `pulp workflow create --dispatch-interval` to schedule a workflow to re-run on a recurring
  interval, and a new `pulp workflow run` command group (`list`, `show`, `cancel`) to inspect and
  cancel the individual runs of a workflow. `pulp workflow cancel` now stops a workflow by removing
  its schedule and canceling any in-flight runs.


### Pulp-workflow GLUE {: #0.1.0-pulp-workflow-glue }


#### Features {: #0.1.0-pulp-workflow-glue-feature }

- Added `PulpWorkflowRunContext` for the new `workflow-runs` resource and a `dispatch_interval` field
  on workflow creation to support periodic (recurring) workflows.


---

## 0.0.1 (2026-07-17) {: #0.0.1 }



No significant changes.


### Pulp-workflow GLUE {: #0.0.1-pulp-workflow-glue }


No significant changes.


---
