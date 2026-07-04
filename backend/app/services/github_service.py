"""GitHub servisi (TASK-212): PyGithub ile public repo erişimi.

OAuth kullanılmaz; yalnızca `GITHUB_API_TOKEN` (public scope) ile rate limit
artırılır.
"""
from __future__ import annotations

from github import Github, GithubException

from app.config import settings
from app.core.constants import MSG_GITHUB_API_ERROR, MSG_GITHUB_USER_NOT_FOUND
from app.core.exceptions import ExternalServiceError, NotFoundError


def _client() -> Github:
    if settings.github_api_token:
        return Github(settings.github_api_token)
    return Github()


def get_github_user_summary(username: str) -> dict:
    try:
        gh = _client()
        gh_user = gh.get_user(username)
        return {
            "github_username": gh_user.login,
            "public_repos": gh_user.public_repos,
            "avatar_url": gh_user.avatar_url,
            "verified": True,
        }
    except GithubException as exc:
        if exc.status == 404:
            raise NotFoundError(MSG_GITHUB_USER_NOT_FOUND) from exc
        raise ExternalServiceError(MSG_GITHUB_API_ERROR, code="GITHUB_ERROR") from exc
    except Exception as exc:  # noqa: BLE001 - DNS/bağlantı hataları GithubException olmayabilir
        raise ExternalServiceError(MSG_GITHUB_API_ERROR, code="GITHUB_ERROR") from exc


def get_language_stats(username: str) -> dict:
    try:
        gh = _client()
        gh_user = gh.get_user(username)
        repos = list(gh_user.get_repos())
        totals: dict[str, int] = {}
        for repo in repos:
            if repo.fork:
                continue
            try:
                for lang, count in repo.get_languages().items():
                    totals[lang] = totals.get(lang, 0) + count
            except GithubException:
                continue

        total_bytes = sum(totals.values()) or 1
        percentages = {lang: round(count / total_bytes * 100, 1) for lang, count in totals.items()}

        return {
            "github_username": gh_user.login,
            "languages": percentages,
            "total_public_repos": gh_user.public_repos,
        }
    except GithubException as exc:
        raise ExternalServiceError(MSG_GITHUB_API_ERROR, code="GITHUB_ERROR") from exc
    except Exception as exc:  # noqa: BLE001 - DNS/bağlantı hataları GithubException olmayabilir
        raise ExternalServiceError(MSG_GITHUB_API_ERROR, code="GITHUB_ERROR") from exc


def get_projects_for_cv(username: str) -> list[dict]:
    try:
        gh = _client()
        gh_user = gh.get_user(username)
        repos = sorted(
            [r for r in gh_user.get_repos() if not r.fork],
            key=lambda r: r.stargazers_count,
            reverse=True,
        )
        projects = []
        for repo in repos[:20]:
            tech_stack = []
            try:
                tech_stack = list(repo.get_languages().keys())[:5]
            except GithubException:
                pass
            projects.append(
                {
                    "name": repo.name,
                    "description": repo.description or "",
                    "tech_stack": tech_stack,
                    "repo_url": repo.html_url,
                    "stars": repo.stargazers_count,
                }
            )
        return projects
    except GithubException as exc:
        raise ExternalServiceError(MSG_GITHUB_API_ERROR, code="GITHUB_ERROR") from exc
    except Exception as exc:  # noqa: BLE001 - DNS/bağlantı hataları GithubException olmayabilir
        raise ExternalServiceError(MSG_GITHUB_API_ERROR, code="GITHUB_ERROR") from exc
