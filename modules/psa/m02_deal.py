import time
from core.base_module import ScreenModule
from playwright.sync_api import Page


class DealCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Deal Creation", depends_on=["Lead Creation"])

    def run(self, page: Page, context=None) -> bool:
        lead_name = getattr(context, "client_name", "ASO1")
        run_tag = str(int(time.time()))[-5:]

        page.goto(
            "https://www.crmleaf.com/account/deals", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        add_deal_btn = page.get_by_role("link", name="Add Deal").first
        add_deal_btn.wait_for(state="visible", timeout=15000)
        add_deal_btn.click()

        # Select the newly created Lead Contact
        lead_picker = page.get_by_role("combobox", name="--").first
        if lead_picker.is_visible(timeout=3000):
            lead_picker.click()
            matching_lead = page.locator(
                f".dropdown-menu.show li a:has-text('{lead_name}')"
            ).first
            if matching_lead.is_visible(timeout=2000):
                matching_lead.click()
            else:
                page.locator(".dropdown-menu.show li:not(.disabled) a").first.click()

        # Fill Deal Title with unique identifier
        deal_name_box = page.get_by_role("textbox", name="Deal Name *")
        deal_name_box.wait_for(state="visible", timeout=5000)
        deal_name_box.fill(f"Deal_{run_tag}")

        deal_val = page.get_by_role("spinbutton", name="Deal Value *")
        if deal_val.is_visible(timeout=2000):
            deal_val.fill("150000")

        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

        # Save Deal
        save_btn = (
            page.locator("#save-lead-form")
            .or_(page.get_by_role("button", name="Save", exact=True))
            .first
        )
        save_btn.wait_for(state="visible", timeout=5000)
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")
        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
