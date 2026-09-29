from core.base_module import ScreenModule
from playwright.sync_api import Page


class TaskBoardModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Task Board", depends_on=["Tasks"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if not project_id:
            raise RuntimeError("Missing context.project_id for Task Board module.")

        page.goto(
            f"https://www.crmleaf.com/account/projects/{project_id}?tab=taskboard",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        # Confirm board columns or drag containers are visible
        board_container = (
            page.locator(".board-column, .drag-container, [id^=drag-container-]")
            .locator("visible=true")
            .first
        )
        board_container.wait_for(state="visible", timeout=15000)

        # Exercise Start Timer toggle if active task cards are present on the board
        start_timer_btn = (
            page.locator(
                'a[description="Start Timer"], a[title="Start Timer"], a.start-timer'
            )
            .locator("visible=true")
            .first
        )
        if start_timer_btn.is_visible(timeout=3000):
            start_timer_btn.click()
            page.wait_for_timeout(1000)

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        if page.url == "about:blank":
            project_id = getattr(context, "project_id", None)
            page.goto(
                f"https://www.crmleaf.com/account/projects/{project_id}?tab=taskboard",
                wait_until="domcontentloaded",
            )
        columns = page.locator(
            ".board-column, .drag-container, [id^=drag-container-]"
        ).locator("visible=true")
        if columns.count() == 0:
            raise AssertionError("Task Board Kanban columns failed to render.")
        return True
