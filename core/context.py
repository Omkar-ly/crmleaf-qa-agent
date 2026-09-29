from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class RunContext:
    run_id: str
    base_url: str = "https://www.crmleaf.com"
    data: Dict[str, Any] = field(default_factory=dict)

    unique_suffix: str = field(default_factory=lambda: str(int(time.time()))[-6:])
    lead_name: Optional[str] = None
    lead_email: Optional[str] = None
    company_name: Optional[str] = None
    deal_name: Optional[str] = None
    proposal_id: Optional[str] = None
    client_name: Optional[str] = None
    client_id: Optional[str] = None
    quote_number: Optional[str] = None
    contract_subject: Optional[str] = None
    contract_number: Optional[str] = None
    project_name: Optional[str] = None
    project_id: Optional[str] = None
    task_name: Optional[str] = None
    milestone_name: Optional[str] = None

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
