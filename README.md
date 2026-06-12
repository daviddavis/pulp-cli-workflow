# Pulp CLI Workflow Plugin

A pulp-cli plugin for managing [Pulp workflows](https://github.com/daviddavis/pulp_workflow).

## Usage

```bash
pulp workflow list
pulp workflow show --name <name>
pulp workflow create --name <name> --task '<json>'
pulp workflow cancel --name <name>
pulp workflow label set --name <name> --key <key> --value <value>
```
