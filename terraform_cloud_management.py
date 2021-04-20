#!/usr/bin/env python
"""terraform_cloud_management.py"""

# Just a little script to manage Terraform Cloud
# https://www.terraform.io/docs/cloud/api/index.html"""


import argparse
import sys
import requests


def cli_args():
    """Console script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument(
        "--organization", required=True, help="Terraform Cloud organization"
    )
    parser.add_argument("--token", required=True, help="Terraform Cloud API token")
    parser.add_argument(
        "--workspace", required=True, help="Terraform Cloud organization workspace"
    )
    args = parser.parse_args()

    return args


def main():
    """Main script execution"""

    # Get CLI args
    args = cli_args()

    # Get email from args
    email = args.email
    # Get organization from args
    organization = args.organization
    # Get API token from args
    token = args.token
    # Get workspace from args
    workspace = args.workspace

    # Define Terraform Cloud API URL
    api_url = "https://app.terraform.io/api/v2"
    # Define headers to use for requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json",
    }

    # Define organizations list and use for collection. Will be used more in the
    # future.
    organizations = []
    # Define API URL for organizations
    url = f"{api_url}/organizations"

    # Get all organizations
    request = requests.get(url, headers=headers)
    # Define data from JSON response data
    data = request.json().get("data")

    # Iterate through JSON data and append organization names to oranizations
    for item in data:
        organizations.append(item["attributes"]["name"])

    # If organization is not found, create it
    if organization not in organizations:
        url = f"{api_url}/organizations"
        payload = {
            "data": {
                "type": "organizations",
                "attributes": {"name": organization, "email": email},
            }
        }

        request = requests.post(url, headers=headers, json=payload)

        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(str(err))
            sys.exit(2)

    workspaces = []
    url = f"{api_url}/organizations/{organization}/workspaces"
    request = requests.get(url, headers=headers)
    data = request.json().get("data")
    for item in data:
        workspaces.append(item["attributes"]["name"])

    # We account for development, staging and production
    environments = ["development", "staging", "production"]

    # Iterate over each environment defined in environments
    for environment in environments:
        workspace_env = f"{workspace}-{environment}"
        if workspace_env not in workspaces:
            url = f"{api_url}/organizations/{organization}/workspaces"
            payload = {
                "data": {
                    "type": "workspaces",
                    "attributes": {"name": workspace_env, "operations": False},
                }
            }

            request = requests.post(url, headers=headers, json=payload)

            try:
                request.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(str(err))
                sys.exit(2)

        else:
            url = f"{api_url}/organizations/{organization}/workspaces/{workspace_env}"
            payload = {
                "data": {"type": "workspaces", "attributes": {"operations": False}}
            }

            request = requests.patch(url, json=payload, headers=headers)

            try:
                request.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(str(err))
                sys.exit(2)


if __name__ == "__main__":
    main()
