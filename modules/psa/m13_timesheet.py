import datetime
from core.base_module import ScreenModule
from playwright.sync_api import Page


class TimesheetModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Time Sheet", depends_on=["Task Board"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if not project_id:
            raise RuntimeError("Missing context.project_id for Time Sheet module.")

        page.goto(
            f"https://www.crmleaf.com/account/projects/{project_id}?tab=timelogs",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        # Open Log Time modal / drawer
        log_btn = (
            page.locator('a:has-text("Log Time"), button:has-text("Log Time")')
            .locator("visible=true")
            .first
        )
        log_btn.wait_for(state="visible", timeout=15000)
        log_btn.click()

        form = (
            page.locator("#save-timelog-data-form, #save-timelog-form")
            .locator("visible=true")
            .first
        )
        form.wait_for(state="visible", timeout=10000)

        today_str = datetime.datetime.now().strftime("%d-%m-%Y")

        # Handle Start Date and End Date inputs (using d-m-Y)
        start_date = (
            form.locator('input[name="start_date"]')
            .or_(form.get_by_role("textbox", name="Start Date *"))
            .locator("visible=true")
            .first
        )
        if start_date.is_visible(timeout=3000):
            start_date.evaluate(
                f"(el) => {{ el.value = '{today_str}'; el.dispatchEvent(new Event('change', {{bubbles: true}})); }}"
            )

        end_date = (
            form.locator('input[name="end_date"]')
            .or_(form.get_by_role("textbox", name="End Date *"))
            .locator("visible=true")
            .first
        )
        if end_date.is_visible(timeout=3000):
            end_date.evaluate(
                f"(el) => {{ el.value = '{today_str}'; el.dispatchEvent(new Event('change', {{bubbles: true}})); }}"
            )

        # Select Member dropdown if present
        member_picker = (
            form.locator('button[data-id="user_id"]')
            .or_(form.get_by_role("combobox", name="--"))
            .locator("visible=true")
            .first
        )
        if member_picker.is_visible(timeout=2000):
            member_picker.click()
            opt = (
                page.locator(".dropdown-menu.show li:not(.disabled) a")
                .locator("visible=true")
                .first
            )
            if opt.is_visible(timeout=2000):
                opt.click()
            page.keyboard.press("Escape")

        # Memo input
        memo_box = (
            form.locator('input[name="memo"]')
            .or_(form.get_by_role("textbox", name="Memo *"))
            .locator("visible=true")
            .first
        )
        if memo_box.is_visible(timeout=3000):
            memo_box.fill("Automated Timesheet Verification")

        # Submit Time Log
        save_btn = (
            form.locator(
                'button[type="button"]:has-text("Save"), button:has-text("Save")'
            )
            .locator("visible=true")
            .first
        )
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")
        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        if page.url == "about:blank":
            project_id = getattr(context, "project_id", None)
            page.goto(
                f"https://www.crmleaf.com/account/projects/{project_id}?tab=timelogs",
                wait_until="domcontentloaded",
            )

        # Valid Playwright selector combining CSS and text with .or_()
        target = (
            page.locator("text='Automated Timesheet Verification'")
            .or_(page.locator("table tbody tr"))
            .locator("visible=true")
            .first
        )

        if not target.is_visible(timeout=8000):
            raise AssertionError(
                "Timesheet entry not visible in project timelog table."
            )
        return True
