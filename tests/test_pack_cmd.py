"""Tests for the `prep pack` command group."""
from click.testing import CliRunner


def _invoke(args: list[str]):
    from prep_agent.commands.pack_cmd import pack_cmd
    runner = CliRunner()
    return runner.invoke(pack_cmd, args)


class TestPackList:
    def test_list_exits_zero(self):
        result = _invoke(["list"])
        assert result.exit_code == 0

    def test_list_shows_sre_pack(self):
        result = _invoke(["list"])
        assert "sre-to-platform-engineer" in result.output
        assert "SRE" in result.output


class TestPackShow:
    def test_show_existing_pack(self):
        result = _invoke(["show", "sre-to-platform-engineer"])
        assert result.exit_code == 0
        assert "SRE" in result.output

    def test_show_unknown_pack_errors(self):
        result = _invoke(["show", "nope"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestPackWeeks:
    def test_weeks_lists_twelve(self):
        result = _invoke(["weeks", "sre-to-platform-engineer"])
        assert result.exit_code == 0
        # 12 weeks, each on its own line starting with a number
        for n in range(1, 13):
            assert f"{n:>2}." in result.output

    def test_weeks_unknown_pack_errors(self):
        result = _invoke(["weeks", "nope"])
        assert result.exit_code == 1


class TestPackWeek:
    def test_week_displays_content(self):
        result = _invoke(["week", "sre-to-platform-engineer", "1"])
        assert result.exit_code == 0
        assert "Platform as a Product" in result.output
        assert "Terms used" in result.output  # every week has the callout

    def test_invalid_week_errors(self):
        result = _invoke(["week", "sre-to-platform-engineer", "99"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_each_week_file_readable(self):
        """Smoke-test that every advertised week actually displays."""
        for n in range(1, 13):
            result = _invoke(["week", "sre-to-platform-engineer", str(n)])
            assert result.exit_code == 0, f"Week {n} failed to display"
            assert len(result.output) > 500, f"Week {n} output suspiciously short"

    def test_quiz_flag_extracts_command(self):
        """--quiz should return exactly one `prep quiz ...` line."""
        result = _invoke(["week", "sre-to-platform-engineer", "1", "--quiz"])
        assert result.exit_code == 0
        line = result.output.strip()
        assert line.startswith("prep quiz")
        assert "--tag" in line

    def test_quiz_flag_differs_per_week(self):
        w1 = _invoke(["week", "sre-to-platform-engineer", "1", "--quiz"]).output.strip()
        w5 = _invoke(["week", "sre-to-platform-engineer", "5", "--quiz"]).output.strip()
        assert w1 != w5
        assert "platform-as-product" in w1
        assert "gitops" in w5


class TestPackStories:
    def test_stories_lists_six_categories(self):
        result = _invoke(["stories", "sre-to-platform-engineer"])
        assert result.exit_code == 0
        # 6 category files: 01..06
        for n in range(1, 7):
            assert f"0{n}-" in result.output


class TestPackMocks:
    def test_mocks_lists_three(self):
        result = _invoke(["mocks", "sre-to-platform-engineer"])
        assert result.exit_code == 0
        assert "mock-1" in result.output
        assert "mock-2" in result.output
        assert "mock-3" in result.output

    def test_mock_by_number(self):
        result = _invoke(["mock", "sre-to-platform-engineer", "1"])
        assert result.exit_code == 0
        assert "IDP" in result.output or "Internal Developer Platform" in result.output

    def test_mock_by_name(self):
        result = _invoke(["mock", "sre-to-platform-engineer", "mock-2-iac-review"])
        assert result.exit_code == 0
        assert "IaC" in result.output

    def test_mock_not_found(self):
        result = _invoke(["mock", "sre-to-platform-engineer", "nonexistent"])
        assert result.exit_code == 1
