import os
import requests
import base64

API_URL = "https://api.github.com"

def update_file_in_pr(owner, repo, token, pr_number, file_path, new_content):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get PR details
    pr_url = f"{API_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
    response = requests.get(pr_url, headers=headers)
    response.raise_for_status()
    pr_data = response.json()
    branch = pr_data["head"]["ref"]

    # Get the current file content
    file_url = f"{API_URL}/repos/{owner}/{repo}/contents/{file_path}"
    response = requests.get(file_url, headers=headers, params={"ref": branch})
    response.raise_for_status()
    file_data = response.json()

    decoded_content = base64.b64decode(file_data['content']).decode("utf-8")

    updated_content = f"{decoded_content}\n{new_content}"

    # # Update the file
    update_url = f"{API_URL}/repos/{owner}/{repo}/contents/{file_path}"
    update_data = {
        "message": f"Update {file_path}",
        "content": base64.b64encode(updated_content.encode('utf-8')).decode('utf-8'),
        "sha": file_data["sha"],
        "branch": branch
    }
    response = requests.put(update_url, headers=headers, json=update_data)
    response.raise_for_status()

    return pr_data["html_url"]

def main():
    # Get configuration from environment variables
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    token = os.environ.get("GITHUB_TOKEN")
    pr_number = 3
    file_path = "CHANGE_LOG.md"
    new_content = "## Updated Content\nThis is an updated content."

    if not all([owner, repo, token, pr_number, file_path, new_content]):
        raise ValueError("Missing required environment variables. Please set GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, GITHUB_PR_NUMBER, GITHUB_FILE_PATH, and GITHUB_NEW_CONTENT.")

    try:
        pr_url = update_file_in_pr(owner, repo, token, pr_number, file_path, new_content)
        print(f"File updated successfully in the pull request. PR URL: {pr_url}")
    except requests.RequestException as e:
        print(f"Error updating file in pull request: {e}")

if __name__ == "__main__":
    main()