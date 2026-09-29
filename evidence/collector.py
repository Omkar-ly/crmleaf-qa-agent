import json
from pathlib import Path
from typing import Any
from playwright.sync_api import Page


class EvidenceCollector:
    def __init__(
        self, run_id: str = None, evidence_dir: str | Path = "evidence_output", **kwargs
    ):
        self.run_id = run_id
        base_dir = Path(evidence_dir)
        self.evidence_dir = base_dir / run_id if run_id else base_dir
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def capture_screenshot(self, page: Page, name: str) -> Path | None:
        if page is None or page.is_closed():
            return None

        clean_name = str(name).strip().rstrip("._-")
        if not clean_name:
            clean_name = "screenshot"
        if not clean_name.lower().endswith((".png", ".jpg", ".jpeg")):
            clean_name = f"{clean_name}.png"

        target = self.evidence_dir / clean_name
        try:
            page.screenshot(path=str(target), full_page=True)
            return target
        except Exception:
            return None

    def take_screenshot(self, page: Page, name: str) -> Path | None:
        return self.capture_screenshot(page, name)

    def dump_logs(self, *args, **kwargs) -> Path:
        module_name = "diagnostics"
        logs = None

        if len(args) == 1:
            logs = args[0]
        elif len(args) >= 2:
            module_name = str(args[0]).strip().rstrip("._-") or "diagnostics"
            logs = args[1:]

        target = self.evidence_dir / f"{module_name}_diagnostics.log"
        content = ""
        if isinstance(logs, (dict, list, tuple)):
            content = json.dumps(logs, indent=2, default=str)
        elif logs is not None:
            content = str(logs)
        else:
            content = json.dumps(kwargs, indent=2, default=str)

        target.write_text(content, encoding="utf-8")
        return target

    def get_video_path(self, page: Page, module_name: str) -> Path | None:
        target = self.evidence_dir / f"{module_name}.webm"

        if not page.is_closed():
            page.close()

        video = page.video
        if video:
            video.save_as(str(target))
            return target
        return None
