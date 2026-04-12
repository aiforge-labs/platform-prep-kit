"""Project Agent -- recommends, scaffolds, and evaluates portfolio projects."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from prep_agent.agents.base import BaseAgent


class ProjectAgent(BaseAgent):
    """Recommends and manages hands-on portfolio projects.

    Observe: user's gaps, quiz scores, current study progress, existing projects
    Reason: which projects would have the highest impact on hire-readiness?
    Act: list, scaffold, evaluate, or generate showcase write-ups
    Evaluate: does the user have demonstrable proof for their weakest areas?
    """

    def __init__(self, config: dict | None = None) -> None:
        super().__init__("project", config)
        self._prep_dir = Path(os.path.expanduser("~/.prep"))
        self._projects_dir = self._prep_dir / "projects"

    # ------------------------------------------------------------------
    # Template loading
    # ------------------------------------------------------------------

    def load_project_templates(self, role: str | None = None) -> list[dict[str, Any]]:
        """Load project templates from bundled YAML files.

        If *role* is given, only loads that role's projects.
        Otherwise loads all roles.
        """
        templates_dir = Path(__file__).resolve().parent.parent.parent / "project_templates"
        if not templates_dir.is_dir():
            return []

        projects: list[dict[str, Any]] = []
        for path in sorted(templates_dir.glob("*.yml")):
            if path.name.startswith("_"):
                continue
            with path.open("r") as f:
                data = yaml.safe_load(f) or {}
            file_role = data.get("role", path.stem)
            if role and file_role != role:
                continue
            for p in data.get("projects", []):
                p["role"] = file_role
                projects.append(p)
        return projects

    # ------------------------------------------------------------------
    # User project state
    # ------------------------------------------------------------------

    def list_user_projects(self) -> list[dict[str, Any]]:
        """Load all projects the user has started or completed."""
        if not self._projects_dir.is_dir():
            return []
        entries: list[dict[str, Any]] = []
        for proj_dir in sorted(self._projects_dir.iterdir()):
            state_file = proj_dir / "project.json"
            if state_file.is_file():
                with state_file.open("r") as f:
                    entries.append(json.load(f))
        return entries

    def get_user_project(self, project_id: str) -> dict[str, Any] | None:
        """Load a single user project by ID."""
        state_file = self._projects_dir / project_id / "project.json"
        if state_file.is_file():
            with state_file.open("r") as f:
                return json.load(f)
        return None

    def _save_user_project(self, entry: dict[str, Any]) -> None:
        proj_dir = self._projects_dir / entry["id"]
        proj_dir.mkdir(parents=True, exist_ok=True)
        with (proj_dir / "project.json").open("w") as f:
            json.dump(entry, f, indent=2, default=str)
            f.write("\n")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def start_project(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Scaffold a project from a template spec.

        Creates the project directory under ~/.prep/projects/<id>/,
        writes starter files, and saves initial state.
        """
        project_id = spec["id"]
        proj_dir = self._projects_dir / project_id
        proj_dir.mkdir(parents=True, exist_ok=True)

        # Write starter files
        for filename, content in spec.get("starter_files", {}).items():
            file_path = proj_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                file_path.write_text(content)

        # Save project state
        entry = {
            "id": project_id,
            "spec_id": spec["id"],
            "title": spec["title"],
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "rubric_results": [
                {"description": r["description"], "met": False}
                for r in spec.get("rubric", [])
            ],
            "rubric_score": None,
            "showcase_path": None,
            "notes": "",
        }
        self._save_user_project(entry)
        return entry

    def check_project(self, project_id: str, met_indices: list[int]) -> dict[str, Any]:
        """Evaluate a project against its rubric.

        *met_indices* lists which rubric items (0-based) the user has completed.
        Returns the updated project entry.
        """
        entry = self.get_user_project(project_id)
        if not entry:
            return {"error": f"Project '{project_id}' not found"}

        rubric = entry.get("rubric_results", [])
        for i, item in enumerate(rubric):
            item["met"] = i in met_indices

        met_count = sum(1 for r in rubric if r["met"])
        total = len(rubric) if rubric else 1
        score = round(met_count / total * 100, 1)

        entry["rubric_results"] = rubric
        entry["rubric_score"] = score

        if score == 100:
            entry["status"] = "completed"
            entry["completed_at"] = datetime.now().isoformat()

        self._save_user_project(entry)
        return entry

    def generate_showcase(self, project_id: str) -> str | None:
        """Generate a portfolio write-up for a completed project.

        Returns the markdown content and saves it to the project directory.
        """
        entry = self.get_user_project(project_id)
        if not entry:
            return None

        rubric = entry.get("rubric_results", [])
        met = [r for r in rubric if r.get("met")]
        score = entry.get("rubric_score", 0)

        md_lines = [
            f"# {entry['title']}",
            "",
            f"**Status:** {entry['status']}  ",
            f"**Started:** {entry.get('started_at', '—')}  ",
        ]
        if entry.get("completed_at"):
            md_lines.append(f"**Completed:** {entry['completed_at']}  ")
        md_lines.append(f"**Rubric Score:** {score}%  ")
        md_lines.append("")

        md_lines.append("## What I Built")
        md_lines.append("")
        md_lines.append("<!-- Describe what you built and the problem it solves -->")
        md_lines.append("")

        md_lines.append("## Key Decisions & Trade-offs")
        md_lines.append("")
        md_lines.append("<!-- Explain your architectural choices and why -->")
        md_lines.append("")

        md_lines.append("## Skills Demonstrated")
        md_lines.append("")
        for r in met:
            md_lines.append(f"- {r['description']}")
        md_lines.append("")

        md_lines.append("## What I Learned")
        md_lines.append("")
        md_lines.append("<!-- Reflect on what was new or challenging -->")
        md_lines.append("")

        if entry.get("notes"):
            md_lines.append("## Notes")
            md_lines.append("")
            md_lines.append(entry["notes"])
            md_lines.append("")

        content = "\n".join(md_lines)

        # Save to project directory
        showcase_path = self._projects_dir / project_id / "SHOWCASE.md"
        showcase_path.write_text(content)
        entry["showcase_path"] = str(showcase_path)
        self._save_user_project(entry)

        return content

    # ------------------------------------------------------------------
    # Ranking / recommendations
    # ------------------------------------------------------------------

    def rank_projects(
        self,
        templates: list[dict[str, Any]],
        quiz_history: list[dict[str, Any]] | None = None,
        completed_ids: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Rank available projects by gap impact.

        Projects covering weak quiz topics score higher.
        Already-completed projects are excluded.
        """
        completed_ids = completed_ids or set()
        available = [t for t in templates if t["id"] not in completed_ids]

        if not quiz_history:
            return available

        # Compute average score per topic
        topic_scores: dict[str, list[float]] = defaultdict(list)
        for q in quiz_history:
            total = q.get("total", 0)
            if total > 0:
                topic_scores[q["topic"]].append(q["score"] / total * 100)

        weak_topics: set[str] = set()
        for topic, scores in topic_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 70:
                weak_topics.add(topic.lower())

        def impact_score(project: dict) -> float:
            """Higher score = more relevant to weak areas."""
            track = project.get("track_id", "").lower()
            topics = [t.lower() for t in project.get("topics", [])]
            score = 0.0
            for wt in weak_topics:
                if wt in track or any(wt in t for t in topics):
                    score += 10
            # Prefer easier projects first if all else equal
            diff_bonus = {"starter": 2, "intermediate": 1, "advanced": 0}
            score += diff_bonus.get(project.get("difficulty", ""), 0)
            return score

        available.sort(key=impact_score, reverse=True)
        return available

    # ------------------------------------------------------------------
    # Portfolio summary
    # ------------------------------------------------------------------

    def get_portfolio_summary(
        self,
        quiz_avg: float = 0,
    ) -> dict[str, Any]:
        """Compute aggregated portfolio metrics."""
        user_projects = self.list_user_projects()
        completed = [p for p in user_projects if p.get("status") == "completed"]
        in_progress = [p for p in user_projects if p.get("status") == "in_progress"]

        all_templates = self.load_project_templates()
        total_available = len(all_templates)

        # Collect skills from completed projects
        skills: set[str] = set()
        rubric_scores: list[float] = []
        for p in completed:
            for r in p.get("rubric_results", []):
                if r.get("met"):
                    skills.add(r["description"])
            if p.get("rubric_score") is not None:
                rubric_scores.append(p["rubric_score"])

        avg_rubric = round(sum(rubric_scores) / len(rubric_scores), 1) if rubric_scores else None

        # Hire-readiness: weighted blend of quiz avg + project completion
        project_pct = (len(completed) / total_available * 100) if total_available else 0
        hire_readiness = round(quiz_avg * 0.4 + project_pct * 0.6, 1) if total_available else quiz_avg

        return {
            "projects_completed": len(completed),
            "projects_in_progress": len(in_progress),
            "total_projects_available": total_available,
            "skills_demonstrated": sorted(skills),
            "avg_rubric_score": avg_rubric,
            "hire_readiness_pct": min(hire_readiness, 100),
        }

    # ------------------------------------------------------------------
    # ReAct overrides
    # ------------------------------------------------------------------

    def observe(self, context: dict) -> dict:
        return {
            "weak_topics": context.get("weak_topics", []),
            "quiz_history": context.get("quiz_history", []),
            "completed_project_ids": {
                p["id"]
                for p in self.list_user_projects()
                if p.get("status") == "completed"
            },
            "role": context.get("role", ""),
        }

    def reason(self, observations: dict) -> dict:
        weak = observations.get("weak_topics", [])
        completed = observations.get("completed_project_ids", set())
        role = observations.get("role", "")

        templates = self.load_project_templates(role or None)
        available = [t for t in templates if t["id"] not in completed]

        if not available:
            return {
                "action": "all_done",
                "params": {},
                "reasoning": "All available projects for this role are completed.",
            }

        if weak:
            return {
                "action": "recommend_for_weak",
                "params": {"weak_topics": weak, "templates": available},
                "reasoning": (
                    f"Weak areas detected: {', '.join(weak[:3])}. "
                    "Recommending projects that address these gaps."
                ),
            }

        return {
            "action": "recommend_next",
            "params": {"templates": available},
            "reasoning": "No specific weak areas. Recommending next available project.",
        }

    def act(self, action: str, params: dict) -> dict:
        if action == "all_done":
            return {
                "result": "all_projects_completed",
                "success": True,
                "message": "All projects completed. Portfolio is strong.",
            }

        templates = params.get("templates", [])
        if not templates:
            return {
                "result": "no_projects",
                "success": True,
                "message": "No project templates found for this role.",
            }

        ranked = self.rank_projects(
            templates,
            quiz_history=params.get("quiz_history"),
        )
        top = ranked[0] if ranked else templates[0]
        return {
            "result": "recommendation",
            "success": True,
            "message": f"Recommended project: {top['title']}",
            "project": top,
        }

    def evaluate(self, result: dict) -> dict:
        return {
            "satisfied": result.get("success", False),
            "feedback": "",
            "next_action": None,
        }
