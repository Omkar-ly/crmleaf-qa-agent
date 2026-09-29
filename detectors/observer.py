from typing import List, Dict
from playwright.sync_api import Page, Response, Error


class DOMAndNetworkObserver:
    def __init__(self, page: Page):
        self.page = page
        self.network_errors: List[Dict[str, str]] = []
        self.console_errors: List[str] = []
        self.page_errors: List[str] = []
        self._attach()

    def _attach(self):
        self.page.on("response", self._handle_response)
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_pageerror)

    def _handle_response(self, response: Response):
        if response.status >= 400:
            self.network_errors.append(
                {
                    "url": response.url,
                    "status": str(response.status),
                    "status_text": response.status_text,
                }
            )

    def _handle_console(self, msg):
        if msg.type == "error":
            self.console_errors.append(msg.text)

    def _handle_pageerror(self, exc: Error):
        self.page_errors.append(str(exc))

    def clear(self):
        self.network_errors.clear()
        self.console_errors.clear()
        self.page_errors.clear()
