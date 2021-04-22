#!/usr/bin/env python

# Just a little script to manage Terraform Cloud
# https://www.terraform.io/docs/cloud/api/index.html"""

import sys
import requests
import click

# Define Terraform Cloud API URL
API_URL = "https://app.terraform.io/api/v2"


def organizations(headers, organization, email):
    """[summary]

    Args:
        headers ([type]): [description]
        organization ([type]): [description]
        email ([type]): [description]
    """

    url = f"{API_URL}/organizations"

    try:
        request = requests.get(url, headers=headers)
        # Define data from JSON response data
        data = request.json().get("data")
        # Get list of all organizations
        organizations = [org for org in data]
        # Get list of just org names
        org_names = [org["attributes"]["name"] for org in organizations]
        # Add organization if not already found
        if organization not in org_names:
            add_org(headers, organization, email)

    except requests.exceptions.HTTPError as err:
        print(str(err))
        sys.exit(2)


def add_org(headers, organization, email):
    """[summary]

    Args:
        headers ([type]): [description]
        organization ([type]): [description]
        email ([type]): [description]
    """

    url = f"{API_URL}/organizations"
    payload = {
        "data": {
            "type": "organizations",
            "attributes": {"name": organization, "email": email},
        }
    }

    try:
        request = requests.post(url, headers=headers, json=payload)
        request.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(str(err))
        sys.exit(2)


def workspaces(headers, organization):
    """[summary]

    Args:
        headers ([type]): [description]
        organization ([type]): [description]

    Returns:
        [type]: [description]
    """

    url = f"{API_URL}/organizations/{organization}/workspaces"

    try:
        request = requests.get(url, headers=headers)
        data = request.json().get("data")
        workspaces = [workspace for workspace in data]
        workspace_names = [workspace["attributes"]["name"] for workspace in workspaces]
        return workspace_names
    except requests.exceptions.HTTPError as err:
        print(str(err))
        sys.exit(2)


def environments(headers, organization, workspace):
    """[summary]

    Args:
        headers ([type]): [description]
        organization ([type]): [description]
        workspace ([type]): [description]
    """

    workspace_names = workspaces(headers, organization)

    # We account for development, staging and production
    environments = ["development", "staging", "production"]

    # Iterate over each environment defined in environments
    for environment in environments:
        workspace_env = f"{workspace}-{environment}"
        if workspace_env not in workspace_names:
            url = f"{API_URL}/organizations/{organization}/workspaces"
            payload = {
                "data": {
                    "type": "workspaces",
                    "attributes": {"name": workspace_env, "operations": False},
                }
            }

            try:
                request = requests.post(url, headers=headers, json=payload)
                request.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(str(err))
                sys.exit(2)

        else:
            url = f"{API_URL}/organizations/{organization}/workspaces/{workspace_env}"
            payload = {
                "data": {"type": "workspaces", "attributes": {"operations": False}}
            }

            try:
                request = requests.patch(url, json=payload, headers=headers)
                request.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(str(err))
                sys.exit(2)


@click.command()
@click.option("--email", help="Admin email")
@click.option("--organization", help="Terraform Cloud organization")
@click.option("--token", required=True, help="Terraform Cloud API token")
@click.option("--workspace", help="Terraform Cloud organization workspace")
def main(email, organization, token, workspace):
    """[summary]

    Args:
        email ([type]): [description]
        organization ([type]): [description]
        token ([type]): [description]
        workspace ([type]): [description]
    """

    # Define headers to use for requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json",
    }

    organizations(headers, organization, email)
    environments(headers, organization, workspace)


if __name__ == "__main__":
    main()
