from core.base_module import ScreenModule
from playwright.sync_api import Page


class PaymentModule(ScreenModule):
    def __init__(self):
        super().__init__(name="Payment", depends_on=["Invoices"])

    def execute(self, page: Page, context=None):
        return self.run(page, context)

    def run(self, page: Page, context=None) -> bool:
        project_id = getattr(context, "project_id", None)
        if not project_id:
            raise RuntimeError("Missing context.project_id for Payment module.")

        # Navigate to Project Payments tab
        page.goto(
            f"https://www.crmleaf.com/account/projects/{project_id}?tab=payments",
            wait_until="domcontentloaded",
        )
        page.wait_for_load_state("networkidle")

        add_pay_btn = (
            page.get_by_role("link", name="Add Payment")
            .or_(
                page.locator(
                    'a:has-text("Add Payment"), button:has-text("Add Payment")'
                )
            )
            .locator("visible=true")
            .first
        )

        if not add_pay_btn.is_visible(timeout=4000):
            # Fallback navigation if tab button didn't render
            page.goto(
                "https://www.crmleaf.com/account/payments",
                wait_until="domcontentloaded",
            )
            page.wait_for_load_state("networkidle")
            add_pay_btn = (
                page.get_by_role("link", name="Add Payment")
                .or_(
                    page.locator(
                        'a:has-text("Add Payment"), button:has-text("Add Payment")'
                    )
                )
                .locator("visible=true")
                .first
            )

        add_pay_btn.wait_for(state="visible", timeout=15000)
        add_pay_btn.click()

        form = (
            page.locator("#save-payment-data-form, #save-payment-form")
            .locator("visible=true")
            .first
        )
        form.wait_for(state="visible", timeout=10000)

        # 1. Single Payment option
        single_pay = (
            form.get_by_role("radio", name="Single Payment")
            .or_(form.locator('input[value="single"]'))
            .locator("visible=true")
            .first
        )
        if single_pay.is_visible(timeout=3000):
            single_pay.check(force=True)

        # 2. Select Invoice if dropdown exists
        inv_combobox = (
            form.locator('button[data-id="invoice_id"]')
            .or_(form.get_by_role("combobox", name="--").first)
            .locator("visible=true")
            .first
        )
        if inv_combobox.is_visible(timeout=3000):
            inv_combobox.click(force=True)
            page.wait_for_timeout(400)
            first_inv = page.locator(".dropdown-menu.show li:not(.disabled) a").first
            if first_inv.is_visible(timeout=2000):
                first_inv.click(force=True)
            page.keyboard.press("Escape")

        # 3. Enter Amount
        amount_input = (
            form.get_by_role("spinbutton", name="Amount *")
            .or_(form.locator('input[name="amount"]'))
            .locator("visible=true")
            .first
        )
        if amount_input.is_visible(timeout=3000):
            amount_input.fill("1000")

        # 4. Click Save
        save_btn = (
            form.locator(
                '#save-payment-form, button[type="button"]:has-text("Save"), button:has-text("Save")'
            )
            .locator("visible=true")
            .first
        )
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)

        try:
            save_btn.wait_for(state="hidden", timeout=10000)
        except Exception:
            pass

        page.wait_for_load_state("networkidle")
        return True

    def validate_invariants(self, page: Page, context=None) -> bool:
        page.goto(
            "https://www.crmleaf.com/account/payments", wait_until="domcontentloaded"
        )
        page.wait_for_load_state("networkidle")
        return (
            page.locator("table tbody tr, #payments-table tbody tr")
            .locator("visible=true")
            .count()
            > 0
        )
