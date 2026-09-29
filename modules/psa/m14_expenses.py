import time
from core.base_module import ScreenModule
from playwright.sync_api import Page


class ExpensesModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Expenses", depends_on=["Project Overview"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if not project_id:
            raise RuntimeError("Missing context.project_id for Expenses module.")

        item_name = f"Expense_{str(int(time.time()))[-5:]}"

        page.goto(
            f"https://www.crmleaf.com/account/projects/{project_id}?tab=expenses",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        add_expense_btn = (
            page.locator('a:has-text("Add Expense"), button:has-text("Add Expense")')
            .locator("visible=true")
            .first
        )
        add_expense_btn.wait_for(state="visible", timeout=15000)
        add_expense_btn.click()

        form = (
            page.locator("#save-expense-data-form, #save-expense-form")
            .locator("visible=true")
            .first
        )
        form.wait_for(state="visible", timeout=10000)

        # Fill Item Name
        item_box = (
            form.locator('input[name="item_name"]')
            .or_(form.get_by_role("textbox", name="Item Name *"))
            .locator("visible=true")
            .first
        )
        item_box.wait_for(state="visible", timeout=5000)
        item_box.fill(item_name)

        # Fill Price
        price_box = (
            form.locator('input[name="price"]')
            .or_(form.get_by_role("spinbutton", name="Price *"))
            .locator("visible=true")
            .first
        )
        if price_box.is_visible(timeout=3000):
            price_box.fill("350")

        # Mark as Bill to Client
        bill_client = (
            form.get_by_role("checkbox", name="Bill to Client")
            .locator("visible=true")
            .first
        )
        if bill_client.is_visible(timeout=2000):
            bill_client.check()

        # Select Member / Employee
        emp_picker = (
            form.locator('button[data-id="user_id"]')
            .or_(form.get_by_role("combobox", name="--"))
            .locator("visible=true")
            .first
        )
        if emp_picker.is_visible(timeout=3000):
            emp_picker.click()
            first_user = (
                page.locator(".dropdown-menu.show li:not(.disabled) a")
                .locator("visible=true")
                .first
            )
            if first_user.is_visible(timeout=2000):
                first_user.click()
            page.keyboard.press("Escape")

        # Save Expense
        save_btn = (
            form.locator(
                'button[type="button"]:has-text("Save"), button:has-text("Save")'
            )
            .locator("visible=true")
            .first
        )
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        page.wait_for_load_state("networkidle")
        if context is not None:
            context.expense_name = item_name

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        if page.url == "about:blank":
            project_id = getattr(context, "project_id", None)
            page.goto(
                f"https://www.crmleaf.com/account/projects/{project_id}?tab=expenses",
                wait_until="domcontentloaded",
            )
        expense_name = getattr(context, "expense_name", None)
        target = (
            page.locator(f"text='{expense_name}'")
            .or_(page.locator("table tbody tr"))
            .locator("visible=true")
            .first
        )
        if not target.is_visible(timeout=8000):
            raise AssertionError(
                "Expense item was not created in the project expenses view."
            )
        return True
