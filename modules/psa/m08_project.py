import time
import datetime
from core.base_module import ScreenModule
from playwright.sync_api import Page, Error


class ProjectCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Project Creation", depends_on=["Contract Creation"])

    def _safe_goto(self, page: Page, url: str):
        try:
            page.goto(url, wait_until="domcontentloaded")
        except Error as e:
            if "ERR_ABORTED" in str(e):
                page.wait_for_timeout(2000)
                page.goto(url, wait_until="domcontentloaded")
            else:
                raise

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        client_name = getattr(context, "client_name", None) or getattr(
            context, "lead_name", None
        )
        run_tag = str(int(time.time()))[-5:]
        project_name = f"Project_{run_tag}"
        short_code = f"PRJ{run_tag}"

        self._safe_goto(page, "https://www.crmleaf.com/account/projects/card-view")
        page.wait_for_load_state("networkidle")

        add_project_btn = (
            page.get_by_role("link", name="Add Project")
            .or_(
                page.locator(
                    'a:has-text("Add Project"), button:has-text("Add Project")'
                )
            )
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

        # 1. Project Name
        name_input = (
            form.get_by_role("textbox", name="Project Name *")
            .locator("visible=true")
            .first
        )
        name_input.wait_for(state="visible", timeout=5000)
        name_input.fill(project_name)

        # 2. Short Code
        short_code_input = (
            form.locator('input[name="project_short_code"]')
            .or_(form.get_by_role("textbox", name="Short Code *"))
            .locator("visible=true")
            .first
        )
        if short_code_input.is_visible(timeout=2000):
            short_code_input.fill(short_code)

        # 3. Start Date (d-m-Y format required)
        start_date_input = (
            form.get_by_role("textbox", name="Start Date *")
            .locator("visible=true")
            .first
        )
        if start_date_input.is_visible(timeout=3000):
            today_dmy = datetime.datetime.now().strftime("%d-%m-%Y")
            start_date_input.evaluate(
                f"(el) => {{ el.value = '{today_dmy}'; el.dispatchEvent(new Event('change', {{bubbles: true}})); }}"
            )
            page.keyboard.press("Escape")

        # 4. Deadline Checkbox
        no_deadline = (
            form.get_by_role("checkbox", name="There is no project deadline")
            .locator("visible=true")
            .first
        )
        if no_deadline.is_visible(timeout=2000):
            no_deadline.check(force=True)

        # 5. Client Dropdown Selection
        client_combobox = (
            form.locator('button[data-id="client_id"]')
            .or_(
                form.locator(
                    '.form-group:has-text("Client") button[data-toggle="dropdown"]'
                )
            )
            .or_(form.get_by_role("combobox", name="--").nth(1))
            .locator("visible=true")
            .first
        )

        if client_combobox.is_visible(timeout=5000):
            client_combobox.scroll_into_view_if_needed()
            client_combobox.click(force=True)
            page.wait_for_timeout(400)

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

            if search_box.is_visible(timeout=2000) and client_name:
                # Strip prefix if needed and search
                search_query = client_name.replace("ASO_", "").replace("Lead_", "")
                search_box.fill(search_query)
                page.wait_for_timeout(400)
                search_box.press("ArrowDown")
                search_box.press("Enter")
            else:
                page.locator(
                    ".dropdown-menu.show ul.dropdown-menu.inner li:not(.disabled) a"
                ).first.click(force=True)

            page.keyboard.press("Escape")
            page.wait_for_timeout(300)

        # 6. Members Selection (Mandatory)
        members_combobox = (
            form.locator("#add_members")
            .get_by_role("combobox", name="Nothing selected")
            .or_(form.locator('button[data-id="user_id"], #add_members button'))
            .locator("visible=true")
            .first
        )

        if members_combobox.is_visible(timeout=5000):
            members_combobox.scroll_into_view_if_needed()
            members_combobox.click(force=True)
            page.wait_for_timeout(400)

            member_search = (
                page.get_by_role("combobox", name="Search")
                .or_(
                    page.locator(
                        ".dropdown-menu.show input[type='search'], .dropdown-menu.show .bs-searchbox input"
                    )
                )
                .locator("visible=true")
                .first
            )

            if member_search.is_visible(timeout=2000):
                member_search.press("ArrowDown")
                member_search.press("Enter")
            else:
                page.locator(".dropdown-menu.show li:not(.disabled) a").first.click(
                    force=True
                )

            page.keyboard.press("Escape")
            page.wait_for_timeout(300)

        # 7. Save Project
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
            raise RuntimeError(f"Project save failed validation: {err_msg}")

        page.wait_for_load_state("networkidle")

        if context is not None:
            context.project_name = project_name

        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        project_name = getattr(context, "project_name", None)
        if not project_name:
            return False
        return True
