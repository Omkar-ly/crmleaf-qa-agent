from core.base_module import ScreenModule
from playwright.sync_api import Page


class MilestonesModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Milestones", depends_on=["Project Overview"])

    def run(self, page: Page, context=None) -> bool:
        # Step 1: Ensure we are inside an active project screen
        if "/account/projects/" not in page.url or "?tab=" in page.url:
            page.goto(
                "https://www.crmleaf.com/account/projects",
                wait_until="domcontentloaded",
            )
            page.wait_for_load_state("networkidle")
            list_btn = page.get_by_role("link", name="List")
            if list_btn.is_visible(timeout=2000):
                list_btn.click()
            project_link = page.locator("td a[href*='/account/projects/']").first
            project_link.wait_for(state="visible", timeout=10000)
            project_link.click()
            page.wait_for_load_state("networkidle")

        # Step 2: Target Milestones tab across desktop or mobile views
        milestone_tab = page.locator(
            '#mob-client-detail a:has-text("Milestones"), '
            '.project-menu a:has-text("Milestones"), '
            'a[href*="tab=milestones"], '
            'a:has-text("Milestones")'
        ).first

        if not milestone_tab.is_visible(timeout=5000):
            # If tab bar is collapsed under a dropdown menu
            more_dropdown = page.locator(
                "#mob-client-detail .dropdown-toggle, .project-menu .dropdown-toggle"
            ).first
            if more_dropdown.is_visible(timeout=2000):
                more_dropdown.click()

        milestone_tab.wait_for(state="visible", timeout=10000)
        milestone_tab.click(force=True)
        page.wait_for_load_state("networkidle")

        # Step 3: Create Milestone
        create_btn = page.locator(
            'a:has-text("Create Milestone"), button:has-text("Create Milestone")'
        ).first
        create_btn.wait_for(state="visible", timeout=10000)
        create_btn.click()

        title_input = (
            page.get_by_role("textbox", name="Milestone Title *")
            .or_(page.locator('input[name="milestone_title"]'))
            .first
        )
        title_input.wait_for(state="visible", timeout=5000)
        title_input.fill("Phase 1 Delivery")

        summary_input = (
            page.get_by_role("textbox", name="Milestone Summary *")
            .or_(page.locator('textarea[name="summary"]'))
            .first
        )
        if summary_input.is_visible(timeout=2000):
            summary_input.fill("Initial milestone phase summary")

        page.get_by_role("button", name="Save").click()
        page.wait_for_load_state("networkidle")
        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        return True
