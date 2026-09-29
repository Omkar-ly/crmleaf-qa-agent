import time
from core.base_module import ScreenModule
from playwright.sync_api import Page


class TasksModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Tasks", depends_on=["Milestones"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if not project_id:
            raise RuntimeError("Missing context.project_id for Tasks module.")

        task_title = f"Task_{str(int(time.time()))[-5:]}"

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

        # Allow drawer animation and loaders to settle
        page.locator(".preloader-container").wait_for(state="hidden", timeout=10000)
        page.wait_for_timeout(1000)

        # Scope directly across the active modal/drawer form
        title_input = (
            page.locator('input[name="heading"], #heading')
            .or_(page.get_by_role("textbox", name="Title *"))
            .locator("visible=true")
            .first
        )
        title_input.wait_for(state="visible", timeout=15000)
        title_input.fill(task_title)

        # Without Due Date Checkbox
        without_due = (
            page.get_by_role("checkbox", name="Without Due Date")
            .locator("visible=true")
            .first
        )
        if without_due.is_visible(timeout=2000):
            without_due.check()

        # Assign Member
        assignee = (
            page.locator('button[data-id="user_id"], button[title="Nothing selected"]')
            .locator("visible=true")
            .first
        )
        if assignee.is_visible(timeout=3000):
            assignee.click()
            opt = (
                page.locator(".dropdown-menu.show li:not(.disabled) a")
                .locator("visible=true")
                .first
            )
            if opt.is_visible(timeout=2000):
                opt.click()
            page.keyboard.press("Escape")

        # Save Task
        save_btn = (
            page.locator(
                '#save-task-data-form button:has-text("Save"), #save-task-form, button.btn-primary:has-text("Save")'
            )
            .locator("visible=true")
            .first
        )
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")

        if context is not None:
            context.task_name = task_title

        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        task_name = getattr(context, "task_name", None)
        if not task_name:
            return False
        return (
            page.locator(f"text='{task_name}'")
            .locator("visible=true")
            .first.is_visible(timeout=8000)
        )
