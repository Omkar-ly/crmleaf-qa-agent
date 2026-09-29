from core.base_module import ScreenModule
from playwright.sync_api import Page


class ProjectCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Project Creation")

    def run(self, page: Page, context=None) -> bool:
        # Step 1: Navigate to Projects
        page.goto(
            "https://www.crmleaf.com/account/projects", wait_until="domcontentloaded"
        )

        # Step 2: Open Add Project
        add_project_btn = page.get_by_role("link", name="Add Project").first
        add_project_btn.wait_for(state="visible", timeout=15000)
        add_project_btn.click()

        # Step 3: Fill Project Name & Settings
        project_name = page.get_by_role("textbox", name="Project Name *")
        project_name.wait_for(state="visible", timeout=5000)
        project_name.fill("Enterprise Implementation Project")

        # Check 'no project deadline'
        no_deadline = page.get_by_role("checkbox", name="There is no project deadline")
        if no_deadline.is_visible(timeout=2000):
            no_deadline.check()

        # Assign Members if available
        members_combobox = page.locator("#add_members").get_by_role("combobox").first
        if members_combobox.is_visible(timeout=2000):
            members_combobox.click()
            member_opt = page.locator(".dropdown-menu.show [role='option']").first
            if member_opt.is_visible(timeout=2000):
                member_opt.click()

        # Step 4: Save Project
        save_btn = page.get_by_role("button", name="Save", exact=True)
        save_btn.click()

        page.wait_for_load_state("networkidle")
        return True
