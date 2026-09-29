from core.base_module import ScreenModule
from playwright.sync_api import Page


class ProjectOverviewModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Project Overview", depends_on=["Project Creation"])

    def run(self, page: Page, context=None) -> bool:
        # Step 1: Navigate to Projects List
        page.goto(
            "https://www.crmleaf.com/account/projects", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        # Step 2: Open List View
        list_btn = page.get_by_role("link", name="List")
        if list_btn.is_visible(timeout=2000):
            list_btn.click()

        # Step 3: Click the first project title link
        project_link = page.locator("td a[href*='/account/projects/']").first
        project_link.wait_for(state="visible", timeout=10000)
        project_link.click()

        # Step 4: Verify Overview Screen
        page.wait_for_load_state("domcontentloaded")
        page.locator("h4, h3, .project-header, .tab-pane").first.wait_for(
            state="visible", timeout=10000
        )

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
