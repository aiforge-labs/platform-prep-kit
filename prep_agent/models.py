"""Pydantic models -- structured I/O contracts for the platform prep kit.

These models define the data flowing between agent components:
Planner, Tutor, Quiz, Reviewer, and the Orchestrator.

Design principle: Agents communicate via typed contracts, not loose dicts.
This enables validation, serialization, and self-documentation.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Priority(str, Enum):
    """Severity ranking for knowledge gaps.

    Used by the Planner Agent to triage study topics and by the Reviewer
    Agent to flag areas that need urgent attention.
    """

    critical = "critical"
    high = "high"
    moderate = "moderate"


class DayStatus(str, Enum):
    """Lifecycle state of a single study day.

    Tracked by the Orchestrator so it can decide whether to advance,
    retry, or reschedule a day's material.
    """

    pending = "pending"
    done = "done"
    skipped = "skipped"


class TrackStatus(str, Enum):
    """Progress state for a study track (a group of related days).

    The Reviewer Agent inspects track statuses to generate progress
    reports and surface stalled tracks.
    """

    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class ContentStatus(str, Enum):
    """Publication lifecycle for content deliverables (blog, portfolio, etc.).

    Used by the Planner Agent when building and reviewing the content plan.
    """

    not_started = "not_started"
    draft = "draft"
    published = "published"


class SessionType(str, Enum):
    """Category of a study session.

    Determines which agent handles the session: Tutor for study,
    Quiz for quiz, and so on.
    """

    study = "study"
    quiz = "quiz"
    mock_interview = "mock_interview"
    review = "review"


class AIProvider(str, Enum):
    """Supported AI back-ends for assisted study sessions.

    The Orchestrator reads this from config to decide how (or whether)
    to invoke an LLM during sessions.
    """

    none = "none"
    claude_code = "claude_code"
    chatgpt_paste = "chatgpt_paste"
    ollama = "ollama"
    openai_api = "openai_api"
    cursor = "cursor"


class Difficulty(str, Enum):
    """Difficulty tier for quiz questions and study material.

    The Tutor and Quiz agents use this to calibrate content to the
    user's current level.
    """

    easy = "easy"
    medium = "medium"
    hard = "hard"


# ---------------------------------------------------------------------------
# Core configuration models
# ---------------------------------------------------------------------------


class Gap(BaseModel):
    """A knowledge gap identified during fitment analysis.

    Gaps are the primary input to the Planner Agent, which converts them
    into study tracks with estimated time budgets. The optional
    ``knowledge_pack`` and ``quiz_bank`` fields link to supplementary
    material the Tutor and Quiz agents can use.
    """

    id: str
    topic: str
    priority: Priority
    estimated_hours: float
    knowledge_pack: Optional[str] = None
    quiz_bank: Optional[str] = None


class Certification(BaseModel):
    """A certification goal included in the prep plan.

    The Planner Agent schedules study blocks around the target date,
    and the Reviewer Agent tracks readiness based on quiz scores.
    """

    name: str
    target_date: Optional[date] = None
    study_hours: int
    status: str


class ContentItem(BaseModel):
    """A content deliverable (blog post, portfolio piece, etc.).

    Managed by the Planner Agent as part of the weekly content plan.
    The Reviewer Agent checks publication status during weekly reviews.
    """

    type: str = Field(..., description="Content type: blog, portfolio, or linkedin")
    title: str
    target_week: int
    status: ContentStatus = ContentStatus.not_started


class TimelineConfig(BaseModel):
    """Time boundaries and cadence for the entire prep plan.

    Read by the Planner Agent to allocate days across tracks and by
    the Orchestrator to determine which day/week the user is on.
    """

    start_date: date
    end_date: date
    weeks: int
    hours_per_week: float
    study_days: list[str]


class ReminderConfig(BaseModel):
    """Notification preferences for morning and evening nudges.

    The Orchestrator uses this to decide when to surface reminders
    and which delivery method to use.
    """

    enabled: bool = True
    morning_time: str = "07:00"
    evening_time: str = "19:00"
    method: str = "desktop"


class ProfileConfig(BaseModel):
    """User profile metadata.

    Passed to agents so they can personalise prompts and reports.
    """

    name: str
    current_role: str = ""


class TargetConfig(BaseModel):
    """The role and position the user is preparing for.

    Used by the Planner Agent to shape the study plan and by the
    Reviewer Agent to frame progress in terms of job-readiness.
    """

    role: str
    company: str = ""
    job_url: str = ""
    location: str = ""


class AIConfig(BaseModel):
    """AI integration settings.

    Controls which LLM provider (if any) the Orchestrator delegates to
    for assisted study sessions, quiz generation, and reviews.
    """

    provider: AIProvider = AIProvider.none


class PrepConfig(BaseModel):
    """Top-level configuration for a career prep plan.

    This is the root model that the CLI loads from a YAML file. Every
    agent receives a reference to it (or a relevant sub-model) so they
    share a single source of truth for plan parameters.
    """

    version: int = 1
    profile: ProfileConfig
    target: TargetConfig
    timeline: TimelineConfig
    reminders: ReminderConfig = Field(default_factory=ReminderConfig)
    strengths: list[str]
    gaps: list[Gap]
    certifications: list[Certification] = Field(default_factory=list)
    content_plan: list[ContentItem] = Field(default_factory=list)
    ai_integration: AIConfig = Field(default_factory=AIConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> PrepConfig:
        """Load a PrepConfig from a YAML file on disk.

        Uses ``yaml.safe_load`` so only standard YAML types are accepted.
        Pydantic validation runs automatically on the parsed dict.
        """
        import yaml

        path = Path(path)
        with path.open("r") as fh:
            data = yaml.safe_load(fh)
        return cls.model_validate(data)

    def to_yaml(self, path: str | Path) -> None:
        """Serialise this config to a YAML file.

        Produces human-friendly YAML (no flow style, sorted keys) so the
        file remains easy to hand-edit.
        """
        import yaml

        path = Path(path)
        data = self.model_dump(mode="json")
        with path.open("w") as fh:
            yaml.dump(data, fh, default_flow_style=False, sort_keys=False)


# ---------------------------------------------------------------------------
# Study plan models
# ---------------------------------------------------------------------------


class DayEntry(BaseModel):
    """A single day in the study plan.

    The Orchestrator looks up today's DayEntry to determine what the
    user should focus on. After the session the Tutor or Quiz agent
    writes back ``status``, ``notes``, and ``score``.
    """

    day_num: int
    date: date
    week: int
    track_id: str
    topic: str
    morning_focus: str
    evening_focus: str
    is_review_day: bool = False
    is_buffer_day: bool = False
    status: DayStatus = DayStatus.pending
    notes: str = ""
    score: Optional[int] = None


class TrackEntry(BaseModel):
    """A study track -- a logical grouping of consecutive days.

    Tracks map 1-to-1 with knowledge gaps. The Planner Agent creates
    them and the Reviewer Agent rolls up per-day results into track-level
    confidence ratings.
    """

    id: str
    name: str
    start_day: int
    end_day: int
    status: TrackStatus = TrackStatus.not_started
    confidence: Optional[str] = None


class Milestone(BaseModel):
    """A notable checkpoint in the study plan.

    Milestones give the Reviewer Agent natural points to generate
    progress summaries and the user visible goals to work towards.
    """

    day: int
    description: str


class StudyPlan(BaseModel):
    """The complete study plan generated by the Planner Agent.

    Contains every day, track, and milestone for the entire prep
    timeline. The Orchestrator iterates over ``days`` to drive the
    daily loop, while the Reviewer Agent uses ``tracks`` and
    ``milestones`` for higher-level reporting.
    """

    total_days: int
    total_weeks: int
    hours_per_day: float
    days: list[DayEntry]
    tracks: list[TrackEntry]
    milestones: list[Milestone]


# ---------------------------------------------------------------------------
# Fitment analysis models
# ---------------------------------------------------------------------------


class SkillMatch(BaseModel):
    """Skill-level fitment between the user and the target role.

    Produced by the fitment analysis step and consumed by the Planner
    Agent to identify which skills need study time allocated.
    """

    matched: list[str]
    missing: list[str]
    bonus: list[str]


class ExperienceMatch(BaseModel):
    """Years-of-experience comparison.

    A simple quantitative signal the Reviewer Agent can include in
    readiness reports.
    """

    required_years: int
    actual_years: int
    score: float


class CertMatch(BaseModel):
    """Certification fitment -- what the role wants vs. what the user has.

    The Planner Agent uses the ``gap`` list to schedule certification
    study blocks.
    """

    required: list[str]
    have: list[str]
    gap: list[str]


class StrengthItem(BaseModel):
    """A single strength identified during fitment analysis.

    Strengths are surfaced in the FitmentReport so agents can leverage
    them (e.g., the Tutor skips topics the user already masters).
    """

    area: str
    score: float
    evidence: str = ""


class GapItem(BaseModel):
    """A single gap identified during fitment analysis.

    Richer than ``Gap`` -- includes a numeric score and a recommendation.
    The Planner Agent converts high-priority GapItems into ``Gap``
    entries in the PrepConfig.
    """

    area: str
    score: float
    priority: Priority
    recommendation: str = ""
    estimated_hours: float = 0


class FitmentReport(BaseModel):
    """Complete fitment analysis output.

    Generated once (or refreshed periodically) and shared with all
    agents. The Planner uses it to build the study plan, the Reviewer
    to benchmark progress, and the Tutor to calibrate difficulty.
    """

    overall_score: int
    strengths: list[StrengthItem]
    gaps: list[GapItem]
    experience_match: ExperienceMatch
    certification_match: CertMatch
    skills_match: SkillMatch


# ---------------------------------------------------------------------------
# Agent communication models
# ---------------------------------------------------------------------------


class AgentMessage(BaseModel):
    """A single message passed between agents or between an agent and the user.

    This is the fundamental communication primitive in the multi-agent
    architecture. The Orchestrator routes messages based on ``role``,
    and agents append to a shared message history to maintain context.
    """

    role: str = Field(
        ...,
        description="Origin agent: planner, tutor, quiz, reviewer, orchestrator, or user",
    )
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)


class StudySessionRequest(BaseModel):
    """Request from Orchestrator to Tutor Agent.

    The Orchestrator observes the user's state and constructs this request
    to tell the Tutor Agent what to teach. This is the 'Act' step in the
    ReAct loop.
    """

    topic: str
    session_type: SessionType
    user_strengths: list[str] = Field(default_factory=list)
    prior_knowledge: str = ""
    difficulty: Difficulty = Difficulty.medium


class QuizQuestion(BaseModel):
    """A single quiz question generated by the Quiz Agent.

    Supports both multiple-choice and open-ended formats. The
    ``key_points`` and ``explanation`` fields let the Tutor Agent
    provide post-quiz review without a second LLM call.
    """

    id: str
    question: str
    type: str = Field(
        ..., description="Question format: multiple_choice or open"
    )
    options: list[str] = Field(default_factory=list)
    answer: str = ""
    key_points: list[str] = Field(default_factory=list)
    explanation: str = ""
    difficulty: Difficulty = Difficulty.medium


class StudySessionResponse(BaseModel):
    """Response from the Tutor Agent back to the Orchestrator.

    Contains the teaching content, optional quiz questions, and a
    suggestion for what to study next. The Orchestrator may forward
    ``suggested_next`` to the Planner for re-prioritisation.
    """

    topic: str
    session_type: SessionType
    content: str
    questions: list[QuizQuestion] = Field(default_factory=list)
    key_takeaways: list[str] = Field(default_factory=list)
    suggested_next: str = ""


class QuizResult(BaseModel):
    """Outcome of a quiz session, produced by the Quiz Agent.

    The Reviewer Agent aggregates these over time to identify weak
    areas and the Orchestrator uses the score to decide whether to
    advance or revisit a topic.
    """

    topic: str
    score: int
    total: int
    answers: list[dict] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class ReviewReport(BaseModel):
    """Periodic progress report generated by the Reviewer Agent.

    The Orchestrator presents this to the user and may also feed it
    back to the Planner Agent to trigger plan adjustments (e.g.,
    reallocating buffer days to weak topics).
    """

    current_day: int
    total_days: int
    progress_pct: float
    streak: int
    strong_topics: list[str]
    weak_topics: list[str]
    recommendations: list[str]
    next_focus: str = ""


# ---------------------------------------------------------------------------
# Progress / tracker state
# ---------------------------------------------------------------------------


class TrackerState(BaseModel):
    """Complete snapshot of the user's progress at a point in time.

    This is the central state object that the Orchestrator maintains.
    It is loaded at startup, mutated during sessions, and persisted
    after each interaction. Every agent can read it (via the
    Orchestrator) to make context-aware decisions.
    """

    current_day: int
    total_days: int
    current_week: int
    total_weeks: int
    start_date: date
    today_topic: str = ""
    today_track: str = ""
    morning_focus: str = ""
    evening_focus: str = ""
    streak: int = 0
    progress_pct: float = 0
    days: list[DayEntry] = Field(default_factory=list)
    tracks: list[TrackEntry] = Field(default_factory=list)
    content: list[ContentItem] = Field(default_factory=list)
    quiz_history: list[QuizResult] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Project / portfolio models
# ---------------------------------------------------------------------------


class ProjectDifficulty(str, Enum):
    """Difficulty tier for hands-on projects."""

    starter = "starter"
    intermediate = "intermediate"
    advanced = "advanced"


class ProjectStatus(str, Enum):
    """Lifecycle state of a hands-on project."""

    available = "available"
    in_progress = "in_progress"
    completed = "completed"


class RubricItem(BaseModel):
    """A single checklist item in a project evaluation rubric."""

    description: str
    met: bool = False


class ProjectSpec(BaseModel):
    """A hands-on project template that maps to a skill gap.

    The ProjectAgent uses these specs to recommend, scaffold, and
    evaluate portfolio projects. Each spec links to one or more
    tracks/topics from the study plan.
    """

    id: str
    title: str
    description: str
    track_id: str = Field(..., description="Study track this project maps to")
    topics: list[str] = Field(default_factory=list, description="Topic IDs this project covers")
    difficulty: ProjectDifficulty = ProjectDifficulty.intermediate
    estimated_hours: float = 8
    skills_demonstrated: list[str] = Field(default_factory=list)
    rubric: list[RubricItem] = Field(default_factory=list)
    starter_files: dict[str, str] = Field(
        default_factory=dict,
        description="Filename → content template for scaffolding",
    )
    resources: list[str] = Field(default_factory=list, description="Reference URLs or notes")


class ProjectEntry(BaseModel):
    """Runtime state of a project the user has started or completed.

    Stored in ~/.prep/projects/<id>/project.json.
    """

    id: str
    spec_id: str
    title: str
    status: ProjectStatus = ProjectStatus.in_progress
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    rubric_results: list[RubricItem] = Field(default_factory=list)
    rubric_score: Optional[float] = None
    showcase_path: Optional[str] = None
    notes: str = ""


class PortfolioSummary(BaseModel):
    """Aggregated portfolio metrics for the dashboard."""

    projects_completed: int = 0
    projects_in_progress: int = 0
    total_projects_available: int = 0
    skills_demonstrated: list[str] = Field(default_factory=list)
    avg_rubric_score: Optional[float] = None
    hire_readiness_pct: float = 0


# ---------------------------------------------------------------------------
# Boundary adapters
# ---------------------------------------------------------------------------


def validate_config_dict(config_dict: dict) -> tuple[PrepConfig | None, list[str]]:
    """Try to validate a raw config dict against PrepConfig.

    This is a boundary adapter — it does NOT replace core/config.py's
    ``validate_config()``.  It adds Pydantic-level validation on top.

    Returns:
        ``(PrepConfig instance, [])`` on success, or
        ``(None, [error strings])`` on failure.
    """
    from pydantic import ValidationError

    try:
        pc = PrepConfig.model_validate(config_dict)
        return pc, []
    except ValidationError as exc:
        errors = [
            f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in exc.errors()
        ]
        return None, errors
