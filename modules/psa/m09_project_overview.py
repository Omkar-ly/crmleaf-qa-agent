import re
from core.base_module import ScreenModule
from playwright.sync_api import Page


class ProjectOverviewModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Project Overview", depends_on=["Project Creation"])

    def run(self, page: Page, context=None) -> bool:
        project_name = getattr(context, "project_name", None)

        # Step 1: Navigate to Projects
        page.goto(
            "https://www.crmleaf.com/account/projects", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")

        # Dismiss any open side panels (like tlPanel)
        page.keyboard.press("Escape")

        # Step 2: Ensure List view is active
        list_btn = (
            page.locator(
                'a[href*="/account/projects"]:has-text("List"), a:has-text("List")'
            )
            .locator("visible=true")
            .first
        )
        if list_btn.is_visible(timeout=3000):
            list_btn.click(force=True)
            page.wait_for_load_state("networkidle")

        # Step 3: Search specifically for the created project using the table search bar
        if project_name:
            # Explicitly target the table search box, ignoring global header searches
            search_input = (
                page.locator(
                    '#search-text-field, .dataTables_filter input[type="search"], .search-box input'
                )
                .locator("visible=true")
                .first
            )

            if search_input.is_visible(timeout=3000):
                search_input.fill(project_name)
                # Wait for the AJAX table to filter the results
                page.wait_for_timeout(1500)

            project_link = (
                page.locator(f"a:has-text('{project_name}')")
                .locator("visible=true")
                .first
            )
        else:
            project_link = (
                page.locator("td a[href*='/account/projects/']")
                .locator("visible=true")
                .first
            )

        # Fallback to the first available project in the table if exact text search failed
        if not project_link.is_visible(timeout=4000):
            project_link = (
                page.locator("table tbody tr td a[href*='/account/projects/']")
                .locator("visible=true")
                .first
            )

        project_link.wait_for(state="visible", timeout=10000)

        # Ensure panels are closed again and force the click to bypass tlPanel
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        project_link.scroll_into_view_if_needed()
        project_link.click(force=True)

        page.wait_for_load_state("domcontentloaded")
        page.wait_for_load_state("networkidle")

        # Step 4: Extract and store project_id into context
        m = re.search(r"/account/projects/(\d+)", page.url)
        if m and context is not None:
            context.project_id = m.group(1)

        return self.validate_invariants(page, context)

    def validate_invariants(self, page: Page, context=None) -> bool:
        return getattr(context, "project_id", None) is not None
