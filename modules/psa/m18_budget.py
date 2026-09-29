import time
import datetime
from core.base_module import ScreenModule
from playwright.sync_api import Page


class BudgetModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Budget", depends_on=["Project Overview"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        project_name = getattr(context, "project_name", None)
        run_tag = str(int(time.time()))[-5:]
        budget_name = f"Budget_{run_tag}"

        # 1. Open Budget tab under the active project
        if project_id:
            page.goto(
                f"https://www.crmleaf.com/account/projects/{project_id}?tab=budget",
                wait_until="domcontentloaded",
            )
        else:
            page.goto(
                "https://www.crmleaf.com/account/projects",
                wait_until="domcontentloaded",
            )
            if project_name:
                page.locator(f"a:has-text('{project_name}')").first.click(force=True)
            more_btn = (
                page.get_by_role("button", name="More ↓").locator("visible=true").first
            )
            if more_btn.is_visible(timeout=3000):
                more_btn.click()
                page.get_by_role("link", name="Budget", exact=True).click()[cite:9]

        page.wait_for_load_state("networkidle")

        # 2. Click 'Create a budget'[cite: 9]
        add_btn = (
            page.get_by_role("link", name="Create a budget")
            .or_(
                page.locator(
                    'a:has-text("Create a budget"), button:has-text("Create a budget"), a:has-text("Add Budget")'
                )
            )
            .locator("visible=true")
            .first
        )
        add_btn.wait_for(state="visible", timeout=15000)
        add_btn.click(force=True)

        page.locator(".preloader-container").wait_for(state="hidden", timeout=10000)
        page.locator(".blockUI.blockOverlay").wait_for(state="hidden", timeout=10000)

        form = (
            page.locator("#save-budget-data-form, #save-budget-form, form")
            .locator("visible=true")
            .first
        )
        form.wait_for(state="visible", timeout=10000)

        # 3. Budget Name[cite: 9]
        name_input = (
            form.get_by_role("textbox", name="Name *")
            .or_(form.locator('input[name="name"]'))
            .locator("visible=true")
            .first
        )
        name_input.wait_for(state="visible", timeout=5000)
        name_input.fill(budget_name)

        # 4. Project Selection (if rendered as empty combobox)[cite: 9]
        proj_combobox = (
            form.locator(
                '.form-group:has-text("Project") button[data-toggle="dropdown"]'
            )
            .or_(form.get_by_role("combobox", name="--").first)
            .locator("visible=true")
            .first
        )

        if proj_combobox.is_visible(timeout=2000):
            proj_combobox.click(force=True)
            page.wait_for_timeout(300)

            search_box = (
                page.get_by_role("combobox", name="Search")
                .or_(
                    page.locator(
                        ".dropdown-menu.show input[type='search'], .dropdown-menu.show .bs-searchbox input"
                    )
                )
                .locator("visible=true")
                .first
            )

            if search_box.is_visible(timeout=2000) and project_name:
                search_box.fill(project_name)[cite:9]
                page.wait_for_timeout(400)
                first_opt = page.locator(
                    ".dropdown-menu.show ul.dropdown-menu.inner li:not(.disabled) a"
                ).first
                if first_opt.is_visible(timeout=2000):
                    first_opt.click(force=True)
                else:
                    search_box.press("ArrowDown")[cite:9]
                    search_box.press("Enter")[cite:9]
            else:
                page.locator(
                    ".dropdown-menu.show ul.dropdown-menu.inner li:not(.disabled) a"
                ).first.click(force=True)

            page.keyboard.press("Escape")
            page.wait_for_timeout(300)

        # 5. Total Budgeted Amount[cite: 9]
        amount_box = (
            form.get_by_role("spinbutton", name="Total budgeted")
            .or_(form.locator('input[name="budgeted_amount"], input[name="amount"]'))
            .locator("visible=true")
            .first
        )
        if amount_box.is_visible(timeout=3000):
            amount_box.fill("500000")[cite:9]

        # 6. Dates (Period start and end in d-m-Y format)[cite: 9]
        today = datetime.datetime.now()
        start_dmy = today.strftime("%d-%m-%Y")
        end_dmy = (today + datetime.timedelta(days=30)).strftime("%d-%m-%Y")

        start_input = (
            form.get_by_role("textbox", name="Period start")
            .or_(form.locator('input[name="start_date"]'))
            .locator("visible=true")
            .first
        )
        if start_input.is_visible(timeout=2000):
            start_input.evaluate(
                f"(el) => {{ el.value = '{start_dmy}'; el.dispatchEvent(new Event('change', {{bubbles: true}})); }}"
            )

        end_input = (
            form.get_by_role("textbox", name="Period end")
            .or_(form.locator('input[name="end_date"]'))
            .locator("visible=true")
            .first
        )
        if end_input.is_visible(timeout=2000):
            end_input.evaluate(
                f"(el) => {{ el.value = '{end_dmy}'; el.dispatchEvent(new Event('change', {{bubbles: true}})); }}"
            )

        form.click(position={"x": 5, "y": 5}, force=True)
        page.wait_for_timeout(300)

        # 7. Save Budget[cite: 9]
        save_btn = (
            form.get_by_role("button", name="Save")
            .or_(
                form.locator(
                    '#save-budget-form, button[type="button"]:has-text("Save")'
                )
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
                else "Budget form did not submit"
            )
            raise RuntimeError(f"Budget validation failed: {err_msg}")

        page.wait_for_load_state("networkidle")
        page.locator(".blockUI.blockOverlay").wait_for(state="hidden", timeout=10000)

        # 8. Approve Budget if Action Menu is visible[cite: 9]
        row = (
            page.locator(f"table tbody tr:has-text('{budget_name}')")
            .or_(page.locator("table tbody tr"))
            .locator("visible=true")
            .first
        )
        if row.is_visible(timeout=5000):
            action_btn = row.locator(
                "button.dropdown-toggle, [id^=dropdownMenuLink-]"
            ).first
            if action_btn.is_visible(timeout=3000):
                action_btn.click(force=True)
                page.wait_for_timeout(400)
                approve_link = page.locator(
                    '.dropdown-menu.show a:has-text("Approve")'
                ).first
                if approve_link.is_visible(timeout=2000):
                    approve_link.click(force=True)[cite:9]
                    confirm_btn = (
                        page.get_by_role("button", name="Yes")
                        .or_(page.locator('button:has-text("Yes")'))
                        .locator("visible=true")
                        .first
                    )
                    if confirm_btn.is_visible(timeout=3000):
                        confirm_btn.click(force=True)[cite:9]
                        page.wait_for_timeout(1000)

        if context is not None:
            context.budget_name = budget_name

        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        budget_name = getattr(context, "budget_name", None)
        if not budget_name:
            return True
        return (
            page.locator(f"table tbody tr:has-text('{budget_name}')")
            .or_(page.locator("table tbody tr"))
            .locator("visible=true")
            .count()
            > 0
        )
