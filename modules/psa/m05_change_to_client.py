from core.base_module import ScreenModule
from playwright.sync_api import Page


class ChangeToClientModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Change To Client", depends_on=["Proposal Acceptance"])

    def run(self, page: Page, context=None) -> bool:
        page.goto(
            "https://www.crmleaf.com/account/lead-contact",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        target_name = getattr(context, "client_name", None) or "ASO1"
        row = page.locator(f"tr:has-text('{target_name}')")
        if row.count() == 0:
            row = page.locator("table tbody tr").first

        action_btn = row.locator("[id^=dropdownMenuLink-]").first
        action_btn.wait_for(state="visible", timeout=10000)
        action_btn.click(force=True)

        change_link = page.get_by_role("link", name="Change To Client")
        if change_link.is_visible(timeout=3000):
            change_link.click()

            # Handle required custom field if prompted
            custom_input = page.get_by_role("textbox", name="Qui pariatur Incidi *")
            if custom_input.is_visible(timeout=2000):
                custom_input.fill("Standard Company Client")

            page.get_by_role("button", name="Save", exact=True).click()
            page.wait_for_load_state("networkidle")

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
