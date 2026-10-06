"""
Playwright end-to-end UI smoke tests for the TicketIQ Angular frontend.

Run with:
    cd ticketiq
    python -m playwright install chromium
    pytest tests/playwright/test_ui.py -v --headed

Requires:
  - Angular dev server running on http://localhost:4200
  - TicketIQ AI Service running on http://127.0.0.1:8000
"""

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:4200"


@pytest.fixture(scope="module")
def browser_context(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    yield context
    context.close()
    browser.close()


@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    yield page
    page.close()


# ── Layout ────────────────────────────────────────────────────────────────────

def test_sidebar_visible(page: Page):
    """Sidebar navigation should be visible on load."""
    expect(page.locator(".sidebar")).to_be_visible()


def test_brand_title_visible(page: Page):
    """TicketIQ brand title must appear in the sidebar."""
    expect(page.locator(".brand-title")).to_contain_text("TicketIQ")


def test_nav_tabs_visible(page: Page):
    """All five navigation items should be rendered."""
    nav = page.locator(".nav-menu .nav-item")
    expect(nav).to_have_count(5)


# ── Ticket Cockpit ────────────────────────────────────────────────────────────

def test_ticket_input_visible(page: Page):
    """Ticket input textarea should be visible on the Cockpit tab."""
    expect(page.locator("textarea")).to_be_visible()


def test_sample_lockout_button_fills_input(page: Page):
    """Clicking 'Lockout' sample button should populate the ticket text area."""
    page.get_by_text("Account Lockout").first.click()
    textarea = page.locator("textarea").first
    expect(textarea).to_contain_text("locked")


def test_analyze_button_visible(page: Page):
    """The Analyze Ticket button should be present."""
    btn = page.get_by_role("button", name="Analyze Ticket")
    if btn.count() == 0:
        btn = page.locator("button").filter(has_text="Analyze")
    expect(btn.first).to_be_visible()


def test_analyze_ticket_flow(page: Page):
    """Full analyze flow: fill in ticket, click analyze, expect result or error."""
    # Fill the ticket text
    textarea = page.locator("textarea").first
    textarea.fill("User cannot log in, account locked after too many failed login attempts.")

    # Click analyze
    btn = page.locator("button").filter(has_text="Analyze").first
    btn.click()

    # Wait for either the result section or an error message (up to 20s)
    page.wait_for_selector(".result-section, .error-banner, .no-match-banner, .evidence-card",
                           timeout=20000)

    # Something should be shown
    result_visible = (
        page.locator(".evidence-card").count() > 0
        or page.locator(".error-banner").count() > 0
        or page.locator(".no-match-banner").count() > 0
    )
    assert result_visible, "Expected result, evidence, or error to be visible after analysis"


# ── Navigation ────────────────────────────────────────────────────────────────

def test_navigate_to_dashboard(page: Page):
    """Clicking Operations Overview tab should show the dashboard."""
    page.locator(".nav-item").filter(has_text="Operations").click()
    expect(page.locator("h2")).to_contain_text("Operations")


def test_navigate_to_knowledge_base(page: Page):
    """Knowledge Base tab should load the article catalog."""
    page.locator(".nav-item").filter(has_text="Knowledge").click()
    page.wait_for_timeout(1000)
    # Either shows articles or an empty-state
    kb_section_visible = (
        page.locator(".kb-card").count() > 0
        or page.locator("h2").filter(has_text="Knowledge").count() > 0
    )
    assert kb_section_visible


def test_navigate_to_evaluation_tab(page: Page):
    """Evaluation Quality tab should show metric cards."""
    page.locator(".nav-item").filter(has_text="Evaluation").click()
    expect(page.locator("h2")).to_contain_text("Evaluation")


# ── Chatbot ───────────────────────────────────────────────────────────────────

def test_chatbot_toggle_opens(page: Page):
    """The chatbot FAB should toggle the chatbot panel open."""
    fab = page.locator(".chatbot-fab")
    if fab.count() == 0:
        pytest.skip("No chatbot FAB found — component may differ")
    fab.click()
    page.wait_for_timeout(500)
    expect(page.locator(".chatbot-window, .chatbot-panel")).to_be_visible()


# ── PII Shield indicator ──────────────────────────────────────────────────────

def test_pii_shield_badge_visible(page: Page):
    """PII Shield Active badge should be visible in the topbar."""
    expect(page.locator(".shield-badge")).to_be_visible()
    expect(page.locator(".shield-badge")).to_contain_text("PII Shield")
