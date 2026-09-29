from core.base_module import ScreenModule
from playwright.sync_api import Page


class GanttChartModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Gantt Chart", depends_on=["Tasks"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if not project_id:
            raise RuntimeError("Missing context.project_id for Gantt Chart module.")

        page.goto(
            f"https://www.crmleaf.com/account/projects/{project_id}?tab=gantt",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        gantt_chart = (
            page.locator(".gantt_container, .gantt_layout_cell, #gantt_here")
            .locator("visible=true")
            .first
        )
        gantt_chart.wait_for(state="visible", timeout=15000)

        # Exercise toolbar zoom/toggle
        toolbar_btn = (
            page.locator(
                'button:has-text("Toolbar"), button:has-text("Day"), button:has-text("Month")'
            )
            .locator("visible=true")
            .first
        )
        if toolbar_btn.is_visible(timeout=3000):
            toolbar_btn.click()

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        if page.url == "about:blank":
            project_id = getattr(context, "project_id", None)
            page.goto(
                f"https://www.crmleaf.com/account/projects/{project_id}?tab=gantt",
                wait_until="domcontentloaded",
            )
        gantt_chart = page.locator(
            ".gantt_container, .gantt_layout_cell, #gantt_here"
        ).locator("visible=true")
        if gantt_chart.count() == 0:
            raise AssertionError("Gantt Chart layout container did not render.")
        return True
