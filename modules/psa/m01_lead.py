import time
from core.base_module import ScreenModule
from playwright.sync_api import Page


class LeadCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Lead Creation", depends_on=[])

    def run(self, page: Page, context=None) -> bool:
        run_tag = str(int(time.time()))[-5:]
        lead_name = f"Lead_{run_tag}"
        company_name = f"Company_{run_tag}"
        lead_email = f"lead_{run_tag}@example.com"

        page.goto(
            "https://www.crmleaf.com/account/lead-contact",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        add_btn = (
            page.locator(
                'a:has-text("Add Lead Contact"), button:has-text("Add Lead Contact")'
            )
            .locator("visible=true")
            .first
        )
        add_btn.wait_for(state="visible", timeout=15000)
        add_btn.click()

        page.locator(".preloader-container").wait_for(state="hidden", timeout=10000)
        page.locator(".blockUI.blockOverlay").wait_for(state="hidden", timeout=10000)

        form = page.locator("#save-lead-data-form")
        form.wait_for(state="visible", timeout=10000)

        name_input = (
            form.locator('input[name="client_name"], input[name="name"]')
            .locator("visible=true")
            .first
        )
        name_input.wait_for(state="visible", timeout=5000)
        name_input.fill(lead_name)

        email_input = form.locator('input[name="email"]').locator("visible=true").first
        if email_input.is_visible(timeout=2000):
            email_input.fill(lead_email)

        company_select_btn = (
            form.locator('button[data-id="company_id"]').locator("visible=true").first
        )
        if company_select_btn.is_visible(timeout=3000):
            company_select_btn.click()

            add_company_btn = (
                page.locator(
                    'button[description="Add Company"], a[description="Add Company"], button:has-text("Add")'
                )
                .locator("visible=true")
                .first
            )
            if add_company_btn.is_visible(timeout=3000):
                add_company_btn.click()

                company_box = (
                    page.locator('#save-lead-company-form input[name="company_name"]')
                    .locator("visible=true")
                    .first
                )
                company_box.wait_for(state="visible", timeout=5000)
                company_box.fill(company_name)

                save_company_btn = (
                    page.locator("#save-lead-company").locator("visible=true").first
                )
                save_company_btn.click()
                save_company_btn.wait_for(state="hidden", timeout=5000)
                page.wait_for_timeout(500)
            else:
                first_opt = (
                    page.locator(".dropdown-menu.show li:not(.disabled) a")
                    .locator("visible=true")
                    .first
                )
                if first_opt.is_visible(timeout=2000):
                    first_opt.click()

        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

        save_btn = (
            form.get_by_role("button", name="Save", exact=True)
            .or_(page.locator("#save-lead-form"))
            .locator("visible=true")
            .first
        )
        save_btn.wait_for(state="visible", timeout=10000)
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")

        if context is not None:
            context.client_name = lead_name
            context.company_name = company_name

        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        lead_name = getattr(context, "client_name", None)
        if not lead_name:
            return False
        toast_or_row = (
            page.locator(f"text='{lead_name}'")
            .or_(page.locator(".toast-success"))
            .locator("visible=true")
            .first
        )
        return toast_or_row.is_visible(timeout=8000)
