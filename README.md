# FOSSA Release Group Management Tool

This tool helps create release groups.

## How this works

When release groups are created in the UI, FOSSA needs at least one project to create a release group. Furthermore, the branch and revision specified must have been scanned. This is important to note due to how the APIs used in this script work. This script runs analysis on a simple python project that has a blank requirements.txt file. This means while the analysis is successful, there are no dependencies to report. This project then gets added to a release group version. From here, the `list` command can be used to verify that the release group has been created. To automatically add legitimate projects to a release group, you can use the release group flags from the `fossa analyze` command:

```
fossa analyze --help | grep release
[--project-label ARG] [--release-group-name ARG --release-group-release ARG] [--only-target PATH] [--exclude-target PATH]
  --release-group-name ARG
      The name of the release group to add this project to
  --release-group-release ARG
      The release of the release group to add this project to
```

## Installation

Ensure that FOSSA is installed and accessible on your system.

## Setup

1. Obtain a FOSSA API key.
2. Run the tool with the `list` command to verify that FOSSA is accessible and to list existing resources.
3. Run `chmod +x fossa-release-groups.py`

## Usage

### Listing resources

To list resources, use the following command:

```bash
python fossa-release-groups.py list --type <resource_type> --fossa-api-key <your_api_key>
```

You can list `projects`, `teams`, `release-groups`, and `policies` which are necessary to understand in your FOSSA organization prior to creating a new Release Group.

### Create a new release group

To add a new release group, use the following command:

```
python fossa-release-groups.py add --release-group-name <group_name> --release-group-version <version> --fossa-api-key <your_api_key>
```

Optionally, you can specify the IDs of the licensing, security, and quality policies using `--licensing-policy-id`, `--security-policy-id`, and `--quality-policy-id` respectively. You can also specify team IDs using `--teams`.

### Add a new version to a release group

Similar to creating a new release, use the same flags, and there will be logic to check if the specified release group version exists or not. If it doesn't exist, then the new release group version will be created. This will also check if the test project exists in your org; if it doesn't then the script will create and scan project, then add it to the new release group version.

### Things to note

This checks if an existing release group of the same release group name and version exists. It'll exit if there exists a release group and version of the same name. This only creates the first version of a release group, as well as adding new versions. Modifiying existing release groups with additional projects (or the same projects) depends on how you want to structure your data, as it comprises of multiple parts to create the payload.
Please see the original documentation of this here: https://docs.fossa.com/docs/modifying-release-groups

### Support
For more features, please open up an Issue and/or contact chelsea@fossa.com.
