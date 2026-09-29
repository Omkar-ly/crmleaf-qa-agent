from core.base_module import ScreenModule
from playwright.sync_api import Page


class ProposalModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Proposal Creation", depends_on=["Deal Creation"])

    def run(self, page: Page, context=None) -> bool:
        # Step 1: Navigate to Proposals
        page.goto(
            "https://www.crmleaf.com/account/proposals", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        # Step 2: Open Create Proposal
        create_proposal_btn = page.get_by_role("link", name="Create Proposal").first
        create_proposal_btn.wait_for(state="visible", timeout=15000)
        create_proposal_btn.click()

        # Step 3: Wait for loaders to hide (not detached)
        preloader = page.locator(".preloader-container")
        if preloader.count() > 0:
            preloader.first.wait_for(state="hidden", timeout=10000)

        overlay = page.locator(".blockUI.blockOverlay")
        if overlay.count() > 0:
            overlay.first.wait_for(state="hidden", timeout=10000)

        # Step 4: Select Lead / Contact
        lead_picker = page.locator(
            'button[data-id="deal_id"], div.bootstrap-select'
        ).first
        if lead_picker.is_visible(timeout=3000):
            lead_picker.click()
            first_opt = page.locator(".dropdown-menu.show li:not(.disabled) a").first
            if first_opt.is_visible(timeout=2000):
                first_opt.click()

        # Step 5: Pick Product using the dropdown button
        product_btn = page.locator('button[data-id="add-products"]').first
        if product_btn.is_visible(timeout=5000):
            product_btn.scroll_into_view_if_needed()
            product_btn.click(force=True)
            prod_opt = page.locator(
                ".dropdown-menu.show li:not(.disabled) a, #bs-select-7-0, #bs-select-7-1"
            ).first
            if prod_opt.is_visible(timeout=2000):
                prod_opt.click()
        else:
            item_name = page.get_by_role("textbox", name="Item Name").first
            if item_name.is_visible(timeout=2000):
                item_name.fill("Consulting Services")

        # Dismiss open menus
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

        # Step 6: Save Proposal
        save_btn = page.locator(
            '#saveInvoiceForm button[type="button"]:has-text("Save"), button:has-text("Save")'
        ).first
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        save_and_send = page.get_by_role("link", name="Save & Send").first
        if save_and_send.is_visible(timeout=2000):
            save_and_send.click()

        page.wait_for_load_state("networkidle")

        # Record created entity context if engine context is available
        if context is not None:
            if not getattr(context, "client_name", None):
                context.client_name = "ASO1"

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True


ProposalCreationModule = ProposalModule
