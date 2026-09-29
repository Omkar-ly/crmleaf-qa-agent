from core.base_module import ScreenModule
from playwright.sync_api import Page


class AcceptProposalModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Proposal Acceptance", depends_on=["Proposal Creation"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        proposal_id = getattr(context, "proposal_id", None)

        page.goto(
            "https://www.crmleaf.com/account/proposals", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        # 1. Target proposal link directly from the list table
        if proposal_id:
            row = (
                page.locator(f"table tbody tr:has-text('{proposal_id}')")
                .locator("visible=true")
                .first
            )
        else:
            row = page.locator("table tbody tr").locator("visible=true").first

        row.wait_for(state="visible", timeout=15000)

        # 2. Click the proposal title or view link to open proposal public details
        proposal_link = row.locator(
            "a[href*='/proposal/'], a[href*='/account/proposals/']"
        ).first
        if not proposal_link.is_visible(timeout=3000):
            # Try via row action dropdown
            menu_btn = row.locator(
                "button.dropdown-toggle, [id^=dropdownMenuLink-]"
            ).first
            menu_btn.click()
            proposal_link = page.locator(
                ".dropdown-menu.show a:has-text('View'), .dropdown-menu.show a[href*='/proposal/']"
            ).first

        href = proposal_link.get_attribute("href") or ""
        if "/proposal/" in href:
            if not href.startswith("http"):
                href = f"https://www.crmleaf.com{href}"
            page.goto(href, wait_until="domcontentloaded")
        else:
            proposal_link.click()

        page.wait_for_load_state("networkidle")

        # 3. Accept and Sign
        accept_btn = (
            page.locator('button:has-text("Accept"), a:has-text("Accept")')
            .locator("visible=true")
            .first
        )
        if accept_btn.is_visible(timeout=5000):
            accept_btn.click(force=True)
            page.wait_for_timeout(500)

            # Draw on signature pad if displayed
            signature_pad = (
                page.locator("#signature-pad, canvas").locator("visible=true").first
            )
            if signature_pad.is_visible(timeout=2000):
                box = signature_pad.bounding_box()
                if box:
                    page.mouse.move(box["x"] + 20, box["y"] + 20)
                    page.mouse.down()
                    page.mouse.move(box["x"] + 100, box["y"] + 40)
                    page.mouse.up()

            sign_btn = (
                page.locator(
                    'button#save-signature, button[type="button"]:has-text("Sign"), button:has-text("Accept")'
                )
                .locator("visible=true")
                .first
            )
            if sign_btn.is_visible(timeout=3000):
                sign_btn.click(force=True)
                page.wait_for_timeout(1000)

        page.wait_for_load_state("networkidle")
        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
