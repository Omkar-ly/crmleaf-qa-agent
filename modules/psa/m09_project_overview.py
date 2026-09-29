import re
from core.base_module import ScreenModule
from playwright.sync_api import Page


class ProjectOverviewModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Project Overview", depends_on=["Project Creation"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_name = getattr(context, "project_name", None)

        # 1. Navigate to Projects area
        page.goto(
            "https://www.crmleaf.com/account/projects", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        # 2. Locate Project Link (supports card view, card title, or list view link)
        proj_link = None
        if project_name:
            proj_link = (
                page.locator(f"a:has-text('{project_name}')")
                .locator("visible=true")
                .first
            )

        if not proj_link or not proj_link.is_visible(timeout=3000):
            proj_link = (
                page.locator(
                    "a[href*='/account/projects/']:not([href*='card-view']):not([href*='view-list']):not([href*='create'])"
                )
                .locator("visible=true")
                .first
            )

        proj_link.wait_for(state="visible", timeout=15000)

        # 3. Extract and persist project_id into context
        href = proj_link.get_attribute("href") or ""
        match = re.search(r"/account/projects/(\d+)", href)
        if match and context is not None:
            context.project_id = match.group(1)

        proj_link.click(force=True)
        page.wait_for_load_state("networkidle")

        # Fallback extraction from active URL
        curr_match = re.search(r"/account/projects/(\d+)", page.url)
        if curr_match and context is not None:
            context.project_id = curr_match.group(1)

        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if project_id and project_id in page.url:
            return True
        return (
            page.locator(
                ".project-header, #project-detail, a:has-text('Overview'), a:has-text('Tasks')"
            )
            .locator("visible=true")
            .count()
            > 0
        )


# Alias to prevent naming conflicts across different runner configurations
OverviewModule = ProjectOverviewModule
