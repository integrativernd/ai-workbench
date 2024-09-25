import os
import requests
import base64
from datetime import datetime

API_URL = "https://api.github.com"

def update_file_and_create_pr(owner, repo, token, base_branch, file_path, new_content):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Generate branch name
    new_branch = f"update-file-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

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

    # Get the current file content and SHA
    file_url = f"{API_URL}/repos/{owner}/{repo}/contents/{file_path}"
    response = requests.get(file_url, headers=headers, params={"ref": new_branch})
    response.raise_for_status()
    current_file = response.json()
    current_sha = current_file["sha"]

    # Update the file in the new branch
    update_data = {
        "message": f"Update {file_path}",
        "content": base64.b64encode(new_content.encode()).decode(),
        "sha": current_sha,
        "branch": new_branch
    }
    response = requests.put(file_url, headers=headers, json=update_data)
    response.raise_for_status()

    # Create a pull request
    pr_url = f"{API_URL}/repos/{owner}/{repo}/pulls"
    pr_data = {
        "title": f"Update {file_path}",
        "body": f"This pull request updates the file {file_path}.",
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
    file_path = os.environ.get("GITHUB_FILE_PATH")
    new_content = os.environ.get("GITHUB_FILE_CONTENT", "This is the updated content.")

    if not all([owner, repo, token, file_path]):
        raise ValueError("Missing required environment variables. Please set GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, and GITHUB_FILE_PATH.")

    try:
        pr_url = update_file_and_create_pr(owner, repo, token, base_branch, file_path, new_content)
        print(f"Pull request for file update created successfully. URL: {pr_url}")
    except requests.RequestException as e:
        print(f"Error updating file and creating pull request: {e}")

if __name__ == "__main__":
    main()