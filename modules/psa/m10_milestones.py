import re
from core.base_module import ScreenModule
from playwright.sync_api import Page


class MilestonesModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Milestones", depends_on=["Project Overview"])

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
            raise RuntimeError("Project ID not resolved for Milestones module.")

        page.goto(
            f"https://www.crmleaf.com/account/projects/{project_id}?tab=milestones",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        create_btn = (
            page.locator(
                'a:has-text("Create Milestone"), button:has-text("Create Milestone")'
            )
            .locator("visible=true")
            .first
        )
        create_btn.wait_for(state="visible", timeout=10000)
        create_btn.click()

        title_input = (
            page.locator('input[name="milestone_title"]')
            .or_(page.get_by_role("textbox", name="Milestone Title *"))
            .locator("visible=true")
            .first
        )
        title_input.wait_for(state="visible", timeout=5000)
        title_input.fill("Phase 1 Delivery")

        summary_input = (
            page.locator('textarea[name="summary"]')
            .or_(page.get_by_role("textbox", name="Milestone Summary *"))
            .locator("visible=true")
            .first
        )
        if summary_input.is_visible(timeout=2000):
            summary_input.fill("Initial milestone phase summary")

        save_btn = (
            page.locator(
                '#save-milestone-data-form button[type="button"]:has-text("Save"), #save-milestone-form, button:has-text("Save")'
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
            page.locator("text='Phase 1 Delivery'")
            .locator("visible=true")
            .first.is_visible(timeout=8000)
        )
