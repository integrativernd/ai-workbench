import os
import requests
import base64
from datetime import datetime

API_URL = "https://api.github.com"

def create_hello_world_pr(owner, repo, token, base_branch):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Generate branch name
    new_branch = f"add-hello-world-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Get the SHA of the latest commit on the base branch
    base_branch_url = f"{API_URL}/repos/{owner}/{repo}/git/refs/heads/{base_branch}"
    response = requests.get(base_branch_url, headers=headers)
    response.raise_for_status()
    base_sha = response.json()["object"]["sha"]

    # Create a new branch
    new_branch_url = f"{API_URL}/repos/{owner}/{repo}/git/refs"
    new_branch_data = {
        "ref": f"refs/heads/{new_branch}",
        "sha": base_sha
    }
    response = requests.post(new_branch_url, headers=headers, json=new_branch_data)
    response.raise_for_status()

    # Create the new file in the new branch
    file_name = "hello_world.txt"
    file_content = "Hello, World!"
    file_url = f"{API_URL}/repos/{owner}/{repo}/contents/{file_name}"
    file_data = {
        "message": "Add Hello World file",
        "content": base64.b64encode(file_content.encode()).decode(),
        "branch": new_branch
    }
    response = requests.put(file_url, headers=headers, json=file_data)
    response.raise_for_status()

    # Create a pull request
    pr_url = f"{API_URL}/repos/{owner}/{repo}/pulls"
    pr_data = {
        "title": "Add Hello World file",
        "body": "This pull request adds a Hello World file to the project.",
        "head": new_branch,
        "base": base_branch
    }
    response = requests.post(pr_url, headers=headers, json=pr_data)
    response.raise_for_status()

    return response.json()["html_url"]

def main():
    # Get configuration from environment variables
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    token = os.environ.get("GITHUB_TOKEN")
    base_branch = os.environ.get("GITHUB_BASE_BRANCH", "main")

    if not all([owner, repo, token]):
        raise ValueError("Missing required environment variables. Please set GITHUB_OWNER, GITHUB_REPO, and GITHUB_TOKEN.")

    try:
        pr_url = create_hello_world_pr(owner, repo, token, base_branch)
        print(f"Pull request created successfully. URL: {pr_url}")
    except requests.RequestException as e:
        print(f"Error creating pull request: {e}")

if __name__ == "__main__":
    main()