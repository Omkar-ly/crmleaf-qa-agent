import time
import datetime
from core.base_module import ScreenModule
from playwright.sync_api import Page, Error


class ProjectCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Project Creation", depends_on=["Contract Creation"])

    def _safe_goto(self, page: Page, url: str):
        """Absorbs ERR_ABORTED caused by asynchronous redirects from previous modules."""
        try:
            page.goto(url, wait_until="domcontentloaded")
        except Error as e:
            if "ERR_ABORTED" in str(e):
                page.wait_for_timeout(2000)
                page.goto(url, wait_until="domcontentloaded")
            else:
                raise

    def run(self, page: Page, context=None) -> bool:
        client_name = getattr(context, "client_name", None)
        if not client_name:
            raise RuntimeError(
                "Missing context.client_name from upstream Lead/Client module."
            )

        run_tag = str(int(time.time()))[-5:]
        project_name = f"Project_{run_tag}"
        short_code = f"PRJ{run_tag}"

        # 1. Resilient Navigation
        self._safe_goto(page, "https://www.crmleaf.com/account/projects")
        page.wait_for_load_state("networkidle")

        add_project_btn = (
            page.locator('a:has-text("Add Project"), button:has-text("Add Project")')
            .locator("visible=true")
            .first
        )
        add_project_btn.wait_for(state="visible", timeout=15000)
        add_project_btn.click(force=True)

        form = (
            page.locator("#save-project-data-form, #save-project-form")
            .locator("visible=true")
            .first
        )
        form.wait_for(state="visible", timeout=10000)

        # 2. Fill Project Name
        name_input = (
            form.get_by_role("textbox", name="Project Name *")
            .locator("visible=true")
            .first
        )
        name_input.wait_for(state="visible", timeout=5000)
        name_input.fill(project_name)

        # 3. Fill Short Code (Mandatory)
        short_code_input = (
            form.locator('input[name="project_short_code"]')
            .or_(form.get_by_role("textbox", name="Short Code *"))
            .locator("visible=true")
            .first
        )
        if short_code_input.is_visible(timeout=2000):
            short_code_input.fill(short_code)

        # 4. Handle Start Date Datepicker
        start_date_input = (
            form.get_by_role("textbox", name="Start Date *")
            .locator("visible=true")
            .first
        )
        if start_date_input.is_visible(timeout=3000):
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            start_date_input.evaluate(
                f"(el) => {{ el.value = '{today_str}'; el.dispatchEvent(new Event('change', {{bubbles: true}})); }}"
            )

            start_date_input.click(force=True)
            page.wait_for_timeout(500)

            today_day = str(datetime.datetime.now().day)
            active_calendar = (
                page.locator(
                    ".qs-datepicker-container.qs-active, .datepicker.dropdown-menu"
                )
                .locator("visible=true")
                .first
            )

            if active_calendar.is_visible(timeout=2000):
                day_cell = active_calendar.get_by_text(today_day, exact=True).first
                if day_cell.is_visible():
                    day_cell.click(force=True)
                else:
                    active_calendar.locator(
                        ".qs-square:not(.qs-empty), td.day:not(.old):not(.new)"
                    ).first.click(force=True)
            else:
                fallback = (
                    page.locator(
                        f".qs-square:text-is('{today_day}'), td.day:text-is('{today_day}')"
                    )
                    .locator("visible=true")
                    .first
                )
                if fallback.is_visible():
                    fallback.click(force=True)

            form.click(position={"x": 5, "y": 5}, force=True)
            page.keyboard.press("Escape")

        # 5. Check Deadline Option
        no_deadline = (
            form.get_by_role("checkbox", name="There is no project deadline")
            .locator("visible=true")
            .first
        )
        if no_deadline.is_visible(timeout=2000):
            no_deadline.check(force=True)

        # 6. Client Selection
        client_combobox = (
            form.locator('button[data-id="client_id"]').locator("visible=true").first
        )
        if not client_combobox.is_visible():
            client_combobox = (
                form.get_by_role("combobox", name="--").locator("visible=true").nth(1)
            )

        if client_combobox.is_visible(timeout=3000):
            client_combobox.scroll_into_view_if_needed()
            client_combobox.click(force=True)

            menu = page.locator(".dropdown-menu.show").locator("visible=true").first
            match_opt = menu.locator(f"a:has-text('{client_name}')").first
            if match_opt.is_visible(timeout=2000):
                match_opt.click(force=True)
            else:
                menu.locator("li:not(.disabled) a").first.click(force=True)

            page.keyboard.press("Escape")
            page.wait_for_timeout(300)

        # 7. Members Selection
        members_combobox = (
            form.locator("#add_members button")
            .or_(form.locator('button[data-id="user_id"]'))
            .locator("visible=true")
            .first
        )

        if members_combobox.is_visible(timeout=3000):
            members_combobox.scroll_into_view_if_needed()
            members_combobox.click(force=True)

            members_menu = (
                page.locator(".dropdown-menu.show").locator("visible=true").first
            )
            first_member = members_menu.locator("li:not(.disabled) a").first
            if first_member.is_visible(timeout=2000):
                first_member.click(force=True)

            page.keyboard.press("Escape")
            page.wait_for_timeout(300)

        # 8. Save the Project
        save_btn = (
            form.locator(
                'button[type="button"]:has-text("Save"), button[type="submit"]:has-text("Save")'
            )
            .locator("visible=true")
            .first
        )
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        try:
            save_btn.wait_for(state="hidden", timeout=8000)
        except Exception:
            error_texts = page.locator(
                ".invalid-feedback:visible, .text-danger:visible, .help-block:visible"
            ).all_inner_texts()
            err_msg = (
                " | ".join([e.strip() for e in error_texts if e.strip()])
                if error_texts
                else "Unknown validation error"
            )
            raise RuntimeError(
                f"Project save failed: Form did not close. Validation errors: {err_msg}"
            )

        page.wait_for_load_state("networkidle")

        if context is not None:
            context.project_name = project_name

        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        project_name = getattr(context, "project_name", None)
        if not project_name:
            return False

        # Avoid double-navigation if already on the list page
        if "/account/projects" not in page.url or "create" in page.url:
            self._safe_goto(page, "https://www.crmleaf.com/account/projects")

        return (
            page.locator(f"a:has-text('{project_name}')")
            .locator("visible=true")
            .first.is_visible(timeout=10000)
        )
