"""Tests for quiz engine."""
import os
import json
import tempfile
import pytest


class TestQuizEngine:
    def _create_temp_prep_dir_with_bank(self):
        tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmpdir, "quiz_banks"), exist_ok=True)
        bank = {
            "topic_id": "test-topic",
            "topic_name": "Test Topic",
            "version": 1,
            "questions": [
                {
                    "id": "q1",
                    "question": "What is 2+2?",
                    "type": "multiple_choice",
                    "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
                    "answer": "B",
                    "explanation": "Basic arithmetic.",
                    "difficulty": "easy",
                },
                {
                    "id": "q2",
                    "question": "Explain the concept of testing.",
                    "type": "open",
                    "key_points": ["Verifies correctness", "Catches regressions", "Improves confidence"],
                    "difficulty": "medium",
                },
            ],
        }
        with open(os.path.join(tmpdir, "quiz_banks", "test-topic.json"), "w") as f:
            json.dump(bank, f)
        return tmpdir

    def test_load_quiz_bank(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        bank = engine.load_quiz_bank("test-topic")
        assert bank is not None
        assert len(bank["questions"]) == 2

    def test_get_questions(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        questions = engine.get_questions("test-topic", num_questions=2)
        assert len(questions) == 2

    def test_get_questions_fewer_available(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        questions = engine.get_questions("test-topic", num_questions=10)
        assert len(questions) == 2  # Only 2 available

    def _create_temp_prep_dir_with_tagged_bank(self):
        """Fixture: bank with tags on some questions, none on others."""
        tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmpdir, "quiz_banks"), exist_ok=True)
        bank = {
            "topic_id": "tagged-topic",
            "title": "Tagged Topic",
            "version": 1,
            "questions": [
                {
                    "id": "t1", "question": "Q1", "type": "multiple_choice",
                    "options": ["A) a", "B) b", "C) c", "D) d"],
                    "answer": "A", "explanation": "x", "difficulty": "easy",
                    "tags": ["gitops", "argocd"],
                },
                {
                    "id": "t2", "question": "Q2", "type": "multiple_choice",
                    "options": ["A) a", "B) b", "C) c", "D) d"],
                    "answer": "B", "explanation": "x", "difficulty": "medium",
                    "tags": ["gitops", "flux"],
                },
                {
                    "id": "t3", "question": "Q3", "type": "open",
                    "key_points": ["p1", "p2"], "difficulty": "hard",
                    "tags": ["policy-as-code"],
                },
                {
                    "id": "t4", "question": "Q4 no tags", "type": "multiple_choice",
                    "options": ["A) a", "B) b", "C) c", "D) d"],
                    "answer": "C", "explanation": "x", "difficulty": "easy",
                },
            ],
        }
        with open(os.path.join(tmpdir, "quiz_banks", "tagged-topic.json"), "w") as f:
            json.dump(bank, f)
        return tmpdir

    def test_get_questions_tag_filter(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_tagged_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        # gitops tag matches 2 questions
        questions = engine.get_questions("tagged-topic", num_questions=10, tag="gitops")
        assert len(questions) == 2
        ids = sorted(q["id"] for q in questions)
        assert ids == ["t1", "t2"]

    def test_get_questions_tag_filter_combined_with_difficulty(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_tagged_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        # gitops + medium = only t2
        questions = engine.get_questions(
            "tagged-topic", num_questions=10, difficulty="medium", tag="gitops"
        )
        assert len(questions) == 1
        assert questions[0]["id"] == "t2"

    def test_get_questions_tag_filter_excludes_untagged(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_tagged_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        # Filter by any tag should exclude t4 (untagged)
        questions = engine.get_questions("tagged-topic", num_questions=10, tag="flux")
        assert len(questions) == 1
        assert questions[0]["id"] == "t2"

    def test_get_questions_tag_filter_no_match(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_tagged_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        questions = engine.get_questions("tagged-topic", num_questions=10, tag="nonexistent")
        assert questions == []

    def test_list_tags(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_tagged_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        tags = engine.list_tags("tagged-topic")
        assert tags == ["argocd", "flux", "gitops", "policy-as-code"]

    def test_validate_bank_rejects_bad_tags(self):
        from prep_agent.core.quiz_engine import QuizEngine
        bank = {
            "topic_id": "x",
            "questions": [{
                "id": "q1", "question": "Q", "type": "multiple_choice",
                "options": ["A) a", "B) b", "C) c", "D) d"],
                "answer": "A", "difficulty": "easy",
                "tags": "not-a-list",  # invalid — should be a list
            }],
        }
        errors = QuizEngine.validate_bank(bank)
        assert any("tags" in e for e in errors)

    def test_missing_quiz_bank(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = tempfile.mkdtemp()
        engine = QuizEngine(prep_dir=tmpdir)
        bank = engine.load_quiz_bank("nonexistent")
        assert bank is None

    def test_log_result(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = tempfile.mkdtemp()
        engine = QuizEngine(prep_dir=tmpdir)
        engine.log_result("Test Topic", 8, 10, ["weak area 1"])
        history = engine.get_history()
        assert len(history) == 1
        assert history[0]["score"] == 8

    def test_generate_ai_quiz_prompt(self):
        from prep_agent.core.quiz_engine import QuizEngine
        engine = QuizEngine()
        prompt = engine.generate_ai_quiz_prompt("OWASP LLM Top 10", num_questions=5)
        assert "OWASP LLM Top 10" in prompt
        assert "5" in prompt

    def test_generate_mock_interview_prompt(self):
        from prep_agent.core.quiz_engine import QuizEngine
        engine = QuizEngine()
        prompt = engine.generate_mock_interview_prompt("Cloud Security Lead")
        assert "Cloud Security Lead" in prompt
        assert "interview" in prompt.lower()

    def test_suggest_review_topics(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = tempfile.mkdtemp()
        engine = QuizEngine(prep_dir=tmpdir)
        # Log some low scores
        engine.log_result("Topic A", 3, 10)
        engine.log_result("Topic B", 9, 10)
        suggestions = engine.suggest_review_topics()
        assert "Topic A" in suggestions
        assert "Topic B" not in suggestions

    # ------------------------------------------------------------------
    # Phase 3 tests — validation, save, generate, import, review
    # ------------------------------------------------------------------

    def test_validate_bank_valid(self):
        from prep_agent.core.quiz_engine import QuizEngine
        bank = {
            "topic_id": "test",
            "questions": [
                {"id": "q1", "question": "Q?", "type": "multiple_choice",
                 "options": ["A) 1", "B) 2", "C) 3", "D) 4"], "answer": "B", "difficulty": "easy"},
                {"id": "q2", "question": "Explain.", "type": "open",
                 "key_points": ["Point 1"], "difficulty": "medium"},
            ],
        }
        errors = QuizEngine.validate_bank(bank)
        assert errors == []

    def test_validate_bank_missing_topic_id(self):
        from prep_agent.core.quiz_engine import QuizEngine
        bank = {"questions": [{"id": "q1", "question": "Q?", "type": "open",
                               "key_points": ["P"], "difficulty": "easy"}]}
        errors = QuizEngine.validate_bank(bank)
        assert any("topic_id" in e for e in errors)

    def test_validate_bank_bad_mc_question(self):
        from prep_agent.core.quiz_engine import QuizEngine
        bank = {
            "topic_id": "test",
            "questions": [
                {"id": "q1", "question": "Q?", "type": "multiple_choice",
                 "options": ["A) 1", "B) 2"], "answer": "E", "difficulty": "easy"},
            ],
        }
        errors = QuizEngine.validate_bank(bank)
        assert len(errors) >= 2  # bad options count + bad answer

    def test_save_bank_creates_file(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = tempfile.mkdtemp()
        engine = QuizEngine(prep_dir=tmpdir)
        bank = {
            "topic_id": "save-test",
            "questions": [
                {"id": "q1", "question": "Q?", "type": "open",
                 "key_points": ["P1"], "difficulty": "easy"},
            ],
        }
        path = engine.save_bank("save-test", bank)
        assert os.path.isfile(path)
        reloaded = engine.load_quiz_bank("save-test")
        assert reloaded is not None
        assert reloaded["topic_id"] == "save-test"

    def test_generate_quiz_bank_prompt_has_schema(self):
        from prep_agent.core.quiz_engine import QuizEngine
        engine = QuizEngine()
        prompt = engine.generate_quiz_bank_prompt("Kubernetes Security", num_questions=10)
        assert "topic_id" in prompt
        assert "multiple_choice" in prompt
        assert "key_points" in prompt
        assert "10" in prompt

    def test_import_local_file(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = tempfile.mkdtemp()
        engine = QuizEngine(prep_dir=tmpdir)
        bank = {
            "topic_id": "import-test",
            "questions": [
                {"id": "q1", "question": "What is a pod?", "type": "multiple_choice",
                 "options": ["A) Container", "B) K8s unit", "C) VM", "D) Process"],
                 "answer": "B", "difficulty": "easy"},
            ],
        }
        import_path = os.path.join(tmpdir, "import-me.json")
        with open(import_path, "w") as f:
            json.dump(bank, f)
        # Validate and save
        errors = engine.validate_bank(bank)
        assert errors == []
        path = engine.save_bank("import-test", bank)
        assert os.path.isfile(path)
        loaded = engine.load_quiz_bank("import-test")
        assert loaded["topic_id"] == "import-test"

    def test_get_review_questions_finds_weak(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = self._create_temp_prep_dir_with_bank()
        engine = QuizEngine(prep_dir=tmpdir)
        # Log a quiz with the exact question text prefix as weak area
        engine.log_result("test-topic", 0, 1, ["What is 2+2?"])
        questions = engine.get_review_questions(num=5)
        assert len(questions) >= 1
        assert any("2+2" in q["question"] for q in questions)

    def test_get_review_questions_empty_history(self):
        from prep_agent.core.quiz_engine import QuizEngine
        tmpdir = tempfile.mkdtemp()
        engine = QuizEngine(prep_dir=tmpdir)
        questions = engine.get_review_questions(num=5)
        assert questions == []
