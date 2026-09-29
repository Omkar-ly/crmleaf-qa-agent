import re
from core.base_module import ScreenModule
from playwright.sync_api import Page


class TasksModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Tasks", depends_on=["Milestones"])

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if not project_id:
            page.goto(
                "https://www.crmleaf.com/account/projects",
                wait_until="domcontentloaded",
            )
            page.locator("td a[href*='/account/projects/']").locator(
                "visible=true"
            ).first.click()
            page.wait_for_load_state("networkidle")
            m = re.search(r"/account/projects/(\d+)", page.url)
            project_id = m.group(1) if m else None
            if context and project_id:
                context.project_id = project_id

        if not project_id:
            raise RuntimeError("Project ID not resolved for Tasks module.")

        page.goto(
            f"https://www.crmleaf.com/account/projects/{project_id}?tab=tasks",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        add_task_btn = (
            page.locator(
                'a.openRightModal:has-text("Add Task"), a:has-text("Add Task"), button:has-text("Add Task")'
            )
            .locator("visible=true")
            .first
        )
        add_task_btn.wait_for(state="visible", timeout=15000)
        add_task_btn.click()

        title_input = (
            page.locator('input[name="heading"]')
            .or_(page.get_by_role("textbox", name="Title *"))
            .locator("visible=true")
            .first
        )
        title_input.wait_for(state="visible", timeout=5000)
        title_input.fill("System Architecture & Test Setup")

        without_due = (
            page.get_by_role("checkbox", name="Without Due Date")
            .locator("visible=true")
            .first
        )
        if without_due.is_visible(timeout=2000):
            without_due.check()

        save_btn = (
            page.locator(
                '#save-task-data-form button[type="button"]:has-text("Save"), #save-task-form, button.btn-primary:has-text("Save")'
            )
            .locator("visible=true")
            .first
        )
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")
        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        return (
            page.locator("text='System Architecture & Test Setup'")
            .locator("visible=true")
            .first.is_visible(timeout=8000)
        )
