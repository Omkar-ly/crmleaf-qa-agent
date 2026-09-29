import re
from core.base_module import ScreenModule
from playwright.sync_api import Page


class InvoiceCreationModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Invoices", depends_on=["Project Overview"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if not project_id:
            raise RuntimeError("Missing context.project_id for Invoices module.")

        page.goto(
            f"https://www.crmleaf.com/account/projects/{project_id}?tab=invoices",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        # Support empty state or toolbar button
        create_inv_btn = (
            page.locator(
                'a:has-text("Create Invoice"), button:has-text("Create Invoice"), a:has-text("Add Invoice")'
            )
            .locator("visible=true")
            .first
        )
        create_inv_btn.wait_for(state="visible", timeout=15000)
        create_inv_btn.click()

        form = page.locator("#saveInvoiceForm").locator("visible=true").first
        form.wait_for(state="visible", timeout=10000)

        # Warehouse Picker if present
        warehouse_picker = (
            form.locator('button[data-id="warehouse_id"]')
            .or_(
                form.get_by_role("combobox", description="Select Warehouse", exact=True)
            )
            .locator("visible=true")
            .first
        )
        if warehouse_picker.is_visible(timeout=3000):
            warehouse_picker.click()
            first_wh = (
                page.locator(".dropdown-menu.show li:not(.disabled) a")
                .locator("visible=true")
                .first
            )
            if first_wh.is_visible(timeout=2000):
                first_wh.click()
            page.keyboard.press("Escape")

        # Select Product
        product_btn = (
            form.locator('button[data-id="add-products"]')
            .or_(form.locator('button:has-text("Select Product")'))
            .locator("visible=true")
            .first
        )
        if product_btn.is_visible(timeout=4000):
            product_btn.click()
            first_prod = (
                page.locator(".dropdown-menu.show li:not(.disabled) a")
                .locator("visible=true")
                .first
            )
            if first_prod.is_visible(timeout=2000):
                first_prod.click()
            page.keyboard.press("Escape")

        # Save Invoice
        save_btn = (
            form.locator(
                '#saveInvoiceForm button:has-text("Save"), button:has-text("Save")'
            )
            .locator("visible=true")
            .first
        )
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        # Handle modal confirmations
        save_and_send = (
            page.locator('a:has-text("Save & Send")').locator("visible=true").first
        )
        if save_and_send.is_visible(timeout=3000):
            save_and_send.click()

        do_later = (
            page.locator('a:has-text("Do It Later"), button:has-text("Close")')
            .locator("visible=true")
            .first
        )
        if do_later.is_visible(timeout=3000):
            do_later.click()

        page.wait_for_load_state("networkidle")

        inv_link = (
            page.locator('a[href*="/account/invoices/"]:has-text("INV#")')
            .locator("visible=true")
            .first
        )
        if inv_link.is_visible(timeout=8000):
            match = re.search(r"INV#\d+", inv_link.inner_text())
            if match and context is not None:
                context.invoice_id = match.group(0)

        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        if page.url == "about:blank":
            project_id = getattr(context, "project_id", None)
            page.goto(
                f"https://www.crmleaf.com/account/projects/{project_id}?tab=invoices",
                wait_until="domcontentloaded",
            )
        inv_row = (
            page.locator(
                'a[href*="/account/invoices/"]:has-text("INV#"), table tbody tr'
            )
            .locator("visible=true")
            .first
        )
        if not inv_row.is_visible(timeout=8000):
            raise AssertionError(
                "Invoice was not created in the project invoices list."
            )
        return True
