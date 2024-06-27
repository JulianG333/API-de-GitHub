import httpx
from fastapi import HTTPException
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


    async def get_user_contributions(self, username: str):
        url = f"https://api.github.com/users/{username}/repos"
        
        try:
            async with self.client.get(url) as response:
                response.raise_for_status()
                repos = await response.json()
        except httpx.HTTPStatusError as http_err:
            raise HTTPException(status_code=http_err.response.status_code, detail=await http_err.response.json())
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"Error al obtener repositorios de GitHub: {str(err)}")
        
        contributions = []
        for repo in repos:
            contrib_url = f"https://api.github.com/repos/{username}/{repo['name']}/contributors"
            try:
                async with self.client.get(contrib_url) as contrib_response:
                    contrib_response.raise_for_status()
                    contrib_data = await contrib_response.json()
                    for contrib in contrib_data:
                        if contrib["login"] == username:
                            contributions.append({
                                "repo": repo["name"],
                                "description": repo["description"],
                                "url": repo["html_url"],
                                "created_at": repo["created_at"],
                                "updated_at": repo["updated_at"],
                                "language": repo["language"],
                                "stars": repo["stargazers_count"],
                                "forks": repo["forks_count"],
                                "count": contrib["contributions"]
                            })
            except httpx.HTTPStatusError as http_err:
                raise HTTPException(status_code=http_err.response.status_code, detail=await http_err.response.json())
            except Exception as err:
                raise HTTPException(status_code=500, detail=f"Error al obtener contribuciones de GitHub: {str(err)}")
        
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