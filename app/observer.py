import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.calculator import Calculator


class Subscriber(ABC):
    """Abstract base class for calculator event subscribers."""

    @abstractmethod
    def update(self, calculator: "Calculator"):
        """Called after each calculation is performed."""

    def update_on_shutdown(self, calculator: "Calculator"):
        """Called when the calculator shuts down. Override to handle cleanup."""


class CalculationSubscriber(Subscriber):
    """Logs each calculation to the application log."""

    def update(self, calculator: "Calculator"):
        """Log the most recent calculation result."""
        c = calculator.get_last_calculation()
        if c is not None:
            logging.info(f"calculation performed -> {c}")

    def update_on_shutdown(self, calculator: "Calculator"):     # pragma: no cover
        pass                                                    # pragma: no cover


class AutoSaveSubscriber(Subscriber):
    """Persists history to disk when the calculator shuts down."""

    _events_seen = 0
    def __init__(self, events_before_autosave: int = 1):
        self._events_before_autosave = events_before_autosave

    def update(self, calculator: "Calculator"):   
        self._events_seen += 1
        if self._events_seen > self._events_before_autosave:
            calculator.save_history()
            self._events_seen = 0

    def update_on_shutdown(self, calculator: "Calculator"):
        """Save the current history to the configured CSV file."""
        calculator.save_history()
