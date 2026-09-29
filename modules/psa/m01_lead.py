import time
from core.base_module import ScreenModule
from playwright.sync_api import Page


class LeadCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Lead Creation", depends_on=[])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        run_tag = str(int(time.time()))[-5:]
        lead_name = f"ASO_{run_tag}"
        lead_email = f"lead_{run_tag}@example.com"
        company_name = f"Company_{run_tag}"

        page.goto(
            "https://www.crmleaf.com/account/lead-contact",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        # 1. Open Add Lead Contact drawer
        add_btn = (
            page.get_by_role("link", name="Add Lead Contact")
            .or_(
                page.locator(
                    'a:has-text("Add Lead Contact"), button:has-text("Add Lead Contact")'
                )
            )
            .locator("visible=true")
            .first
        )
        add_btn.wait_for(state="visible", timeout=15000)
        add_btn.click()

        page.locator(".preloader-container").wait_for(state="hidden", timeout=10000)
        form = (
            page.locator("#save-lead-data-form, #save-lead-form")
            .locator("visible=true")
            .first
        )
        form.wait_for(state="visible", timeout=10000)

        # 2. Select Salutation
        salutation_btn = (
            form.locator('button[data-id="salutation"]')
            .or_(form.get_by_role("combobox", name="--").first)
            .locator("visible=true")
            .first
        )
        if salutation_btn.is_visible(timeout=3000):
            salutation_btn.click()
            page.wait_for_timeout(300)
            mr_opt = page.locator(".dropdown-menu.show a:has-text('Mr')").first
            if mr_opt.is_visible(timeout=2000):
                mr_opt.click()
            else:
                page.locator(".dropdown-menu.show li:not(.disabled) a").first.click()
            page.keyboard.press("Escape")

        # 3. Fill Name and Email
        name_input = (
            form.get_by_role("textbox", name="Name *", exact=True)
            .or_(form.locator('input[name="client_name"], input[name="name"]'))
            .locator("visible=true")
            .first
        )
        name_input.wait_for(state="visible", timeout=5000)
        name_input.fill(lead_name)

        email_input = (
            form.get_by_role("textbox", name="Email")
            .or_(form.locator('input[name="email"]'))
            .locator("visible=true")
            .first
        )
        if email_input.is_visible(timeout=3000):
            email_input.fill(lead_email)

        # 4. Company Selection / Auto-Creation
        add_comp_btn = (
            page.get_by_role("button", name="Add", description="Add Company")
            .or_(
                form.locator(
                    'button[description="Add Company"], a[description="Add Company"]'
                )
            )
            .or_(form.locator('.form-group:has-text("Company") button:has-text("Add")'))
            .locator("visible=true")
            .first
        )

        if not add_comp_btn.is_visible(timeout=3000):
            form.get_by_role("combobox", name="Select Company").or_(
                form.locator('button[data-id="company_id"]')
            ).first.click(force=True)
            page.wait_for_timeout(300)
            add_comp_btn = (
                page.locator(
                    '.dropdown-menu.show a:has-text("Add"), button:has-text("Add")'
                )
                .locator("visible=true")
                .first
            )

        add_comp_btn.click(force=True)

        comp_name_box = (
            page.get_by_role("textbox", name="Company Name *")
            .or_(page.locator('#save-lead-company-form input[name="company_name"]'))
            .locator("visible=true")
            .first
        )
        comp_name_box.wait_for(state="visible", timeout=7000)
        comp_name_box.fill(company_name)

        save_comp_btn = page.locator("#save-lead-company").locator("visible=true").first
        save_comp_btn.click(force=True)
        save_comp_btn.wait_for(state="hidden", timeout=10000)
        page.wait_for_timeout(1000)

        # Update select element and bootstrap-select state directly
        page.evaluate(
            f"""(compName) => {{
            const selectEl = document.querySelector('select#company_id, select[name="company_id"]');
            if (selectEl) {{
                let targetVal = null;
                for (let i = 0; i < selectEl.options.length; i++) {{
                    if (selectEl.options[i].text.includes(compName)) {{
                        targetVal = selectEl.options[i].value;
                        selectEl.selectedIndex = i;
                        break;
                    }}
                }}
                if (!targetVal && selectEl.options.length > 1) {{
                    targetVal = selectEl.options[selectEl.options.length - 1].value;
                    selectEl.selectedIndex = selectEl.options.length - 1;
                }}
                if (targetVal) {{
                    selectEl.value = targetVal;
                    if (window.jQuery && window.jQuery(selectEl).selectpicker) {{
                        window.jQuery(selectEl).selectpicker('val', targetVal);
                        window.jQuery(selectEl).selectpicker('refresh');
                    }}
                    selectEl.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }}
        }}""",
            company_name,
        )

        # 5. Uncheck 'Create Deal'
        create_deal_checkbox = (
            form.get_by_role("checkbox", name="Create Deal")
            .locator("visible=true")
            .first
        )
        if create_deal_checkbox.is_visible(timeout=3000):
            create_deal_checkbox.scroll_into_view_if_needed()
            if create_deal_checkbox.is_checked():
                create_deal_checkbox.uncheck(force=True)

        # 6. Save Form
        save_btn = (
            form.get_by_role("button", name="Save", exact=True)
            .or_(
                form.locator('#save-lead-form, button[type="button"]:has-text("Save")')
            )
            .locator("visible=true")
            .first
        )
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        try:
            save_btn.wait_for(state="hidden", timeout=12000)
        except Exception:
            err_els = page.locator(
                ".invalid-feedback:visible, .text-danger:visible, .help-block:visible"
            ).all_inner_texts()
            err_msg = (
                " | ".join([e.strip() for e in err_els if e.strip()])
                if err_els
                else "Form did not submit"
            )
            raise RuntimeError(f"Lead creation failed validation: {err_msg}")

        page.wait_for_load_state("networkidle")

        if context is not None:
            context.client_name = lead_name
            context.lead_name = lead_name
            context.lead_email = lead_email
            context.company_name = company_name

        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        lead_name = getattr(context, "client_name", None) or getattr(
            context, "lead_name", None
        )
        if not lead_name:
            return False

        if "/account/lead-contact" not in page.url:
            page.goto(
                "https://www.crmleaf.com/account/lead-contact",
                wait_until="domcontentloaded",
            )
            page.wait_for_load_state("networkidle")

        search_box = (
            page.locator('input[type="search"], #search-text-field')
            .locator("visible=true")
            .first
        )
        if search_box.is_visible(timeout=3000):
            search_box.fill(lead_name)
            page.wait_for_timeout(1000)

        match = (
            page.locator(f"table tbody tr:has-text('{lead_name}')")
            .or_(page.locator(f"a:has-text('{lead_name}')"))
            .locator("visible=true")
            .first
        )
        return match.is_visible(timeout=8000)


# Support both naming conventions across runner scripts
LeadModule = LeadCreationModule
