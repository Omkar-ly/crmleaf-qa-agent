import time
from core.base_module import ScreenModule
from playwright.sync_api import Page


class LeadCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Lead Creation", depends_on=[])

    def run(self, page: Page, context=None) -> bool:
        # Generate unique inputs for every single execution run
        run_tag = str(int(time.time()))[-5:]
        lead_name = f"ASO_{run_tag}"
        company_name = f"BDM_{run_tag}"
        lead_email = f"lead_{run_tag}@example.com"

        page.goto(
            "https://www.crmleaf.com/account/lead-contact",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        add_btn = page.locator(
            'a:has-text("Add Lead Contact"), button:has-text("Add Lead Contact")'
        ).first
        add_btn.wait_for(state="visible", timeout=15000)
        add_btn.click()

        page.locator(".preloader-container").wait_for(state="hidden", timeout=10000)
        page.locator(".blockUI.blockOverlay").wait_for(state="hidden", timeout=10000)

        # Enter Lead Name & Email
        name_input = (
            page.get_by_role("textbox", name="Name *", exact=True)
            .or_(
                page.locator(
                    '#save-lead-data-form input[name="name"], input[name="client_name"]'
                )
            )
            .first
        )
        name_input.wait_for(state="visible", timeout=10000)
        name_input.fill(lead_name)

        email_input = (
            page.get_by_role("textbox", name="Email")
            .or_(page.locator('#save-lead-data-form input[name="email"]'))
            .first
        )
        if email_input.is_visible(timeout=2000):
            email_input.fill(lead_email)

        # Open Select Company dropdown
        company_select_btn = (
            page.locator('button[data-id="company_id"]')
            .or_(page.get_by_role("combobox", name="Select Company"))
            .first
        )

        if company_select_btn.is_visible(timeout=3000):
            company_select_btn.click()

            # Target the Add Company button directly inside the dropdown/header
            add_company_btn = (
                page.locator(
                    'button[description="Add Company"], '
                    'a[description="Add Company"], '
                    'button:has-text("Add"), '
                    'a:has-text("Add")'
                )
                .filter(has_text="Add")
                .first
            )

            if add_company_btn.is_visible(timeout=3000):
                add_company_btn.click()

                # Wait for the company creation modal and input field
                company_box = (
                    page.locator('#save-lead-company-form input[name="company_name"]')
                    .or_(page.get_by_role("textbox", name="Company Name *"))
                    .first
                )
                company_box.wait_for(state="visible", timeout=5000)
                company_box.fill(company_name)

                # Save the new company modal
                save_company_btn = page.locator("#save-lead-company").first
                save_company_btn.click()

                # Wait for the company sub-modal to close
                save_company_btn.wait_for(state="hidden", timeout=5000)
                page.wait_for_timeout(500)
            else:
                first_opt = page.locator(
                    ".dropdown-menu.show li:not(.disabled) a"
                ).first
                if first_opt.is_visible(timeout=2000):
                    first_opt.click()

        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

        # Submit the main Lead Contact form
        save_btn = page.locator(
            "#save-lead-form, "
            '#save-lead-data-form button[type="button"]:has-text("Save"), '
            "#save-lead-contact-form, "
            '.modal-footer button.btn-primary:has-text("Save")'
        ).first

        save_btn.wait_for(state="visible", timeout=10000)
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")

        # Pass unique credentials forward to subsequent modules
        if context is not None:
            context.client_name = lead_name
            context.company_name = company_name

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
