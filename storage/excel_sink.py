import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from core.models import Finding


class ExcelTicketSink:
    def __init__(self, file_path: str = "CRMLeaf PSA.xlsx"):
        self.file_path = Path(file_path)
        self._init_workbook()

    def _init_workbook(self):
        if not self.file_path.exists():
            wb = Workbook()
            ws_tickets = wb.active
            ws_tickets.title = "Tickets"
            ws_tickets.append(
                [
                    "Ticket ID",
                    "Fingerprint",
                    "Run ID",
                    "Module",
                    "Screen",
                    "Severity",
                    "Failure Type",
                    "Title",
                    "Repro Steps",
                    "Expected",
                    "Actual",
                    "Screenshot",
                    "Video",
                    "Diagnostics Log",
                    "First Seen",
                    "Last Seen",
                    "Occurrences",
                    "Status",
                ]
            )
            self._style_header(ws_tickets)

            ws_runs = wb.create_sheet(title="Runs")
            ws_runs.append(
                [
                    "Run ID",
                    "Timestamp",
                    "Total",
                    "Passed",
                    "Failed",
                    "Blocked",
                    "Status",
                ]
            )
            self._style_header(ws_runs)

            ws_supp = wb.create_sheet(title="Suppressions")
            ws_supp.append(["Fingerprint", "Reason", "Added On"])
            self._style_header(ws_supp)

            wb.save(self.file_path)

    def _style_header(self, ws):
        fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        for cell in ws[1]:
            cell.fill = fill
            cell.font = font
            cell.alignment = Alignment(horizontal="center", vertical="center")

    def _compute_fingerprint(self, finding: Finding) -> str:
        raw = f"{finding.module}_{finding.screen}_{finding.failure_type}_{finding.target_locator}_{finding.normalized_reason}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def sync_finding(self, finding: Finding, run_id: str) -> None:
        fingerprint = self._compute_fingerprint(finding)

        wb_ro = load_workbook(self.file_path, read_only=True)
        ws_supp = wb_ro["Suppressions"]
        for row in ws_supp.iter_rows(min_row=2, values_only=True):
            if row and row[0] == fingerprint:
                wb_ro.close()
                return
        wb_ro.close()

        backup_path = self.file_path.with_suffix(".bak")
        shutil.copyfile(self.file_path, backup_path)

        try:
            wb = load_workbook(self.file_path)
            ws = wb["Tickets"]
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing_row = None

            for r in range(2, ws.max_row + 1):
                if ws.cell(row=r, column=2).value == fingerprint:
                    existing_row = r
                    break

            if existing_row:
                ws.cell(row=existing_row, column=16, value=now_str)
                count = ws.cell(row=existing_row, column=17).value or 1
                ws.cell(row=existing_row, column=17, value=count + 1)
                curr_status = ws.cell(row=existing_row, column=18).value
                if curr_status != "Not a bug":
                    ws.cell(row=existing_row, column=18, value="Reproduced")
            else:
                ticket_id = f"PSA-{ws.max_row:04d}"
                ss_cell = (
                    f'=HYPERLINK("{finding.screenshot_path}", "Screenshot")'
                    if finding.screenshot_path
                    else ""
                )
                vid_cell = (
                    f'=HYPERLINK("{finding.video_path}", "Video")'
                    if finding.video_path
                    else ""
                )
                log_cell = (
                    f'=HYPERLINK("{finding.console_log_path}", "Logs")'
                    if finding.console_log_path
                    else ""
                )

                ws.append(
                    [
                        ticket_id,
                        fingerprint,
                        run_id,
                        finding.module,
                        finding.screen,
                        finding.severity,
                        finding.failure_type,
                        finding.title,
                        finding.repro_steps,
                        finding.expected,
                        finding.actual,
                        ss_cell,
                        vid_cell,
                        log_cell,
                        now_str,
                        now_str,
                        1,
                        "Draft",
                    ]
                )

            wb.save(self.file_path)
        except PermissionError:
            print(
                f"[!] Warning: '{self.file_path}' is open in Excel. Written to backup: {backup_path}"
            )

    def log_run(
        self, run_id: str, total: int, passed: int, failed: int, blocked: int
    ) -> None:
        try:
            wb = load_workbook(self.file_path)
            ws = wb["Runs"]
            status = "PASSED" if failed == 0 and blocked == 0 else "FAILED"
            ws.append(
                [
                    run_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    total,
                    passed,
                    failed,
                    blocked,
                    status,
                ]
            )
            wb.save(self.file_path)
        except PermissionError:
            pass
