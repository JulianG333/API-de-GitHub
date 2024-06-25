import httpx

class GitHubService:
    def __init__(self, token: str):
        self.token = token
        self.client = httpx.Client(headers={"Authorization": f"token {self.token}"})

    def get_user_repos(self, username):
        url = f"https://api.github.com/users/{username}/repos"
        response = self.client.get(url)
        response.raise_for_status()
        repos = response.json()
        repos_with_pulls = []
        for repo in repos:
            pulls = self.get_pull_requests(username, repo["name"])
            repo["pulls"] = pulls
            repos_with_pulls.append(repo)
        return repos_with_pulls

    def get_pull_requests(self, username, repo_name):
        url = f"https://api.github.com/repos/{username}/{repo_name}/pulls"
        response = self.client.get(url)
        response.raise_for_status()
        pulls = response.json()
        return [{"title": pull["title"], "html_url": pull["html_url"]} for pull in pulls]

    
    def get_user_contributions(self, username: str):
        url = f"https://api.github.com/users/{username}/repos"
        response = self.client.get(url)
        response.raise_for_status()
        repos = response.json()
        
        contributions = []
        for repo in repos:
            contrib_url = f"https://api.github.com/repos/{username}/{repo['name']}/contributors"
            contrib_response = self.client.get(contrib_url)
            contrib_response.raise_for_status()
            contrib_data = contrib_response.json()
            for contrib in contrib_data:
                if contrib["login"] == username:
                    contributions.append({
                        "repo": repo["name"],
                        "count": contrib["contributions"]
                    })
        return contributions
    
    def get_user_events(self, username):
            url = f"https://api.github.com/users/{username}/events"
            response = self.client.get(url)
            response.raise_for_status()
            events = response.json()
            formatted_events = []
            for event in events:
                formatted_event = {
                    "type": event["type"],
                    "repo": event["repo"]["name"],
                    "date": event["created_at"]
                }
                formatted_events.append(formatted_event)
            return formatted_events