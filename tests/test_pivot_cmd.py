"""Tests for prep pivot command — role transition recommender."""

import pytest
from click.testing import CliRunner

from prep_agent.cli import prep
from prep_agent.commands.pivot_cmd import _normalise_role, _score_pivot, _parse_timeline_weeks


class TestNormaliseRole:
    def test_exact_key_passthrough(self):
        assert _normalise_role("software_engineering") == "software_engineering"

    def test_alias_devops_engineer_maps_to_devops_sre(self):
        assert _normalise_role("devops_engineer") == "devops_sre"

    def test_alias_ml_engineer_maps_to_ml_engineering(self):
        assert _normalise_role("ml_engineer") == "ml_engineering"

    def test_alias_cloud_engineer_maps_to_cloud_engineering(self):
        assert _normalise_role("cloud_engineer") == "cloud_engineering"

    def test_alias_sre_maps_to_devops_sre(self):
        assert _normalise_role("sre") == "devops_sre"

    def test_hyphen_normalised(self):
        # hyphens converted to underscores before alias lookup
        result = _normalise_role("cloud-engineer")
        assert result == "cloud_engineering"

    def test_unknown_role_returned_as_is(self):
        assert _normalise_role("unicorn_role") == "unicorn_role"


class TestParseTimelineWeeks:
    def test_range_returns_midpoint(self):
        assert _parse_timeline_weeks("8-10 weeks") == 9.0

    def test_single_value(self):
        assert _parse_timeline_weeks("8 weeks") == 8.0

    def test_empty_defaults(self):
        assert _parse_timeline_weeks("") == 10.0

    def test_no_numbers_defaults(self):
        assert _parse_timeline_weeks("flexible") == 10.0


class TestScorePivot:
    _TEMPLATE = {
        "name": "Test Role",
        "suggested_timeline": "8-10 weeks",
        "bridge_from": {
            "software_engineering": {
                "strengths": ["coding", "CI/CD"],
                "gaps": ["cloud infra", "security", "IaC"],
                "recommended_start": "track-one",
            }
        },
    }

    def test_returns_none_when_no_bridge(self):
        tmpl = {"name": "No Bridge", "bridge_from": {}}
        assert _score_pivot("software_engineering", tmpl, "no-bridge") is None

    def test_returns_none_for_unmatched_role(self):
        result = _score_pivot("data_scientist", self._TEMPLATE, "test-role")
        assert result is None

    def test_returns_dict_for_matched_role(self):
        result = _score_pivot("software_engineering", self._TEMPLATE, "test-role")
        assert result is not None
        assert result["template_id"] == "test-role"
        assert result["template_name"] == "Test Role"

    def test_overlap_pct_calculation(self):
        # 2 strengths, 3 gaps → 2/5 = 40%
        result = _score_pivot("software_engineering", self._TEMPLATE, "test-role")
        assert result["overlap_pct"] == 40

    def test_ramp_weeks_reduced_by_overlap(self):
        result = _score_pivot("software_engineering", self._TEMPLATE, "test-role")
        base = 9.0  # midpoint of 8-10
        # 40% overlap → factor = max(0.4, 1 - 40/200) = max(0.4, 0.8) = 0.8
        expected = round(base * 0.8, 1)
        assert result["ramp_weeks"] == expected

    def test_strengths_and_gaps_present(self):
        result = _score_pivot("software_engineering", self._TEMPLATE, "test-role")
        assert result["strengths"] == ["coding", "CI/CD"]
        assert result["gaps"] == ["cloud infra", "security", "IaC"]

    def test_recommended_start_present(self):
        result = _score_pivot("software_engineering", self._TEMPLATE, "test-role")
        assert result["recommended_start"] == "track-one"

    def test_normalised_key_lookup(self):
        # template uses 'devops_sre' key; query uses 'sre' alias
        tmpl = {
            "name": "Platform",
            "suggested_timeline": "8 weeks",
            "bridge_from": {
                "devops_sre": {
                    "strengths": ["CI/CD"],
                    "gaps": ["IDP"],
                    "recommended_start": "idp-concepts",
                }
            },
        }
        result = _score_pivot("sre", tmpl, "platform-engineer")
        assert result is not None
        assert result["overlap_pct"] == 50  # 1 strength / (1 + 1)

    def test_template_key_normalised_against_query(self):
        # template uses 'devops_engineer'; query uses 'devops_sre'
        # both normalise to devops_sre → should match
        tmpl = {
            "name": "Compliance",
            "suggested_timeline": "8 weeks",
            "bridge_from": {
                "devops_engineer": {
                    "strengths": ["a", "b"],
                    "gaps": ["x"],
                    "recommended_start": "start",
                }
            },
        }
        result = _score_pivot("devops_sre", tmpl, "compliance")
        assert result is not None


class TestPivotCLI:
    def test_pivot_returns_results(self):
        runner = CliRunner()
        result = runner.invoke(prep, ["pivot", "--from", "software_engineering"])
        assert result.exit_code == 0
        assert "Role Pivot Recommendations" in result.output
        assert "software_engineering" in result.output

    def test_pivot_shows_quick_start(self):
        runner = CliRunner()
        result = runner.invoke(prep, ["pivot", "--from", "software_engineering"])
        assert "prep init --template" in result.output

    def test_pivot_top_flag_limits_output(self):
        runner = CliRunner()
        result = runner.invoke(prep, ["pivot", "--from", "software_engineering", "--top", "2"])
        assert result.exit_code == 0
        assert "#1" in result.output
        assert "#2" in result.output
        assert "#3" not in result.output

    def test_pivot_unknown_role_shows_known_roles(self):
        runner = CliRunner()
        result = runner.invoke(prep, ["pivot", "--from", "imaginary_role_xyz"])
        assert result.exit_code == 0
        assert "Known source roles" in result.output

    def test_pivot_devops_sre_matches_multiple_templates(self):
        runner = CliRunner()
        result = runner.invoke(prep, ["pivot", "--from", "devops_sre"])
        assert result.exit_code == 0
        # devops_sre / devops_engineer keys exist in multiple templates
        assert "#1" in result.output
        assert "#2" in result.output

    def test_pivot_cloud_engineering_returns_results(self):
        runner = CliRunner()
        result = runner.invoke(prep, ["pivot", "--from", "cloud_engineering"])
        assert result.exit_code == 0
        assert "Role Pivot Recommendations" in result.output

    def test_pivot_all_flag_shows_unmatched(self):
        runner = CliRunner()
        # Use a role that won't match everything to ensure some unmatched show up
        result = runner.invoke(prep, ["pivot", "--from", "penetration_testing", "--all"])
        assert result.exit_code == 0
