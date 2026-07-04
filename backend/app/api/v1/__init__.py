from fastapi import APIRouter

from app.api.v1 import agent, analysis, auth, cv, documents, github, health, interview, profile, tasks

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(cv.router, prefix="/cv", tags=["cv"])
api_router.include_router(analysis.skill_gap_router, prefix="/skill-gap", tags=["skill-gap"])
api_router.include_router(analysis.roadmap_router, prefix="/roadmap", tags=["roadmap"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
