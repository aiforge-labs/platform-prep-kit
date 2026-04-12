"""AI bridge -- provider-agnostic AI integration for study sessions."""
import json
import os
import sys
from datetime import datetime


class AIBridge:
    """Provider-agnostic AI integration for study sessions.

    Supports multiple AI backends (or none at all) for generating
    study sessions, prompts, and interview prep.
    """

    PROVIDERS = ["none", "claude-code", "chatgpt-paste", "ollama", "openai-api", "cursor"]

    def __init__(self, config: dict, prep_dir: str | None = None):
        self.config = config
        self.prep_dir = prep_dir or os.path.expanduser("~/.prep")
        self.provider: str = config.get("ai_integration", {}).get("provider", "none")

    def generate_session(
        self,
        topic: str,
        tracker_data: dict,
        notes: str | None = None,
    ) -> str:
        """Generate a study session based on configured provider.

        Returns instructions or a prompt for the user, depending on
        which provider is configured.
        """
        if self.provider == "none":
            return self._standalone_session(topic, notes)

        elif self.provider == "claude-code":
            self._update_claude_md(topic, tracker_data, notes)
            return "Claude Code files updated. Start Claude Code and say 'continue my prep'."

        elif self.provider == "chatgpt-paste":
            prompt = self._build_study_prompt(topic, tracker_data, notes)
            copied = self._try_copy_clipboard(prompt)
            suffix = " (copied to clipboard)" if copied else ""
            return f"{prompt}\n\n---\nPaste the above into ChatGPT to start your session.{suffix}"

        elif self.provider == "ollama":
            return self._ollama_session(topic, notes)

        else:
            # Generic fallback: just build the prompt
            prompt = self._build_study_prompt(topic, tracker_data, notes)
            return prompt

    def _standalone_session(self, topic: str, notes: str | None = None) -> str:
        """No AI: return a structured study guide from knowledge packs.

        Checks if a knowledge pack exists for the topic and returns a
        structured study guide with sections, resources, and self-test
        questions.
        """
        from ..__init__ import __name__ as _  # noqa: avoid circular at module level
        from ..core.knowledge import KnowledgeBase

        kb = KnowledgeBase(self.prep_dir)
        existing_notes = kb.get_topic(topic)

        sections: list[str] = [
            f"# Study Session: {topic}",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]

        if existing_notes:
            sections.append("## Your Notes")
            sections.append(existing_notes[:2000])
            sections.append("")

        sections.extend([
            "## Study Plan",
            f"1. Review fundamentals of {topic}",
            f"2. Identify key concepts and terminology",
            f"3. Practice explaining {topic} to someone unfamiliar",
            f"4. Work through example scenarios",
            "",
            "## Self-Test Questions",
            f"- What are the core principles of {topic}?",
            f"- How does {topic} apply to your target role?",
            f"- What are common misconceptions about {topic}?",
            f"- Can you explain {topic} in 2 minutes to a non-expert?",
            "",
            "## Next Steps",
            "- [ ] Complete self-test above",
            "- [ ] Add notes on areas of uncertainty",
            "- [ ] Schedule a quiz to test retention",
        ])

        if notes:
            sections.extend([
                "",
                "## Additional Context",
                notes[:1000],
            ])

        return "\n".join(sections)

    def _build_study_prompt(
        self,
        topic: str,
        tracker_data: dict,
        notes: str | None = None,
    ) -> str:
        """Build a study session prompt for any AI.

        Format: teach -> discuss -> quiz.
        """
        target_role = tracker_data.get("target_role", "your target role")
        current_level = tracker_data.get("current_level", "experienced professional")
        weak_areas = tracker_data.get("weak_areas", [])
        completed_topics = tracker_data.get("completed_topics", [])

        notes_section = ""
        if notes:
            notes_section = (
                f"\n\nHere is what I have studied so far on this topic:\n"
                f"---\n{notes[:3000]}\n---"
            )

        weak_section = ""
        if weak_areas:
            weak_section = (
                f"\n\nI have identified these as weak areas: "
                f"{', '.join(weak_areas[:5])}"
            )

        # Quiz history context for this topic
        quiz_section = ""
        quiz_history = tracker_data.get("quiz_history", [])
        topic_quizzes = [
            q for q in quiz_history
            if q.get("topic", "").lower() == topic.lower()
        ][-3:]  # last 3 attempts
        if topic_quizzes:
            scores = [f"{q.get('score', 0)}/{q.get('total', 0)}" for q in topic_quizzes]
            quiz_section = f"\n\nMy recent quiz scores on this topic: {', '.join(scores)}"
            all_weak = []
            for q in topic_quizzes:
                all_weak.extend(q.get("weak_areas", []))
            if all_weak:
                quiz_section += f"\nSpecific areas I got wrong: {'; '.join(all_weak[:5])}"

        # Teaching approach hint
        approach = tracker_data.get("approach", "")
        approach_section = ""
        if approach:
            approach_map = {
                "basics_first": "I'm new to this topic — start from fundamentals.",
                "targeted_review": "I've studied this but scored poorly — focus on my weak spots.",
                "deep_dive": "I have a solid foundation — go deep on advanced concepts.",
                "analogy": "I have related experience — use analogies to bridge my knowledge.",
            }
            hint = approach_map.get(approach, "")
            if hint:
                approach_section = f"\n\nTeaching preference: {hint}"

        return f"""You are a career prep coach helping me study for a {target_role} position.
I am a {current_level}.

Today's topic: {topic}
{notes_section}{weak_section}{quiz_section}{approach_section}

Session format:
1. TEACH (5 min): Give me a concise overview of the key concepts. Focus on what an interviewer would expect me to know.
2. DISCUSS (10 min): Ask me probing questions to test my understanding. Challenge my assumptions.
3. QUIZ (5 min): Give me 3-5 targeted questions mixing conceptual and applied knowledge.

After the quiz, provide:
- Score and areas to strengthen
- 2-3 specific resources to review
- One key takeaway to remember

Start with the TEACH phase now."""

    def _update_claude_md(
        self,
        topic: str,
        tracker_data: dict,
        notes: str | None = None,
    ) -> None:
        """Generate/update CLAUDE.md for Claude Code auto-resume.

        Writes to ~/.prep/.ai/claude-code/CLAUDE.md with current state
        and session instructions.
        """
        claude_dir = os.path.join(self.prep_dir, ".ai", "claude-code")
        os.makedirs(claude_dir, exist_ok=True)
        claude_md_path = os.path.join(claude_dir, "CLAUDE.md")

        content = self.generate_claude_md(self.config, tracker_data)

        # Add current session info
        content += f"\n\n## Current Session\n"
        content += f"- **Topic:** {topic}\n"
        content += f"- **Started:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        if notes:
            content += f"\n### Study Notes\n{notes[:2000]}\n"

        with open(claude_md_path, "w") as f:
            f.write(content)

    def _ollama_session(self, topic: str, notes: str | None = None) -> str:
        """Try to call local Ollama API. Fall back to prompt generation."""
        try:
            import urllib.request

            ai_cfg = self.config.get("ai_integration", {})
            model = ai_cfg.get("ollama_model", "llama3")
            base_url = ai_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")

            prompt = (
                f"You are a study coach. Help me learn about: {topic}\n\n"
                f"Start with a brief overview of key concepts, then ask me "
                f"questions to test understanding."
            )
            if notes:
                prompt += f"\n\nContext from my notes:\n{notes[:2000]}"

            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
            }).encode()

            req = urllib.request.Request(
                f"{base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                return result.get("response", "No response from Ollama.")

        except Exception:
            # Ollama not available -- fall back to prompt
            return (
                f"Could not connect to Ollama at {base_url} (is it running?).\n\n"
                f"Here is a prompt you can use with any AI instead:\n\n"
                f"{self._build_study_prompt(topic, {}, notes)}"
            )

    def _try_copy_clipboard(self, text: str) -> bool:
        """Try to copy text to clipboard. Silent fail if not available."""
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except (ImportError, Exception):
            # Try platform-native fallback on macOS
            if sys.platform == "darwin":
                try:
                    import subprocess
                    process = subprocess.Popen(
                        ["pbcopy"],
                        stdin=subprocess.PIPE,
                    )
                    process.communicate(text.encode("utf-8"))
                    return process.returncode == 0
                except Exception:
                    pass
            return False

    def generate_claude_md(self, config: dict, tracker_data: dict) -> str:
        """Generate CLAUDE.md content for Claude Code integration.

        Template with current state, session format, and file paths.
        Generic -- no company references in the template itself;
        user's config data fills in the specifics.
        """
        target_role = tracker_data.get("target_role", "your target role")
        target_company = tracker_data.get("target_company", "")
        focus_areas = tracker_data.get("focus_areas", [])
        weak_areas = tracker_data.get("weak_areas", [])
        completed = tracker_data.get("completed_topics", [])
        prep_dir = config.get("prep_dir", self.prep_dir)

        company_line = f"- **Target Company:** {target_company}" if target_company else ""
        focus_section = ""
        if focus_areas:
            focus_section = "- **Focus Areas:** " + ", ".join(focus_areas)
        weak_section = ""
        if weak_areas:
            weak_section = "- **Weak Areas:** " + ", ".join(weak_areas)
        completed_section = ""
        if completed:
            completed_section = (
                "\n\n## Completed Topics\n"
                + "\n".join(f"- {t}" for t in completed[-10:])
            )

        return f"""# Career Prep Session

## Context
- **Target Role:** {target_role}
{company_line}
{focus_section}
{weak_section}
- **Knowledge Base:** {os.path.join(prep_dir, 'knowledge')}
- **Quiz History:** {os.path.join(prep_dir, 'quiz-history.json')}
{completed_section}

## Session Instructions
When the user says "continue my prep", follow this flow:

1. Check which topic is scheduled for today
2. Review their notes on that topic (in the knowledge directory)
3. Run a teach -> discuss -> quiz session
4. Log results and suggest next steps

## File Paths
- Prep directory: {prep_dir}
- Knowledge notes: {os.path.join(prep_dir, 'knowledge')}/
- Quiz banks: {os.path.join(prep_dir, 'quiz_banks')}/
- Quiz history: {os.path.join(prep_dir, 'quiz-history.json')}
"""
