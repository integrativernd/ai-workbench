import os
import requests
from datetime import datetime

API_URL = "https://api.github.com"

def post_github_issue(owner, repo, token, title, body, labels=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    issue_url = f"{API_URL}/repos/{owner}/{repo}/issues"
    issue_data = {
        "title": title,
        "body": body,
    }
    
    if labels:
        issue_data["labels"] = labels

    response = requests.post(issue_url, headers=headers, json=issue_data)
    response.raise_for_status()

    return response.json()["html_url"]

def create_github_issue(request_data):
    # Get configuration from environment variables
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    token = os.environ.get("GITHUB_TOKEN")

    if not all([owner, repo, token]):
        raise ValueError("Missing required environment variables. Please set GITHUB_OWNER, GITHUB_REPO, and GITHUB_TOKEN.")

    try:
        issue_url = post_github_issue(
            owner,
            repo,
            token,
            request_data["title"] or "New Issue",
            request_data["description"] or "This is a new issue.",
            # request_data.get("labels")
        )
        return f"Issue created successfully. {issue_url}"
    except requests.RequestException as e:
        print(f"Error creating issue: {e}")
        return f"Error creating issue: {str(e)}"

def read_default_github_issue(owner, repo, token, issue_number):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    issue_url = f'{API_URL}/repos/{owner}/{repo}/issues/{issue_number}'
    response = requests.get(issue_url, headers=headers)
    response.raise_for_status()

    issue_data = response.json()
    title = issue_data['title']
    body = issue_data['body']

    return title, body

def read_github_issue(request_data):
    # Get configuration from environment variables
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    token = os.environ.get("GITHUB_TOKEN")

    if not all([owner, repo, token]):
        raise ValueError("Missing required environment variables. Please set GITHUB_OWNER, GITHUB_REPO, and GITHUB_TOKEN.")

    try:
        title, body = read_default_github_issue(
            owner,
            repo,
            token,
            request_data["issue_number"],
        )
        return title, body
    except requests.RequestException as e:
        print(f"Error analyzing issue: {e}")
        return f"Error analyzing issue: {str(e)}"










# if __name__ == "__main__":
#     result = create_github_issue({
#         "title": "Test Issue",
#         "body": "This is a test issue created at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "labels": ["test", "automated"]
#     })
#     print(result)