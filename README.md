# FOSSA Release Group Management Tool

This tool helps create release groups.

## Installation

Ensure that FOSSA is installed and accessible on your system.

## Setup

1. Obtain a FOSSA API key.
2. Run the tool with the `list` command to verify that FOSSA is accessible and to list existing resources.

## Usage

### Listing resources

To list resources, use the following command:

```bash
python fossa-release-groups.py list --type <resource_type> --fossa-api-key <your_api_key>
```

You can list `projects`, `teams`, `release-groups`, and `policies` which are necessary to understand in your FOSSA organization prior to creating a new Release Group.

### Adding a new release group

To add a new release group, use the following command:

```
python fossa-release-groups.py add --release-group-name <group_name> --release-group-version <version> --fossa-api-key <your_api_key>
```

Optionally, you can specify the IDs of the licensing, security, and quality policies using `--licensing-policy-id`, `--security-policy-id`, and `--quality-policy-id` respectively. You can also specify team IDs using `--teams`.

### Things to note

This checks if an existing release group of the same release group name exists. It'll exit if there exists a release group of the same name. This only creates a new release group. Modifiying existing release groups depends on how you want to structure your data, as it comprises of multiple parts to create the payload.
Please see the original docuemtnation of this here: https://docs.fossa.com/docs/modifying-release-groups

### Support
For more features, please open up an Issue and/or contact chelsea@fossa.com.
