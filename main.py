from fastapi import FastAPI, Request, HTTPException, Depends, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from services.github_service import GitHubService
import os
import httpx

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class RepoCreateRequest(BaseModel):
    repo_name: str
    private: bool = True
    user_name: str
    pull_request: str
    

def get_github_service():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise HTTPException(status_code=400, detail="GitHub token not provided")
    return GitHubService(token)

@app.get("/")
async def read_root(request: Request, username: str = Query(None)):
    if username:
        return RedirectResponse(url=f"/users/{username}/repos")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/users/{username}/repos")
async def get_user_repos(username: str, request: Request, github_service: GitHubService = Depends(get_github_service)):
    try:
        repos = github_service.get_user_repos(username,)
        return templates.TemplateResponse("repos.html", {"request": request, "repos": repos, "username": username})
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
    

@app.get("/users/{username}/repos")
async def get_user_repos(username: str, request: Request, github_service: GitHubService = Depends(get_github_service)):
    try:
        repos = github_service.get_user_repos(username)
        repos_with_pulls = []
        for repo in repos:
            pulls = github_service.get_pull_requests(username, repo["name"]) 
            repo["pulls"] = pulls 
            repos_with_pulls.append(repo) 
        return templates.TemplateResponse("repos.html", {"request": request, "repos": repos_with_pulls, "username": username})
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

@app.get("/users/{username}/activity")
async def get_user_activity(username: str, request: Request, github_service: GitHubService = Depends(get_github_service)):
    try:
        events = github_service.get_user_events(username)
        return templates.TemplateResponse("activity.html", {"request": request, "events": events, "username": username})
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

@app.get("/users/{username}/contributions")
async def get_user_contributions(username: str, request: Request, github_service: GitHubService = Depends(get_github_service)):
    try:
        contributions = github_service.get_user_contributions(username)
        return templates.TemplateResponse("contributions.html", {"request": request, "contributions": contributions, "username": username})
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)