import pytest
from playwright.sync_api import Page, expect

def test_ticket_iq_title_and_header(page: Page):
    # Navigate to local Angular frontend (assuming dev server running on 4200)
    page.goto("http://localhost:4200")
    
    # Check Header Title
    expect(page.locator("h1")).to_contain_text("TicketIQ")
    expect(page.locator(".tagline")).to_contain_text("Evidence-Gated IT Support Copilot")

def test_ticket_quick_fill_sample(page: Page):
    page.goto("http://localhost:4200")
    
    # Click "Payroll Auth Error" sample button
    page.click("button:has-text('Payroll Auth Error')")
    
    # Verify input text is populated with AUTH-401 details
    textarea = page.locator("textarea")
    expect(textarea).to_contain_text("AUTH-401")
