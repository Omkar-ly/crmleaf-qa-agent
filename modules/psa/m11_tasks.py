import re
from core.base_module import ScreenModule
from playwright.sync_api import Page


class TasksModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Tasks", depends_on=["Milestones"])

    def run(self, page: Page, context=None) -> bool:
        # Step 1: Ensure project ID is derived or click Tasks tab directly
        current_url = page.url
        match = re.search(r"/account/projects/(\d+)", current_url)

        if match:
            project_id = match.group(1)
            target_url = (
                f"https://www.crmleaf.com/account/projects/{project_id}?tab=tasks"
            )
            page.goto(target_url, wait_until="domcontentloaded")
        else:
            task_nav = page.locator(
                '#mob-client-detail a[href*="tab=tasks"], '
                '#mob-client-detail a:has-text("Tasks"), '
                '.project-menu a:has-text("Tasks"), '
                'a:has-text("Tasks")'
            ).first

            if not task_nav.is_visible(timeout=3000):
                dropdown_toggle = page.locator(
                    "#mob-client-detail .dropdown-toggle, .project-menu .dropdown-toggle"
                ).first
                if dropdown_toggle.is_visible(timeout=2000):
                    dropdown_toggle.click()

            task_nav.wait_for(state="visible", timeout=10000)
            task_nav.click(force=True)

        page.wait_for_load_state("networkidle")
        page.locator(".preloader-container").wait_for(state="hidden", timeout=10000)
        page.locator(".blockUI.blockOverlay").wait_for(state="hidden", timeout=10000)

        # Step 2: Open Add Task modal / form
        add_task_btn = page.locator(
            'a.openRightModal:has-text("Add Task"), '
            'a:has-text("Add Task"), '
            'button:has-text("Add Task")'
        ).first
        add_task_btn.wait_for(state="visible", timeout=15000)
        add_task_btn.click()

        # Step 3: Enter Task Details
        title_input = (
            page.get_by_role("textbox", name="Title *")
            .or_(page.locator('input[name="heading"]'))
            .first
        )
        title_input.wait_for(state="visible", timeout=10000)
        title_input.fill("System Architecture & Test Setup")

        without_due = page.get_by_role("checkbox", name="Without Due Date")
        if without_due.is_visible(timeout=2000):
            without_due.check()

        # Step 4: Save Task
        save_btn = page.locator(
            '#save-task-data-form, button.btn-primary:has-text("Save"), button[type="submit"]:has-text("Save")'
        ).first
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")
        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
