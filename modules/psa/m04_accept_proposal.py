import os
from core.base_module import ScreenModule
from playwright.sync_api import Page


class AcceptProposalModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Proposal Acceptance", depends_on=["Proposal Creation"])

    def run(self, page: Page, context=None) -> bool:
        page.goto(
            "https://www.crmleaf.com/account/proposals", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        target_id = getattr(context, "proposal_id", None)
        row = (
            page.locator(f"tr:has-text('{target_id}')")
            if target_id
            else page.locator("table tbody tr").locator("visible=true").first
        )

        action_btn = (
            row.locator("[id^=dropdownMenuLink-]").locator("visible=true").first
        )
        action_btn.wait_for(state="visible", timeout=10000)
        action_btn.click(force=True)

        with page.expect_popup() as popup_info:
            page.get_by_role("link", name="Public Link").locator("visible=true").click()
        public_page = popup_info.value

        public_page.wait_for_load_state("domcontentloaded")
        accept_btn = (
            public_page.get_by_role("link", name="Accept").locator("visible=true").first
        )
        if accept_btn.is_visible(timeout=10000):
            accept_btn.click()

            signer_name = getattr(context, "client_name", "Authorized Signer")
            signer_email = os.getenv(
                "TEST_SIGNER_EMAIL",
                getattr(context, "signer_email", "qa-test-signer@example.com"),
            )

            public_page.get_by_role("textbox", name="Name *").locator(
                "visible=true"
            ).fill(signer_name)
            public_page.get_by_role("textbox", name="Email *").locator(
                "visible=true"
            ).fill(signer_email)

            sign_pad = public_page.locator("#signature-pad").locator("visible=true")
            if sign_pad.is_visible(timeout=3000):
                sign_pad.click(position={"x": 200, "y": 50})

            public_page.get_by_role("button", name="Sign", exact=True).locator(
                "visible=true"
            ).click()
            public_page.wait_for_load_state("networkidle")

        public_page.close()
        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True


ProposalAcceptanceModule = AcceptProposalModule
