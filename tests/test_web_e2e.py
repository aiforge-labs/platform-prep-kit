"""End-to-end browser tests for the web UI using Playwright.

These tests start a real uvicorn server on a free port, drive Chromium
headlessly, and assert the user-visible behaviour: nav links, version
badge, page routing, portfolio cards, knowledge link resolution.

Marked as integration so they can be skipped with ``-m "not e2e"`` for
fast unit-only runs.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from urllib.request import urlopen
from urllib.error import URLError

import pytest

playwright_sync = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright, expect  # noqa: E402

pytestmark = pytest.mark.e2e


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server():
    """Start uvicorn on a free port, wait until /health responds, tear down after."""
    port = _free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "prep_agent.web.app:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"

    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            with urlopen(f"{base}/health", timeout=1) as r:
                if r.status == 200:
                    break
        except (URLError, ConnectionError):
            time.sleep(0.2)
    else:
        proc.kill()
        pytest.fail("uvicorn did not become ready within 15s")

    yield base

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture
def page(browser, server):
    ctx = browser.new_context()
    page = ctx.new_page()
    yield page
    ctx.close()


def test_health_endpoint_returns_current_version(server):
    """Smoke check: /health responds with the package version."""
    from prep_agent import __version__

    with urlopen(f"{server}/health") as r:
        body = r.read().decode()
    assert f'"version":"{__version__}"' in body


def test_dashboard_loads_with_version_badge(page, server):
    """Dashboard renders, sidebar shows the version from the package."""
    from prep_agent import __version__

    page.goto(server)
    expect(page).to_have_title("Dashboard - Platform Prep Kit")
    expect(page.locator(".sidebar .version")).to_have_text(f"v{__version__}")


def test_help_page_in_nav_and_loads(page, server):
    """The Help nav link is visible and routes to a populated /help page."""
    page.goto(server)
    help_link = page.locator(".sidebar a[href='/help']")
    expect(help_link).to_be_visible()
    expect(help_link).to_have_text("Help")

    help_link.click()
    page.wait_for_url(f"{server}/help")
    expect(page.locator("h2")).to_contain_text("Help")
    expect(page.locator("body")).to_contain_text("Running locally")
    expect(page.locator("body")).to_contain_text("Contributing")
    expect(page.locator("body")).to_contain_text("Get support")


def test_portfolio_shows_projects(page, server):
    """Portfolio page populates with the configured role's project templates."""
    page.goto(f"{server}/portfolio")
    # Empty-state copy should not appear
    expect(page.locator("body")).not_to_contain_text(
        "No project templates found"
    )


def test_today_study_material_link_resolves(page, server):
    """If a today entry exists, the Study Material link must point at an
    actual knowledge pack slug (not the raw track_id) — regression for
    the /knowledge/interview-prep 404."""
    page.goto(f"{server}/today")
    link = page.locator("a.btn:has-text('Study Material')")
    if link.count() == 0:
        pytest.skip("No active plan / no today entry — nothing to validate")

    href = link.first.get_attribute("href")
    assert href and href.startswith("/knowledge/")
    slug = href.split("/knowledge/")[-1]

    # The slug must actually exist
    resp = page.request.get(f"{server}{href}")
    assert resp.status == 200, f"Study Material link goes to {href} but returns {resp.status}"
    assert slug != "interview-prep", (
        "Today page is still emitting the raw track_id 'interview-prep'; "
        "_find_knowledge_pack() should resolve it to 'interview-frameworks'"
    )


def test_knowledge_hub_lists_packs(page, server):
    """Knowledge hub renders pack cards with section counts."""
    page.goto(f"{server}/knowledge")
    cards = page.locator(".knowledge-card")
    assert cards.count() >= 5, "expected several knowledge packs to render"
    # MITRE pack should be among them (user has noted this is a flagship pack)
    expect(page.locator("body")).to_contain_text("MITRE")
