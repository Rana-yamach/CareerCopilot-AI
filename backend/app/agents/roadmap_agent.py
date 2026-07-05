"""Roadmap Agent (TASK-207): missing_skills + weekly_hours -> haftalık plan."""
from __future__ import annotations

import math

from app.agents.base import BaseAgent


def _heuristic_plan(missing_skills: list[dict], weekly_hours: int) -> dict:
    total_estimated_weeks = sum(skill.get("estimated_weeks", 3) for skill in missing_skills) or 4
    total_weeks = max(4, min(12, math.ceil(total_estimated_weeks * (10 / max(weekly_hours, 1)) ** 0.3)))

    weekly_plan = []
    skills_cycle = missing_skills or [{"name": "Genel Kariyer Gelişimi"}]
    for week in range(1, total_weeks + 1):
        skill = skills_cycle[(week - 1) % len(skills_cycle)]
        weekly_plan.append(
            {
                "week": week,
                "theme": f"{skill.get('name', 'Genel Konu')} Çalışması",
                "tasks": [
                    {"title": f"{skill.get('name', 'Konu')} temel kavramlarını tekrar et", "done": False, "resource": "Kişisel araştırma"},
                    {"title": f"{skill.get('name', 'Konu')} ile ilgili pratik proje/alıştırma yap", "done": False, "resource": "leetcode.com / kişisel proje"},
                ],
            }
        )

    milestones = [
        {"week": w, "title": f"{w}. hafta değerlendirmesi tamamlandı"}
        for w in (total_weeks // 2, total_weeks)
        if w > 0
    ]

    return {"total_weeks": total_weeks, "milestones": milestones, "weekly_plan": weekly_plan}


class RoadmapAgent(BaseAgent):
    name = "roadmap_agent"
    system_prompt_path = "roadmap_tr.txt"

    async def generate(self, missing_skills: list[dict], weekly_hours: int) -> dict:
        prompt = self.load_prompt(missing_skills=missing_skills, weekly_hours=weekly_hours)
        parsed, _used_fallback = await self.generate_json_with_fallback(
            prompt,
            fallback_fn=lambda: _heuristic_plan(missing_skills, weekly_hours),
            validate_fn=lambda p: bool(p.get("weekly_plan")),
            max_tokens=1024,
            temperature=0.5,
        )
        return parsed
