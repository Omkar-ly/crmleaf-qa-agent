from dataclasses import dataclass
from typing import Optional


@dataclass
class Finding:
    module: str
    screen: str
    failure_type: str  # 'ProductDefect', 'EnvironmentError', 'ScriptError'
    severity: str  # 'Critical', 'Major', 'Minor', 'Low'
    title: str
    repro_steps: str
    expected: str
    actual: str
    target_locator: str = ""
    normalized_reason: str = ""
    screenshot_path: Optional[str] = None
    video_path: Optional[str] = None
    trace_path: Optional[str] = None
    console_log_path: Optional[str] = None


@dataclass
class StepResult:
    screen_name: str
    status: str  # 'Pass', 'Fail', 'Blocked'
    finding: Optional[Finding] = None
    duration_sec: float = 0.0
