from abc import ABC
from typing import List
from playwright.sync_api import Page


class BaseModule(ABC):
    def __init__(self, name: str = "", depends_on: List[str] = None):
        self.name = name
        self.depends_on = depends_on or []

    def run(self, page: Page, context=None):
        if (
            hasattr(self, "execute")
            and callable(self.execute)
            and type(self).execute != BaseModule.execute
        ):
            return self.execute(page, context)
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run() or execute()."
        )

    def execute(self, page: Page, context=None):
        if (
            hasattr(self, "run")
            and callable(self.run)
            and type(self).run != BaseModule.run
        ):
            return self.run(page, context)
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run() or execute()."
        )

    def validate_invariants(self, page: Page, context=None) -> bool:
        """Post-execution invariant checks. Defaults to True if not overridden."""
        return True


class ScreenModule(BaseModule):
    def __init__(self, name: str = "", depends_on: List[str] = None):
        super().__init__(name=name, depends_on=depends_on)
