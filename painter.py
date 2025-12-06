import requests
import base64
from getpass import getpass

def paint_commit(
    username: str,
    repository: str,
    token: str,
    date_str: str,
):
    api = "https://api.github.com"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    target_date = f"{date_str}T12:00:00Z"
    owner = username
    repo = repository
    branch = "main"
    file_path = "paint.txt"
    file_content = "github painter\n"

    ref = requests.get(
        f"{api}/repos/{owner}/{repo}/git/ref/heads/{branch}",
        headers=headers
    ).json()

    base_commit_sha = ref["object"]["sha"]

    base_commit = requests.get(
        f"{api}/repos/{owner}/{repo}/git/commits/{base_commit_sha}",
        headers=headers
    ).json()

    base_tree_sha = base_commit["tree"]["sha"]

    blob = requests.post(
        f"{api}/repos/{owner}/{repo}/git/blobs",
        headers=headers,
        json={
            "content": file_content,
            "encoding": "utf-8"
        }
    ).json()

    blob_sha = blob["sha"]

    tree = requests.post(
        f"{api}/repos/{owner}/{repo}/git/trees",
        headers=headers,
        json={
            "base_tree": base_tree_sha,
            "tree": [
                {
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                }
            ]
        }
    ).json()

    tree_sha = tree["sha"]

    commit = requests.post(
        f"{api}/repos/{owner}/{repo}/git/commits",
        headers=headers,
        json={
            "message": "paint commit",
            "tree": tree_sha,
            "parents": [base_commit_sha],
            "author": {
                "name": username,
                "email": f"{username}@users.noreply.github.com",
                "date": target_date
            },
            "committer": {
                "name": username,
                "email": f"{username}@users.noreply.github.com",
                "date": target_date
            }
        }
    ).json()

    new_commit_sha = commit["sha"]

    requests.patch(
        f"{api}/repos/{owner}/{repo}/git/refs/heads/{branch}",
        headers=headers,
        json={"sha": new_commit_sha}
    )

    print(f"Commit Successfuly on {date_str} date.")

print("GitHub Contribution Board Painter v1.0\nCredits: Simon Scap\n")

username = input("GitHub Account Name: ")
repository = input("GitHub Repository Name (choose a old repo): ")
token = getpass("GitHub Account Personel Access Token (PAT): ")
dates = input("Enter Commit Dates (YYYY-MM-DD, YYYY-MM-DD, ...): ").split(",")

for date in dates:
	paint_commit(
    	username=username,
    	repository=repository,
    	token=token,
    	date_str=date.strip()
    )
print("finished.")
