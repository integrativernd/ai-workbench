import os
import requests
import base64

def get_github_readme(owner, repo, token):
    """
    Fetches the README content from a private GitHub repository.

    Args:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    token (str): GitHub personal access token with repo scope.

    Returns:
    str: The content of the README file, or None if the request fails.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        content = response.json()["content"]
        decoded_content = base64.b64decode(content).decode("utf-8")
        return decoded_content

    except requests.RequestException as e:
        print(f"Error fetching README: {e}")
        return None
    
print(get_github_readme("integrativernd", "ai-agent", os.environ["GITHUB_TOKEN"]))