"""Quiz engine -- local and AI-assisted quizzes for career prep."""
import json
import os
import random
from datetime import datetime


class QuizEngine:
    """Manages quiz banks, runs interactive quizzes, and tracks history."""

    def __init__(self, prep_dir: str | None = None):
        self.prep_dir = prep_dir or os.path.expanduser("~/.prep")
        self.history_path = os.path.join(self.prep_dir, "quiz-history.json")

    def load_quiz_bank(self, topic_id: str) -> dict | None:
        """Load quiz bank from built-in banks or user's local banks.

        Search order:
        1. Package quiz_banks/ directory (shipped with prep-agent)
        2. User's ~/.prep/quiz_banks/
        Returns None if not found.
        """
        # Package-level quiz banks (project root quiz_banks/)
        package_dir = os.path.join(os.path.dirname(__file__), "..", "..", "quiz_banks")
        package_path = os.path.join(package_dir, f"{topic_id}.json")
        if os.path.isfile(package_path):
            return self._read_bank(package_path)

        # User-level quiz banks
        user_path = os.path.join(self.prep_dir, "quiz_banks", f"{topic_id}.json")
        if os.path.isfile(user_path):
            return self._read_bank(user_path)

        return None

    def get_questions(
        self,
        topic_id: str,
        num_questions: int = 5,
        difficulty: str | None = None,
    ) -> list[dict]:
        """Get quiz questions for a topic. Mix difficulties if not specified.

        Args:
            topic_id: Identifier matching a quiz bank filename (without .json).
            num_questions: How many questions to return.
            difficulty: One of 'easy', 'medium', 'hard', or None for mixed.

        Returns:
            List of question dicts, each containing:
            {id, question, type, options (if MC), key_points (if open),
             difficulty, explanation}
        """
        bank = self.load_quiz_bank(topic_id)
        if not bank:
            return []

        questions = bank.get("questions", [])
        if difficulty:
            questions = [q for q in questions if q.get("difficulty") == difficulty]

        if len(questions) <= num_questions:
            selected = list(questions)
        else:
            selected = random.sample(questions, num_questions)

        random.shuffle(selected)
        return selected

    def run_interactive_quiz(self, questions: list[dict]) -> dict:
        """Run an interactive terminal quiz session.

        For multiple choice: accept A/B/C/D input.
        For open questions: show question, accept free text, show key points,
        ask self-rating 1-5.

        Returns:
            {topic, score, total, answers: [{question, user_answer, correct,
             points}], weak_areas}
        """
        answers: list[dict] = []
        score = 0
        total = len(questions)

        for i, q in enumerate(questions, 1):
            print(f"\n--- Question {i}/{total} [{q.get('difficulty', '?')}] ---")
            print(q["question"])

            if q.get("type") == "multiple_choice":
                for opt in q.get("options", []):
                    print(f"  {opt}")
                user_answer = input("\nYour answer (A/B/C/D): ").strip().upper()
                correct_answer = q.get("answer", "").upper()
                is_correct = user_answer == correct_answer
                points = 1 if is_correct else 0
                score += points

                if is_correct:
                    print("Correct!")
                else:
                    print(f"Incorrect. The answer is {correct_answer}.")
                if q.get("explanation"):
                    print(f"Explanation: {q['explanation']}")

                answers.append({
                    "question": q["question"],
                    "user_answer": user_answer,
                    "correct": is_correct,
                    "points": points,
                })

            elif q.get("type") == "open":
                user_answer = input("\nYour answer: ").strip()
                print("\nKey points to cover:")
                for kp in q.get("key_points", []):
                    print(f"  - {kp}")
                rating_str = input("Rate yourself 1-5 (5 = nailed it): ").strip()
                try:
                    rating = max(1, min(5, int(rating_str)))
                except ValueError:
                    rating = 3
                points = rating
                score += points

                answers.append({
                    "question": q["question"],
                    "user_answer": user_answer,
                    "correct": rating >= 4,
                    "points": points,
                })
            else:
                # Unknown type -- treat as open
                user_answer = input("\nYour answer: ").strip()
                answers.append({
                    "question": q["question"],
                    "user_answer": user_answer,
                    "correct": None,
                    "points": 0,
                })

        # Identify weak areas: incorrect or low-rated answers
        weak_areas = [
            a["question"][:80]
            for a in answers
            if not a.get("correct")
        ]

        # Normalize score to percentage-friendly ints for MC-only quizzes
        mc_count = sum(
            1 for q in questions if q.get("type") == "multiple_choice"
        )
        open_count = total - mc_count

        result = {
            "topic": questions[0].get("topic_id", "unknown") if questions else "unknown",
            "score": score,
            "total": total if open_count == 0 else total * 5,
            "answers": answers,
            "weak_areas": weak_areas,
        }

        print(f"\n=== Results: {score}/{result['total']} ===")
        if weak_areas:
            print("Areas to review:")
            for wa in weak_areas:
                print(f"  - {wa}")

        return result

    def log_result(
        self,
        topic: str,
        score: int,
        total: int,
        weak_areas: list[str] | None = None,
    ) -> None:
        """Record quiz result to history."""
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        history = self._load_history()
        history.append({
            "topic": topic,
            "score": score,
            "total": total,
            "percentage": round(score / total * 100, 1) if total else 0,
            "weak_areas": weak_areas or [],
            "timestamp": datetime.now().isoformat(),
        })
        with open(self.history_path, "w") as f:
            json.dump(history, f, indent=2)

    def get_history(
        self, topic: str | None = None, limit: int = 20
    ) -> list[dict]:
        """Get quiz history, optionally filtered by topic."""
        history = self._load_history()
        if topic:
            topic_lower = topic.lower()
            history = [
                h for h in history if h.get("topic", "").lower() == topic_lower
            ]
        # Most recent first
        history.sort(key=lambda h: h.get("timestamp", ""), reverse=True)
        return history[:limit]

    def suggest_review_topics(self) -> list[str]:
        """Suggest topics to revisit based on low/declining scores.

        Returns topics where:
        - Average score < 60%, or
        - Score is declining (last result < previous result)
        """
        history = self._load_history()
        if not history:
            return []

        # Group by topic
        by_topic: dict[str, list[dict]] = {}
        for entry in history:
            topic = entry.get("topic", "unknown")
            by_topic.setdefault(topic, []).append(entry)

        suggestions: list[str] = []
        for topic, entries in by_topic.items():
            entries.sort(key=lambda e: e.get("timestamp", ""))
            percentages = [e.get("percentage", 0) for e in entries]

            avg = sum(percentages) / len(percentages)
            if avg < 60:
                suggestions.append(topic)
                continue

            # Check declining trend (last two attempts)
            if len(percentages) >= 2 and percentages[-1] < percentages[-2]:
                suggestions.append(topic)

        return suggestions

    def generate_ai_quiz_prompt(
        self,
        topic: str,
        studied_notes: str | None = None,
        num_questions: int = 5,
    ) -> str:
        """Generate a prompt for AI to quiz the user.

        Can be copy-pasted into any AI chat. Includes topic context,
        what the user has studied, desired format, and difficulty mix.
        """
        notes_section = ""
        if studied_notes:
            notes_section = (
                f"\n\nHere is what I have studied so far:\n"
                f"---\n{studied_notes}\n---\n"
            )

        return f"""I want you to quiz me on: {topic}
{notes_section}
Please generate {num_questions} questions with a mix of difficulties (easy, medium, hard).

Format:
- Mix of multiple-choice and open-ended questions
- For multiple choice: provide 4 options (A-D) and wait for my answer before revealing the correct one
- For open-ended: ask the question, wait for my answer, then evaluate my response
- After each answer, provide a brief explanation
- At the end, summarize my score and suggest areas to review

Ask one question at a time and wait for my response before proceeding."""

    def generate_mock_interview_prompt(
        self,
        target_role: str,
        target_company: str | None = None,
        focus: str = "technical",
    ) -> str:
        """Generate a mock interview prompt for AI.

        Args:
            target_role: The role being prepared for.
            target_company: Optional company name for tailored questions.
            focus: One of 'technical', 'leadership', 'behavioral', 'system-design'.
        """
        company_context = ""
        if target_company:
            company_context = (
                f" at {target_company}. Tailor questions to what this "
                f"company values and the challenges they likely face"
            )

        focus_instructions = {
            "technical": (
                "Focus on technical depth: architecture decisions, "
                "trade-offs, debugging scenarios, and system design."
            ),
            "leadership": (
                "Focus on leadership: team management, conflict resolution, "
                "stakeholder communication, and strategic thinking."
            ),
            "behavioral": (
                "Focus on behavioral questions: past experiences, "
                "challenges overcome, teamwork, and decision-making using "
                "the STAR format."
            ),
            "system-design": (
                "Focus on system design: scalability, reliability, "
                "data modeling, API design, and infrastructure decisions."
            ),
        }

        focus_text = focus_instructions.get(focus, focus_instructions["technical"])

        return f"""You are an experienced interviewer conducting a mock interview for a {target_role} position{company_context}.

{focus_text}

Instructions:
- Ask 5-7 questions, one at a time
- Wait for my response before asking the next question
- After each answer, provide brief feedback on what was strong and what could be improved
- Use follow-up questions to probe deeper when my answer is surface-level
- At the end, provide an overall assessment with:
  - Strengths demonstrated
  - Areas for improvement
  - Specific suggestions for better answers
  - An overall readiness rating (1-5)

Begin with a brief introduction and your first question."""

    # -- Private helpers --

    def _read_bank(self, path: str) -> dict | None:
        """Read and parse a quiz bank JSON file."""
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _load_history(self) -> list[dict]:
        """Load quiz history from disk."""
        if not os.path.isfile(self.history_path):
            return []
        try:
            with open(self.history_path) as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    # ------------------------------------------------------------------
    # Validation & persistence
    # ------------------------------------------------------------------

    @staticmethod
    def validate_bank(data: dict) -> list[str]:
        """Validate a quiz bank dict against the expected schema.

        Returns a list of error strings. Empty list means valid.
        """
        errors: list[str] = []
        if not isinstance(data, dict):
            return ["Root must be a JSON object"]

        if "topic_id" not in data:
            errors.append("Missing required field: topic_id")

        questions = data.get("questions")
        if not isinstance(questions, list) or len(questions) == 0:
            errors.append("'questions' must be a non-empty array")
            return errors

        valid_types = {"multiple_choice", "open"}
        valid_diffs = {"easy", "medium", "hard"}

        for i, q in enumerate(questions):
            prefix = f"questions[{i}]"
            for field in ("id", "question", "type", "difficulty"):
                if field not in q:
                    errors.append(f"{prefix}: missing '{field}'")

            qtype = q.get("type")
            if qtype and qtype not in valid_types:
                errors.append(f"{prefix}: type must be one of {valid_types}")

            diff = q.get("difficulty")
            if diff and diff not in valid_diffs:
                errors.append(f"{prefix}: difficulty must be one of {valid_diffs}")

            if qtype == "multiple_choice":
                opts = q.get("options")
                if not isinstance(opts, list) or len(opts) != 4:
                    errors.append(f"{prefix}: MC question must have exactly 4 options")
                ans = q.get("answer")
                if ans not in ("A", "B", "C", "D"):
                    errors.append(f"{prefix}: MC answer must be A, B, C, or D")

            if qtype == "open":
                kp = q.get("key_points")
                if not isinstance(kp, list) or len(kp) == 0:
                    errors.append(f"{prefix}: open question must have non-empty key_points")

        return errors

    def save_bank(self, topic_id: str, data: dict) -> str:
        """Validate and save a quiz bank to the user's local directory.

        Returns the file path. Raises ValueError if validation fails.
        """
        errors = self.validate_bank(data)
        if errors:
            raise ValueError(f"Invalid quiz bank: {'; '.join(errors)}")

        user_dir = os.path.join(self.prep_dir, "quiz_banks")
        os.makedirs(user_dir, exist_ok=True)
        path = os.path.join(user_dir, f"{topic_id}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    # ------------------------------------------------------------------
    # Generation prompt
    # ------------------------------------------------------------------

    def generate_quiz_bank_prompt(self, topic: str, num_questions: int = 10) -> str:
        """Build a prompt that asks an LLM to produce a quiz bank in valid JSON."""
        return f"""Generate a quiz bank about "{topic}" with exactly {num_questions} questions.

Return ONLY valid JSON (no markdown fences, no explanation) matching this schema:

{{
  "topic_id": "{topic.lower().replace(' ', '-')}",
  "title": "{topic}",
  "version": 1,
  "questions": [
    {{
      "id": "q01",
      "question": "Your question here?",
      "type": "multiple_choice",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "B",
      "explanation": "Why B is correct.",
      "difficulty": "medium"
    }},
    {{
      "id": "q02",
      "question": "Explain concept X.",
      "type": "open",
      "key_points": ["Point 1", "Point 2", "Point 3"],
      "difficulty": "hard"
    }}
  ]
}}

Requirements:
- Mix of multiple_choice and open questions
- Mix of easy, medium, and hard difficulties
- Each question must have: id, question, type, difficulty
- MC questions must have: options (exactly 4, prefixed A-D), answer (A/B/C/D), explanation
- Open questions must have: key_points (non-empty list)
- Questions should be practical and interview-relevant
- Return ONLY the JSON object, nothing else"""

    # ------------------------------------------------------------------
    # Spaced repetition
    # ------------------------------------------------------------------

    def get_review_questions(self, num: int = 5) -> list[dict]:
        """Find questions the user previously got wrong for spaced review.

        Searches quiz history for weak areas, then matches them back to
        quiz bank questions by text prefix.
        """
        history = self._load_history()
        if not history:
            return []

        # Collect weak areas with frequency counts
        weak_counts: dict[str, int] = {}
        for entry in history:
            for wa in entry.get("weak_areas", []):
                wa_key = wa.strip()[:60]
                weak_counts[wa_key] = weak_counts.get(wa_key, 0) + 1

        if not weak_counts:
            return []

        # Load all available quiz banks
        all_questions: list[dict] = []
        bank_dirs = [
            os.path.join(os.path.dirname(__file__), "..", "..", "quiz_banks"),
            os.path.join(self.prep_dir, "quiz_banks"),
        ]
        seen_ids: set[str] = set()
        for bank_dir in bank_dirs:
            if not os.path.isdir(bank_dir):
                continue
            for fname in os.listdir(bank_dir):
                if not fname.endswith(".json"):
                    continue
                bank = self._read_bank(os.path.join(bank_dir, fname))
                if bank:
                    for q in bank.get("questions", []):
                        qid = q.get("id", "")
                        if qid not in seen_ids:
                            seen_ids.add(qid)
                            all_questions.append(q)

        # Match weak areas to questions by prefix
        matched: list[tuple[int, dict]] = []
        for q in all_questions:
            q_text = q.get("question", "")[:60]
            for wa_key, count in weak_counts.items():
                if q_text and wa_key and q_text.startswith(wa_key[:40]):
                    matched.append((count, q))
                    break

        # Sort: most times wrong first
        matched.sort(key=lambda x: x[0], reverse=True)

        # Deduplicate and limit
        result: list[dict] = []
        result_ids: set[str] = set()
        for _, q in matched:
            qid = q.get("id", "")
            if qid not in result_ids:
                result_ids.add(qid)
                result.append(q)
            if len(result) >= num:
                break

        return result
