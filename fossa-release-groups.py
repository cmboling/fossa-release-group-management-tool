import subprocess
import os
import requests
import argparse

FOSSA_API_BASE_URL = "https://app.fossa.com/api"

def check_fossa_existence():
    try:
        output = subprocess.check_output(["fossa", "--version"], stderr=subprocess.STDOUT)
        print("FOSSA exists.")
        return True
    except subprocess.CalledProcessError as e:
        print("Error: FOSSA is not installed or accessible.")
        return False

def create_test_directory():
    os.makedirs("test-project-for-release-group-creation", exist_ok=True)

def create_blank_requirements_file():
    with open("test-project-for-release-group-creation/requirements.txt", "w") as f:
        pass

def run_fossa_analyze(api_key):
    os.chdir("test-project-for-release-group-creation")
    subprocess.run(["fossa", "analyze", "--title", "test-project-for-release-group-creation", "--revision", "test-revision", "--branch", "test-branch", "--fossa-api-key", api_key])

def run_fossa_test(api_key):
    subprocess.run(["fossa", "test", "--fossa-api-key", api_key])

def list_projects(api_key, suppress_output=False):
    url = f"{FOSSA_API_BASE_URL}/projects"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = sorted(response.json(), key=lambda x: x['title'])
        if not suppress_output:
            print("List of projects:")
            print("{:<40} {:<20}".format("Project Name", "Project Locator"))
            for project in projects:
                print("{:<40} {:<20}".format(project['title'], project['locator']))
        return projects
    else:
        print(f"Failed to list projects: {response.text}")
        return []


def list_teams(api_key):
    url = f"{FOSSA_API_BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        teams = sorted(response.json(), key=lambda x: x['name'])
        print("List of teams:")
        print("{:<40} {:<20}".format("Team Name", "Team ID"))
        for team in teams:
            print("{:<40} {:<20}".format(team['name'], team['id']))
    else:
        print(f"Failed to list teams: {response.text}")

def list_policies(api_key):
    url = f"{FOSSA_API_BASE_URL}/policies"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        policies = sorted(response.json(), key=lambda x: x['title'])
        print("List of policies:")
        print("{:<40} {:<20}".format("Policy Name", "Policy ID"))
        for policy in policies:
            print("{:<40} {:<20}".format(policy['title'], policy['id']))
    else:
        print(f"Failed to list policies: {response.text}")

def list_release_groups(api_key, list_release_projects=False):
    page = 1
    count = 20
    sort = "latest-scan_desc"
    url = f"{FOSSA_API_BASE_URL}/v2/release-groups?count={count}&sort={sort}"

    headers = {"Authorization": f"Bearer {api_key}"}
    release_groups_list = []
    print("List of release groups:")
    print("{:<40} {:<20}".format("Release group name", "Release group ID"))
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data["releaseGroups"]:
                print("No release groups found.")
                break

            if "releaseGroups" in data:
                release_groups = data["releaseGroups"]
                for group in release_groups:
                    release_group_info = {"name": group['title'], "id": group['id'], "projects": group["projects"]}
                    release_groups_list.append(release_group_info)
                    print("{:<40} {:<20}".format(group['title'], group['id']))

                    # Fetch and print details of releases for this release group
                    release_details = fetch_release_details(api_key, group['id'], list_release_projects)
                    release_groups_list[-1]["releases"] = release_details  # Add releases to the last item in the list

                    print("Release details:")
                    for release in release_details:
                        print(f"\t Release ID: {release['id']}")
                        print(f"\t Release Title: {release['title']}")

                        if list_release_projects:
                            for project in release["projects"]:
                                print(f"\t\t\t Project Id: {project['projectId']}")
                                print(f"\t\t\t Project Branch: {project['branch']}")
                                print(f"\t\t\t Project Revision: {project['revisionId']}\n")
                    print("-----------------")

            else:
                print("No release groups found.")
                break

            count_fetched = len(release_groups)
            total_groups = data.get("total", 0)
            if count_fetched < count or count_fetched == total_groups:
                break  # All groups fetched or no more groups left
            else:
                page += 1
                url = f"{FOSSA_API_BASE_URL}/v2/release-groups?page={page}&count={count}&sort={sort}"
        else:
            print(f"Failed to list release groups: {response.text}")
            break
    print(release_groups_list)
    return release_groups_list

def fetch_release_details(api_key, release_group_id, list_release_projects=False):
    url = f"{FOSSA_API_BASE_URL}/project_group/{release_group_id}"

    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        releases = data.get("releases", [])

        if not releases:
            print(f"No releases found for release group ID {release_group_id}.")
            return []

        release_details = []
        for release in releases:
            #print(release)
            release_info = {"id": release['id'], "title": release['title'], "projects": release['projects']}
            release_details.append(release_info)

        return release_details
    else:
        print(f"Failed to fetch release details for release group ID {release_group_id}: {response.text}")
        return []

def release_group_exists(api_key, release_group_name, release_group_version):
    release_groups = list_release_groups(api_key)
    for group in release_groups:
        if group['name'] == release_group_name:
            # Check if the release group has any versions
            if "releases" in group and group["releases"]:
                for release in group["releases"]:
                    if release["title"] == release_group_version:
                        print(f"Release group '{release_group_name}' already exists with Release Group ID: {group['id']} and has version '{release_group_version}'.")
                        exit()
                print(f"Release group '{release_group_name}' already exists with Release Group ID: {group['id']} but the specified version '{release_group_version}' does not exist.")
                return group['id']
            else:
                # should never return this case
                print(f"Release group '{release_group_name}' already exists with Release Group ID: {group['id']} but has no versions.")
                return False
    print(f"Release group '{release_group_name}' doesn't exist.")
    return False

def create_new_release_group(api_key, release_group_name, release_group_version, licensing_policy_id=None, security_policy_id=None, quality_policy_id=None, teams=None):
    # Check if the test project exists
    projects = list_projects(api_key, suppress_output=True)
    test_project = next((project for project in projects if project["title"] == "test-project-for-release-group-creation"), None)

    if test_project:
        test_project_id = test_project["locator"]
    else:
        # Perform necessary setup actions if the test project doesn't exist
        create_test_directory()
        create_blank_requirements_file()
        run_fossa_analyze(api_key)
        run_fossa_test(api_key)

        # Retrieve the project ID again after setup actions
        projects = list_projects(api_key, suppress_output=True)
        test_project = next((project for project in projects if project["title"] == "test-project-for-release-group-creation"), None)

        if not test_project:
            print("Error: Test project not found.")
            return

        test_project_id = test_project["locator"]

    url = f"{FOSSA_API_BASE_URL}/project_group"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "title": release_group_name,
        "release": {
            "projects": [
                {
                    "projectId": test_project_id,
                    "branch": "test-branch",
                    "revisionId": test_project_id + "$test-revision"
                }
            ],
            "title": release_group_version
        }
    }
    if licensing_policy_id:
        payload["licensingPolicyId"] = licensing_policy_id
    if security_policy_id:
        payload["securityPolicyId"] = security_policy_id
    if quality_policy_id:
        payload["qualityPolicyId"] = quality_policy_id
    if teams:
        payload["teams"] = teams

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Release group created successfully.")
    else:
        print(f"Failed to create release group: {response.text}")

def add_test_project_to_existing_release_group(api_key, release_group_id, release_group_version):
    # Check if the test project exists
    projects = list_projects(api_key, suppress_output=True)
    test_project = next((project for project in projects if project["title"] == "test-project-for-release-group-creation"), None)

    if test_project:
        test_project_id = test_project["locator"]
    else:
        # Perform necessary setup actions if the test project doesn't exist
        create_test_directory()
        create_blank_requirements_file()
        run_fossa_analyze(api_key)
        run_fossa_test(api_key)

        # Retrieve the project ID again after setup actions
        projects = list_projects(api_key, suppress_output=True)
        test_project = next((project for project in projects if project["title"] == "test-project-for-release-group-creation"), None)

        if not test_project:
            print("Error: Test project not found.")
            return

        test_project_id = test_project["locator"]

    url = f"{FOSSA_API_BASE_URL}/project_group/{release_group_id}/release"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "title": release_group_version,
        "projects": [
            {
                "projectId": test_project_id,
                "branch": "test-branch",
                "revisionId": test_project_id + "$test-revision"
            }
        ],
        "projectsToDelete":[]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Project added to release group successfully.")
    else:
        print(f"Failed to add project to release group: {response.text}")


def copy_projects_between_release_groups(api_key, release_group_name_src, release_group_name_dest, release_group_version):
    # Check if both release groups exist and have the same version
    release_groups = list_release_groups(api_key)

    src_version_exists = False
    dest_version_exists = False

    for release in release_groups:
        print('this is release in release groups')
        print(release)
        if release["name"] == release_group_name_src:
            if "releases" in release:
                for release_group in release["releases"]:
                    if release_group["title"] == release_group_version:
                        projects_to_copy = release_group["projects"]
                        print("Source release version exists + projects copied")
                        src_version_exists = True
                        break

    for release in release_groups:
        if release["name"] == release_group_name_dest:
            release_group_destination_id = release["id"]
            if "releases" in release:
                for release_group in release["releases"]:
                    if release_group["title"] == release_group_version:
                        release_group_version_destination_id = release_group["id"]
                        print("Destination release version exists")
                        dest_version_exists = True
                        break

    if not src_version_exists and not dest_version_exists:
        print(f"Doesn't exist in parallel release groups '{release_group_name_src}' + '{release_group_name_dest}' with version '{release_group_version}'.")
        return

    # Add projects to destination release group version
    url = f"{FOSSA_API_BASE_URL}/project_group/{release_group_destination_id}/release/{release_group_version_destination_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "title": release_group_version,
        "projects": projects_to_copy,
        "projectsToDelete": []
    }

    response = requests.put(url, headers=headers, json=payload)
    print('what is response')
    print(response)

    if response.status_code == 200:
        print("Projects copied successfully from release group '{0}' to release group '{1}' with version '{2}'.".format(release_group_name_src, release_group_name_dest, release_group_version))
    else:
        print(f"Failed to copy projects to release group '{release_group_name_dest}': {response.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage FOSSA projects, teams, and policies.")
    parser.add_argument("command", choices=["list", "add", "copy"], help="Command to execute")
    parser.add_argument("--type", choices=["projects", "teams", "policies", "release-groups"], help="Type of resource to list")
    parser.add_argument("--release-group-name", help="Name of the release group")
    parser.add_argument("--release-group-version", help="Version of the release group")
    parser.add_argument("--release-group-name-src", help="Name of the source release group for copying projects")
    parser.add_argument("--release-group-name-dest", help="Name of the destination release group for copying projects")
    parser.add_argument("--release-projects", action="store_true", help="Projects of a particular release group version")
    parser.add_argument("--licensing-policy-id", help="ID of the licensing policy")
    parser.add_argument("--security-policy-id", help="ID of the security policy")
    parser.add_argument("--quality-policy-id", help="ID of the quality policy")
    parser.add_argument("--teams", nargs="+", type=int, help="IDs of the teams")
    parser.add_argument("--fossa-api-key", help="FOSSA API key")
    args = parser.parse_args()

    if args.command == "list":
        if args.type == "projects":
            list_projects(args.fossa_api_key, suppress_output=False)
        elif args.type == "teams":
            list_teams(args.fossa_api_key)
        elif args.type == "policies":
            list_policies(args.fossa_api_key)
        elif args.type == "release-groups":
            list_release_groups(args.fossa_api_key, args.release_projects)
        else:
            print("Please specify a valid type (--type projects/teams/policies/release_groups) to list.")
    elif args.command == "add":
        if not args.release_group_name or not args.release_group_version:
            print("Both release group name and release group version are required for the 'add' command.")
        else:
            if check_fossa_existence():
                release_group_id = release_group_exists(args.fossa_api_key, args.release_group_name, args.release_group_version)
                if release_group_id:
                    add_test_project_to_existing_release_group(args.fossa_api_key, release_group_id, args.release_group_version)
                else:
                    create_new_release_group(args.fossa_api_key, args.release_group_name, args.release_group_version, args.licensing_policy_id, args.security_policy_id, args.quality_policy_id, args.teams)
    elif args.command == "copy":
        if not args.release_group_name_src or not args.release_group_name_dest or not args.release_group_version:
            print("Both source release group name, destination release group name, and release group version are required for the 'copy' command.")
        else:
            if check_fossa_existence():
                copy_projects_between_release_groups(args.fossa_api_key, args.release_group_name_src, args.release_group_name_dest, args.release_group_version)
