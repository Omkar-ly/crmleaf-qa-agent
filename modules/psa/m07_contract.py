from core.base_module import ScreenModule
from playwright.sync_api import Page


class ContractCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Contract Creation", depends_on=["Quote Creation"])

    def run(self, page: Page, context=None) -> bool:
        # Step 1: Navigate to Contracts
        page.goto(
            "https://www.crmleaf.com/account/contracts", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        # Dismiss any open side panels or overlays
        close_drawer = page.locator(
            "#close-task-detail, .close-task-detail, .task-detail-panel .close"
        )
        if close_drawer.is_visible(timeout=2000):
            close_drawer.first.click()
            page.wait_for_timeout(500)

        page.locator(".blockUI.blockOverlay").wait_for(state="detached", timeout=10000)

        # Step 2: Open Create Contract
        create_contract_btn = page.get_by_role("link", name="Create Contract").first
        create_contract_btn.wait_for(state="visible", timeout=15000)
        create_contract_btn.click()

        # Step 3: Fill Contract Subject & Settings
        subject_input = page.get_by_role("textbox", name="Subject *")
        subject_input.wait_for(state="visible", timeout=5000)
        subject_input.fill("Master Services Agreement")

        without_due = page.get_by_role("checkbox", name="Without Due Date")
        if without_due.is_visible(timeout=2000):
            without_due.check()

        amount_input = page.locator("input[name='amount']")
        if amount_input.is_visible(timeout=2000):
            amount_input.fill("5000000")

        # Step 4: Select Client
        client_picker = page.get_by_role("combobox", name="Select Client")
        if client_picker.is_visible(timeout=3000):
            client_picker.click()
            first_client = page.locator(".dropdown-menu.show [role='option']").first
            if first_client.is_visible(timeout=2000):
                first_client.click()

        # Step 5: Save Contract
        save_btn = page.get_by_role("button", name="Save").first
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")
        page.locator(".blockUI.blockOverlay").wait_for(state="detached", timeout=10000)

        # Step 6: Company Signature
        action_dropdown = page.locator("[id^='dropdownMenuLink-']").first
        if action_dropdown.is_visible(timeout=5000):
            action_dropdown.click(force=True)
            sign_link = page.get_by_role("link", name="Company Signature")
            if sign_link.is_visible(timeout=3000):
                sign_link.click()
                sign_pad = page.locator("#sign-pad")
                if sign_pad.is_visible(timeout=3000):
                    sign_pad.click(position={"x": 200, "y": 50})
                    page.get_by_role("button", name="Sign", exact=True).click()
                    page.wait_for_load_state("networkidle")

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
