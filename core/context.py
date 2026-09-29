import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class RunContext:
    run_id: str
    base_url: str = "https://www.crmleaf.com"
    data: Dict[str, Any] = field(default_factory=dict)

    # Unique identifier suffix generated per run to avoid collision
    unique_suffix: str = field(default_factory=lambda: str(int(time.time()))[-6:])

    # Upstream entity tracking
    lead_name: Optional[str] = None
    lead_email: Optional[str] = None
    company_name: Optional[str] = None
    deal_name: Optional[str] = None
    deal_id: Optional[str] = None
    proposal_id: Optional[str] = None
    client_name: Optional[str] = None
    client_id: Optional[str] = None
    quote_number: Optional[str] = None
    quote_id: Optional[str] = None
    contract_subject: Optional[str] = None
    contract_number: Optional[str] = None
    contract_id: Optional[str] = None

    # Project lifecycle tracking
    project_name: Optional[str] = None
    project_id: Optional[str] = None
    milestone_name: Optional[str] = None
    task_name: Optional[str] = None
    task_id: Optional[str] = None

    # Integrated modules tracking (Task Board, Timesheet, Expenses, Invoices, Payment)
    timesheet_memo: Optional[str] = None
    expense_name: Optional[str] = None
    expense_id: Optional[str] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


# Alias to satisfy modules or runners expecting AutomationContext
AutomationContext = RunContext
