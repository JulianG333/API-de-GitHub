from github import Github

class GitHubService:
    def __init__(self, token: str):
        self.token = token
        self.client = Github(self.token)

    def get_user_repos(self, username):
        user = self.client.get_user(username)
        repos = user.get_repos()
        repos_with_pulls = []
        for repo in repos:
            pulls = self.get_pull_requests(repo)
            repo_data = repo.raw_data
            repo_data["pulls"] = pulls
            repos_with_pulls.append(repo_data)
        return repos_with_pulls

    def get_pull_requests(self, repo):
        pulls = repo.get_pulls(state='open')
        return [{"title": pull.title, "html_url": pull.html_url} for pull in pulls]

    async def get_user_contributions(self, username: str):
        user = self.client.get_user(username)
        repos = user.get_repos()
        contributions = []
        for repo in repos:
            contributors = repo.get_contributors()
            for contrib in contributors:
                if contrib.login == username:
                    contributions.append({
                        "repo": repo.name,
                        "description": repo.description,
                        "url": repo.html_url,
                        "created_at": repo.created_at,
                        "updated_at": repo.updated_at,
                        "language": repo.language,
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "count": contrib.contributions
                    })
        return contributions

    def get_user_events(self, username):
        user = self.client.get_user(username)
        events = user.get_events()
        formatted_events = []
        for event in events:
            formatted_event = {
                "type": event.type,
                "repo": event.repo.name,
                "date": event.created_at
            }
            formatted_events.append(formatted_event)
        return formatted_events
