"""Tests for the project / portfolio engine (Phase 6)."""

from __future__ import annotations

import json
import os
import shutil
import tempfile

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_prep_dir(tmp_path):
    """Create a temporary ~/.prep directory for tests."""
    prep_dir = tmp_path / ".prep"
    prep_dir.mkdir()
    (prep_dir / "projects").mkdir()
    return prep_dir


@pytest.fixture
def agent(tmp_prep_dir):
    from prep_agent.agents.project import ProjectAgent

    a = ProjectAgent()
    a._prep_dir = tmp_prep_dir
    a._projects_dir = tmp_prep_dir / "projects"
    return a


@pytest.fixture
def sample_spec():
    return {
        "id": "test-project",
        "title": "Test Project",
        "description": "A test project for unit tests.",
        "track_id": "test-track",
        "topics": ["topic-a", "topic-b"],
        "difficulty": "starter",
        "estimated_hours": 4,
        "skills_demonstrated": ["Skill A", "Skill B"],
        "rubric": [
            {"description": "Item 1 is done"},
            {"description": "Item 2 is done"},
            {"description": "Item 3 is done"},
        ],
        "starter_files": {
            "README.md": "# Test\n",
            "main.py": "print('hello')\n",
        },
        "resources": ["https://example.com"],
    }


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class TestProjectModels:
    def test_project_spec_model(self):
        from prep_agent.models import ProjectSpec

        spec = ProjectSpec(
            id="test",
            title="Test",
            description="A test",
            track_id="t1",
            topics=["a"],
            difficulty="starter",
            estimated_hours=5,
            skills_demonstrated=["Python"],
            rubric=[{"description": "Works", "met": False}],
        )
        assert spec.id == "test"
        assert spec.difficulty.value == "starter"

    def test_project_entry_model(self):
        from prep_agent.models import ProjectEntry

        entry = ProjectEntry(id="p1", spec_id="s1", title="Project 1")
        assert entry.status.value == "in_progress"
        assert entry.completed_at is None

    def test_portfolio_summary_model(self):
        from prep_agent.models import PortfolioSummary

        s = PortfolioSummary()
        assert s.projects_completed == 0
        assert s.hire_readiness_pct == 0

    def test_project_difficulty_enum(self):
        from prep_agent.models import ProjectDifficulty

        assert ProjectDifficulty.starter.value == "starter"
        assert ProjectDifficulty.advanced.value == "advanced"

    def test_project_status_enum(self):
        from prep_agent.models import ProjectStatus

        assert ProjectStatus.available.value == "available"
        assert ProjectStatus.completed.value == "completed"


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------


class TestTemplateLoading:
    def test_load_all_templates(self, agent):
        templates = agent.load_project_templates()
        assert len(templates) > 0
        for t in templates:
            assert "id" in t
            assert "title" in t
            assert "rubric" in t

    def test_load_templates_by_role(self, agent):
        templates = agent.load_project_templates("ai-platform-engineer")
        assert len(templates) >= 2
        for t in templates:
            assert t["role"] == "ai-platform-engineer"

    def test_load_templates_unknown_role(self, agent):
        templates = agent.load_project_templates("nonexistent-role")
        assert templates == []


# ---------------------------------------------------------------------------
# Project lifecycle
# ---------------------------------------------------------------------------


class TestProjectLifecycle:
    def test_start_project(self, agent, sample_spec):
        entry = agent.start_project(sample_spec)
        assert entry["id"] == "test-project"
        assert entry["status"] == "in_progress"
        assert len(entry["rubric_results"]) == 3

        # Check starter files were created
        proj_dir = agent._projects_dir / "test-project"
        assert (proj_dir / "README.md").exists()
        assert (proj_dir / "main.py").exists()
        assert (proj_dir / "project.json").exists()

    def test_get_user_project(self, agent, sample_spec):
        agent.start_project(sample_spec)
        entry = agent.get_user_project("test-project")
        assert entry is not None
        assert entry["title"] == "Test Project"

    def test_get_nonexistent_project(self, agent):
        assert agent.get_user_project("nope") is None

    def test_list_user_projects(self, agent, sample_spec):
        assert agent.list_user_projects() == []
        agent.start_project(sample_spec)
        projects = agent.list_user_projects()
        assert len(projects) == 1

    def test_check_project_partial(self, agent, sample_spec):
        agent.start_project(sample_spec)
        updated = agent.check_project("test-project", [0, 2])
        assert updated["rubric_score"] == pytest.approx(66.7, abs=0.1)
        assert updated["status"] == "in_progress"
        assert updated["rubric_results"][0]["met"] is True
        assert updated["rubric_results"][1]["met"] is False
        assert updated["rubric_results"][2]["met"] is True

    def test_check_project_complete(self, agent, sample_spec):
        agent.start_project(sample_spec)
        updated = agent.check_project("test-project", [0, 1, 2])
        assert updated["rubric_score"] == 100.0
        assert updated["status"] == "completed"
        assert updated["completed_at"] is not None

    def test_check_nonexistent_project(self, agent):
        result = agent.check_project("nope", [0])
        assert "error" in result

    def test_generate_showcase(self, agent, sample_spec):
        agent.start_project(sample_spec)
        agent.check_project("test-project", [0, 1, 2])
        content = agent.generate_showcase("test-project")
        assert content is not None
        assert "Test Project" in content
        assert "SHOWCASE.md" in str(agent._projects_dir / "test-project" / "SHOWCASE.md")
        assert (agent._projects_dir / "test-project" / "SHOWCASE.md").exists()

    def test_generate_showcase_nonexistent(self, agent):
        assert agent.generate_showcase("nope") is None


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


class TestRanking:
    def test_rank_excludes_completed(self, agent):
        templates = [
            {"id": "p1", "title": "P1", "track_id": "t1", "topics": [], "difficulty": "starter"},
            {"id": "p2", "title": "P2", "track_id": "t2", "topics": [], "difficulty": "starter"},
        ]
        ranked = agent.rank_projects(templates, completed_ids={"p1"})
        assert len(ranked) == 1
        assert ranked[0]["id"] == "p2"

    def test_rank_by_weak_topics(self, agent):
        templates = [
            {"id": "p1", "title": "P1", "track_id": "rag", "topics": ["rag-arch"], "difficulty": "intermediate"},
            {"id": "p2", "title": "P2", "track_id": "sre", "topics": ["monitoring"], "difficulty": "starter"},
        ]
        quiz_history = [
            {"topic": "rag", "score": 2, "total": 10},  # 20% — weak
            {"topic": "sre", "score": 9, "total": 10},   # 90% — strong
        ]
        ranked = agent.rank_projects(templates, quiz_history=quiz_history)
        assert ranked[0]["id"] == "p1"  # rag project first (weak area)

    def test_rank_empty_quiz_history(self, agent):
        templates = [
            {"id": "p1", "title": "P1", "track_id": "t1", "topics": [], "difficulty": "starter"},
        ]
        ranked = agent.rank_projects(templates, quiz_history=[])
        assert len(ranked) == 1


# ---------------------------------------------------------------------------
# Portfolio summary
# ---------------------------------------------------------------------------


class TestPortfolioSummary:
    def test_empty_portfolio(self, agent):
        summary = agent.get_portfolio_summary(quiz_avg=50)
        assert summary["projects_completed"] == 0
        assert summary["projects_in_progress"] == 0
        assert summary["avg_rubric_score"] is None

    def test_portfolio_with_completed_project(self, agent, sample_spec):
        agent.start_project(sample_spec)
        agent.check_project("test-project", [0, 1, 2])
        summary = agent.get_portfolio_summary(quiz_avg=80)
        assert summary["projects_completed"] == 1
        assert summary["avg_rubric_score"] == 100.0
        assert summary["hire_readiness_pct"] > 0
        assert len(summary["skills_demonstrated"]) == 3  # 3 rubric items met


# ---------------------------------------------------------------------------
# ReAct agent behavior
# ---------------------------------------------------------------------------


class TestReActBehavior:
    def test_react_recommends_for_weak_topics(self, agent):
        context = {
            "weak_topics": ["rag", "embeddings"],
            "quiz_history": [],
            "role": "ai-platform-engineer",
        }
        result = agent.run(context)
        assert result["agent"] == "project"
        assert result["result"]["success"] is True

    def test_react_with_no_weak_topics(self, agent):
        context = {
            "weak_topics": [],
            "quiz_history": [],
            "role": "ai-platform-engineer",
        }
        result = agent.run(context)
        assert result["result"]["success"] is True

    def test_react_unknown_role(self, agent):
        context = {
            "weak_topics": [],
            "quiz_history": [],
            "role": "nonexistent-role",
        }
        result = agent.run(context)
        # Should still succeed (with general templates or "no projects" message)
        assert result["result"]["success"] is True
