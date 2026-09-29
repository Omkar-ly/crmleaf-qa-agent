import os
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

from core.context import AutomationContext
from core.models import Finding
from detectors.observer import DOMAndNetworkObserver
from evidence.collector import EvidenceCollector
from storage.excel_sink import ExcelTicketSink

from modules.psa.m01_lead import LeadCreationModule
from modules.psa.m02_deal import DealCreationModule
from modules.psa.m03_proposal import ProposalModule
from modules.psa.m04_accept_proposal import AcceptProposalModule
from modules.psa.m05_change_to_client import ChangeToClientModule
from modules.psa.m06_quote import QuoteCreationModule
from modules.psa.m07_contract import ContractCreationModule
from modules.psa.m08_project import ProjectCreationModule
from modules.psa.m09_project_overview import ProjectOverviewModule
from modules.psa.m10_milestones import MilestonesModule
from modules.psa.m11_tasks import TasksModule
from modules.psa.m12_task_board import TaskBoardModule
from modules.psa.m13_timesheet import TimesheetModule
from modules.psa.m14_expenses import ExpensesModule
from modules.psa.m15_gantt import GanttChartModule
from modules.psa.m16_invoice import InvoiceCreationModule
from modules.psa.m17_payment import PaymentModule


class SafeAutonomousEngine:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.sink = ExcelTicketSink("CRMLeaf PSA.xlsx")
        self.pipeline = [
            LeadCreationModule(),
            DealCreationModule(),
            ProposalModule(),
            AcceptProposalModule(),
            ChangeToClientModule(),
            QuoteCreationModule(),
            ContractCreationModule(),
            ProjectCreationModule(),
            ProjectOverviewModule(),
            MilestonesModule(),
            TasksModule(),
            TaskBoardModule(),
            TimesheetModule(),
            ExpensesModule(),
            GanttChartModule(),
            InvoiceCreationModule(),
            PaymentModule(),
        ]

    def _ensure_authenticated_session(
        self, p, base_url: str = "https://www.crmleaf.com"
    ):
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login_url = f"{base_url.rstrip('/')}/login"
        page.goto(login_url, wait_until="domcontentloaded", timeout=30000)

        email_field = page.get_by_role("textbox", name="Email Address")
        if email_field.is_visible(timeout=5000):
            email_field.fill(self.email)
            page.get_by_role("textbox", name="Password").fill(self.password)
            page.get_by_role("button", name="Log In").click()
            page.wait_for_load_state("domcontentloaded")

        workspace_link = page.get_by_role("link", name="BDM Industries")
        if workspace_link.is_visible(timeout=5000):
            workspace_link.click()
            page.wait_for_load_state("networkidle")

        page.wait_for_url("**/account/**", timeout=30000)

        storage_path = "auth_state.json"
        context.storage_state(path=storage_path)
        context.close()
        browser.close()
        return storage_path

    def run(self):
        run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ctx = AutomationContext(run_id=run_id)
        evidence = EvidenceCollector(run_id=run_id)

        passed_modules = set()
        failed_modules = set()
        blocked_modules = set()

        with sync_playwright() as p:
            auth_path = self._ensure_authenticated_session(p)

            for module in self.pipeline:
                missing_deps = [
                    dep for dep in module.depends_on if dep not in passed_modules
                ]
                if missing_deps:
                    print(
                        f"[-] [BLOCKED] {module.name} (Waiting for: {', '.join(missing_deps)})"
                    )
                    blocked_modules.add(module.name)
                    continue

                print(f"[>] Running: {module.name}...")

                screen_slug = module.name.replace(" ", "_")
                video_dir = Path("evidence") / run_id / screen_slug / "video"
                video_dir.mkdir(parents=True, exist_ok=True)

                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    storage_state=str(auth_path),
                    record_video_dir=str(video_dir),
                    viewport={"width": 1920, "height": 1080},
                )
                context.tracing.start(screenshots=True, snapshots=True, sources=False)
                page = context.new_page()
                observer = DOMAndNetworkObserver(page)

                start_time = time.time()
                success = False
                error_details = ""

                try:
                    module.execute(page, ctx)
                    module.validate_invariants(page, ctx)
                    success = True
                except Exception as ex:
                    error_details = str(ex)

                duration = time.time() - start_time

                if success:
                    print(f"[+] [PASS] {module.name} ({duration:.1f}s)")
                    passed_modules.add(module.name)
                    context.tracing.stop()
                    page.close()
                    context.close()
                    browser.close()
                else:
                    print(f"[!] [FAIL] {module.name}: {error_details}")
                    failed_modules.add(module.name)

                    ss_path = evidence.capture_screenshot(page, screen_slug)
                    diag_path = evidence.dump_logs(
                        screen_slug, observer.network_errors, observer.console_errors
                    )

                    trace_path = str(
                        Path("evidence") / run_id / screen_slug / "trace.zip"
                    )
                    try:
                        context.tracing.stop(path=trace_path)
                    except Exception:
                        trace_path = None

                    try:
                        page.close()
                        context.close()
                        browser.close()
                    except Exception:
                        pass

                    video_files = list(video_dir.glob("*.webm"))
                    vid_path = str(video_files[0]) if video_files else None

                    failure_type = (
                        "ScriptError"
                        if "Timeout" in error_details or "waiting for" in error_details
                        else "ProductDefect"
                    )

                    finding = Finding(
                        module="PSA",
                        screen=module.name,
                        failure_type=failure_type,
                        severity=(
                            "Critical" if failure_type == "ProductDefect" else "Major"
                        ),
                        title=f"{failure_type} in {module.name}",
                        repro_steps=f"1. Authenticate to CRMLeaf.\n2. Execute {module.name} workflow sequence.",
                        expected=f"Module {module.name} passes all UI invariants without blocking.",
                        actual=error_details.split("\n")[0],
                        target_locator=(
                            error_details.split("Call log:")[0].strip()
                            if "Call log:" in error_details
                            else ""
                        ),
                        normalized_reason=error_details.split("\n")[0][:120],
                        screenshot_path=ss_path,
                        video_path=vid_path,
                        trace_path=trace_path,
                        console_log_path=diag_path,
                    )
                    self.sink.sync_finding(finding, run_id)

        self.sink.log_run(
            run_id,
            len(self.pipeline),
            len(passed_modules),
            len(failed_modules),
            len(blocked_modules),
        )
        print(
            f"\n[*] Execution finished: {len(passed_modules)} Passed, {len(failed_modules)} Failed, {len(blocked_modules)} Blocked."
        )
        print("[*] Saved output to 'CRMLeaf PSA.xlsx'.")


if __name__ == "__main__":
    email = os.environ.get("CRMLeaf_USERNAME")
    password = os.environ.get("CRMLeaf_PASSWORD")

    if not email or not password:
        print("[!] Credentials missing. Set them before running:")
        print('    $env:CRMLeaf_USERNAME="your_email@domain.com"')
        print('    $env:CRMLeaf_PASSWORD="your_password"')
        sys.exit(1)

    engine = SafeAutonomousEngine(email=email, password=password)
    engine.run()
