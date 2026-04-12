"""Tests for the eval CLI command and AgentEvaluator integration."""

import json
import os
import tempfile

from prep_agent.agents.evaluation import AgentEvaluator


class TestAgentEvaluator:
    def test_report_generates_markdown(self):
        evaluator = AgentEvaluator(prep_dir=tempfile.mkdtemp())
        report = evaluator.generate_report()
        assert "# Agent Evaluation Report" in report
        assert "Test Scenarios" in report
        assert "Agent Reliability" in report

    def test_scenarios_all_pass(self):
        evaluator = AgentEvaluator(prep_dir=tempfile.mkdtemp())
        results = evaluator.run_test_scenarios()
        assert len(results) >= 5
        for s in results:
            assert s["passed"], f"Scenario failed: {s['scenario']} — expected {s['expected']}, got {s['actual']}"

    def test_learning_curve_empty(self):
        evaluator = AgentEvaluator(prep_dir=tempfile.mkdtemp())
        curve = evaluator.get_learning_curve()
        assert curve["trend"] == "insufficient_data"
        assert curve["scores_over_time"] == []

    def test_learning_curve_with_data(self):
        tmpdir = tempfile.mkdtemp()
        evaluator = AgentEvaluator(prep_dir=tmpdir)
        # Log some sessions with quiz scores
        evaluator.log_session_quality("quiz", 30, quiz_score=60)
        evaluator.log_session_quality("quiz", 30, quiz_score=70)
        evaluator.log_session_quality("quiz", 30, quiz_score=85)
        evaluator.log_session_quality("quiz", 30, quiz_score=90)

        curve = evaluator.get_learning_curve()
        assert len(curve["scores_over_time"]) == 4
        assert curve["trend"] == "improving"

    def test_reliability_empty(self):
        evaluator = AgentEvaluator(prep_dir=tempfile.mkdtemp())
        rel = evaluator.get_agent_reliability()
        assert rel["total_decisions"] == 0
        assert rel["error_rate"] == 0.0

    def test_decision_logging(self):
        tmpdir = tempfile.mkdtemp()
        evaluator = AgentEvaluator(prep_dir=tmpdir)
        evaluator.log_agent_decision("planner", "compress", "behind schedule", "day 45/60")

        rel = evaluator.get_agent_reliability()
        assert rel["total_decisions"] == 1
        assert "compress" in rel["most_common_actions"]


class TestEvalCommand:
    def test_eval_cmd_registered(self):
        """The eval command should be discoverable in the CLI."""
        from prep_agent.cli import prep
        commands = list(prep.commands.keys())
        assert "eval" in commands

    def test_eval_report_via_click(self):
        """Invoke eval report via Click's test runner."""
        from click.testing import CliRunner
        from prep_agent.commands.eval_cmd import eval_cmd

        runner = CliRunner()
        result = runner.invoke(eval_cmd, ["report"])
        assert result.exit_code == 0
        assert "Agent Evaluation Report" in result.output

    def test_eval_scenarios_via_click(self):
        from click.testing import CliRunner
        from prep_agent.commands.eval_cmd import eval_cmd

        runner = CliRunner()
        result = runner.invoke(eval_cmd, ["scenarios"])
        assert result.exit_code == 0
