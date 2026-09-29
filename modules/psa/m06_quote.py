from core.base_module import ScreenModule
from playwright.sync_api import Page


class QuoteCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Quote Creation", depends_on=["Proposal Creation"])

    def run(self, page: Page, context=None) -> bool:
        page.goto(
            "https://www.crmleaf.com/account/estimates", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        create_quote_btn = page.get_by_role("link", name="Create Quote").first
        create_quote_btn.wait_for(state="visible", timeout=15000)
        create_quote_btn.click()

        # Resolve target client name defensively
        target_client = getattr(context, "client_name", None) or "ASO1"

        # Select Client combobox
        client_combobox = page.get_by_role("combobox", name="--").first
        if client_combobox.is_visible(timeout=3000):
            client_combobox.click()

            menu = page.locator(".dropdown-menu.show")
            client_option = menu.get_by_text(target_client).first
            if client_option.is_visible(timeout=2000):
                client_option.click()
            else:
                # Fallback to first non-empty option
                menu.locator("li:not(.disabled) a").first.click()

        # Save Quote
        save_btn = page.get_by_role("button", name="Save", exact=True).first
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")
        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
