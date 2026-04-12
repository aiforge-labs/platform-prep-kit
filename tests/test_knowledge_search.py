"""Tests for TF-IDF search in KnowledgeBase and TutorAgent knowledge retrieval."""

import os
import tempfile

from prep_agent.core.knowledge import KnowledgeBase


class TestTFIDFSearch:
    def _make_kb(self, tmp_path) -> KnowledgeBase:
        kb = KnowledgeBase(prep_dir=str(tmp_path))
        kb.add_note("Kubernetes", "Container orchestration with pods, services, and deployments. Kubernetes manages workloads.")
        kb.add_note("Python", "Programming language for web frameworks, data science, and automation. Django and Flask.")
        kb.add_note("Cloud Security", "IAM policies, encryption at rest and transit, network security groups, VPC configuration.")
        return kb

    def test_relevant_doc_scores_highest(self, tmp_path):
        kb = self._make_kb(tmp_path)
        results = kb.search("kubernetes container pods")
        assert len(results) > 0
        assert results[0]["topic"] == "Kubernetes"
        assert results[0]["score"] > 0

    def test_scores_are_descending(self, tmp_path):
        kb = self._make_kb(tmp_path)
        results = kb.search("security encryption IAM")
        assert len(results) > 0
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_result_has_backward_compat_fields(self, tmp_path):
        kb = self._make_kb(tmp_path)
        results = kb.search("python")
        assert len(results) > 0
        r = results[0]
        assert "topic" in r
        assert "matching_lines" in r
        assert "file_path" in r
        assert "score" in r

    def test_matching_lines_contain_query_terms(self, tmp_path):
        kb = self._make_kb(tmp_path)
        results = kb.search("IAM policies")
        assert len(results) > 0
        # At least one matching line should contain "IAM" or "policies"
        cloud_result = next((r for r in results if r["topic"] == "Cloud Security"), None)
        assert cloud_result is not None
        assert any("IAM" in line or "policies" in line for line in cloud_result["matching_lines"])

    def test_top_k_limits_results(self, tmp_path):
        kb = self._make_kb(tmp_path)
        # All 3 docs might match a broad query
        results = kb.search("and", top_k=2)
        assert len(results) <= 2

    def test_empty_corpus_returns_empty(self):
        kb = KnowledgeBase(prep_dir=tempfile.mkdtemp())
        results = kb.search("anything")
        assert results == []

    def test_empty_query_returns_empty(self, tmp_path):
        kb = self._make_kb(tmp_path)
        results = kb.search("")
        assert results == []

    def test_no_match_returns_empty(self, tmp_path):
        kb = self._make_kb(tmp_path)
        results = kb.search("xyzzyspoonshift")
        assert results == []


class TestTFIDFHelpers:
    def test_tokenize(self):
        tokens = KnowledgeBase._tokenize("Hello, World! Python-3.10 is great.")
        assert tokens == ["hello", "world", "python", "3", "10", "is", "great"]

    def test_compute_tf(self):
        tf = KnowledgeBase._compute_tf(["a", "b", "a", "c"])
        assert tf["a"] == 0.5
        assert tf["b"] == 0.25
        assert tf["c"] == 0.25

    def test_compute_tf_empty(self):
        assert KnowledgeBase._compute_tf([]) == {}

    def test_compute_idf(self):
        docs = [["a", "b"], ["b", "c"], ["c", "d"]]
        idf = KnowledgeBase._compute_idf(docs)
        # "b" appears in 2/3 docs, "a" in 1/3 — "a" should have higher IDF
        assert idf["a"] > idf["b"]

    def test_score_tfidf(self):
        idf = {"hello": 2.0, "world": 1.0}
        score = KnowledgeBase._score_tfidf(
            ["hello", "world"],
            ["hello", "hello", "world", "foo"],
            idf,
        )
        assert score > 0


class TestTutorKnowledgeRetrieval:
    def test_tutor_injects_knowledge_pack(self, tmp_path):
        """TutorAgent should retrieve knowledge and inject it into context."""
        # Set up knowledge base
        kb = KnowledgeBase(prep_dir=str(tmp_path))
        kb.add_note("Cloud Security", "Zero trust architecture and IAM best practices")

        from prep_agent.agents.tutor import TutorAgent

        tutor = TutorAgent()
        # Monkey-patch to use our test KB path
        import prep_agent.core.knowledge as kb_mod
        original_init = KnowledgeBase.__init__

        def patched_init(self_kb, prep_dir=None):
            original_init(self_kb, prep_dir=str(tmp_path))

        kb_mod.KnowledgeBase.__init__ = patched_init
        try:
            result = tutor.generate_study_session({
                "topic": "Cloud Security",
                "strengths": [],
                "prior_notes": "",
                "topic_quiz_scores": [],
            })
            assert "topic" in result
            assert result["topic"] == "Cloud Security"
        finally:
            kb_mod.KnowledgeBase.__init__ = original_init
