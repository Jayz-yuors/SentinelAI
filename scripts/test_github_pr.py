import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

owner = "Jayz-yuors"
repo = "Stock-Insights"

# CHANGE THIS to the candidate branch that SentinelAI already pushed
candidate_branch = "PUT_CANDIDATE_BRANCH_HERE"

url = f"https://api.github.com/repos/{owner}/{repo}/pulls"

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}",
    "X-GitHub-Api-Version": "2026-03-10",
}

data = {
    "title": "SentinelAI test PR",
    "body": "Testing SentinelAI GitHub PR creation.",
    "head": candidate_branch,
    "base": "main",
}

response = requests.post(
    url,
    headers=headers,
    json=data,
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)