import logging
import pandas as pd
from app.memento import CalculatorMemento
from app.calculation import Calculation, CalculationFactory
from app.observer import Subscriber, CalculationSubscriber, AutoSaveSubscriber
from app.calculator_config import CalculatorConfig


class Calculator():
    """Calculator that executes operations, maintains history, and notifies subscribers.

    Initializes logging and history from disk on startup. Registers a
    CalculationSubscriber by default, and an AutoSaveSubscriber when auto-save
    is enabled in config.
    """

    def __init__(self, config: CalculatorConfig = None):
        """Initialize the calculator, logging, and history.

        Args:
            config: Configuration instance. Creates a default CalculatorConfig if not provided.
        """
        self.config = CalculatorConfig() \
            if config is None else config

        self._history: list[Calculation] = []
        self._subscribers: list[Subscriber] = []
        self._init_logging()
        self._init_history()
        self._log_config()

        self._add_subscriber(CalculationSubscriber())
        if self.config.auto_save:
            self._add_subscriber(AutoSaveSubscriber(self.config.events_before_autosave))

        self._undo_stack: list[CalculatorMemento] = []
        self._redo_stack: list[CalculatorMemento] = []

    def calculate(self, operation: str, operand_a: float, operand_b: float) -> Calculation:
        """Build, execute, and record a calculation.

        Args:
            operation: Registered operation name (e.g. 'add', 'divide').
            operand_a: First operand.
            operand_b: Second operand.

        Returns:
            The executed Calculation with result set.

        Raises:
            ValueError: If the operation is not registered.
            ZeroDivisionError: If the operation divides by zero.
        """
        op = [possible_op for possible_op in self.get_supported_operations() if operation in possible_op]
        # if the operation was not found in supported ops
        # use the provided operation and let CalculationFactory handle the issue
        # otherwise use the first operation found
        if not op:
            op = operation
        else:
            op = op[0]
        calc = CalculationFactory.build_calculation(op, operand_a, operand_b)
        calc.execute()
        self._undo_stack.append(CalculatorMemento(self))
        self._redo_stack.clear()
        if len(self._history) >= self.config.history_size:
            logging.info(f"max history size hit -> removing {self._history.pop(0)}")
        self._history.append(calc)
        self._update_subscribers()
        return calc

    def _init_logging(self) -> None:
        """Configure the root logger to write to the log file specified in config."""
        logging.basicConfig(
            filename=self.config.log_file,
            encoding=self.config.encoding,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info(f"logging initialized at {self.config.log_file}")

    def _init_history(self) -> None:
        """Load history from disk if it exists, or create an empty file if auto-save is on."""
        if self.config.history_file.exists():
            self.load_history()
        elif self.config.auto_save:
            self.config.history_file.touch()

    def _log_config(self) -> None:
        """Log all active configuration values at startup."""
        logging.info(f"history size set to {self.config.history_size}")
        logging.info(f"precision set to {self.config.precision}")
        logging.info(f"encoding set to {self.config.encoding}")
        logging.info(f"max value set to {self.config.max_value}")
        logging.info(f"auto-save set to {self.config.auto_save}")

    def _add_subscriber(self, sub: Subscriber) -> None:
        """Register a subscriber to receive calculation and shutdown events."""
        logging.info(f"adding {sub.__class__.__name__}")
        self._subscribers.append(sub)

    def load_history(self) -> None:
        """Read history CSV and populate _history, trimming to history_size if needed."""
        try:
            if self.config.history_file.stat().st_size == 0:
                logging.info("no history to load")
                return
            df = pd.read_csv(self.config.history_file, encoding=self.config.encoding)
            if len(df) > self.config.history_size:
                logging.info(f"history file has {len(df)} entries, trimming to {self.config.history_size}")
            df = df.tail(self.config.history_size)
            for _, row in df.iterrows():
                calc = CalculationFactory.from_dict(row.to_dict())
                self._history.append(calc)
            logging.info(f"loaded {len(self._history)} calculations from disk")
        except Exception as e:
            logging.error(f"could not load history: {e}")

    def get_last_calculation(self) -> Calculation:
        """Return the most recent calculation, or None if history is empty."""
        return self._history[-1] if self._history else None

    def _update_subscribers(self):
        """Notify all subscribers that a new calculation was performed."""
        for sub in self._subscribers:
            sub.update(self)
        logging.info(f"notified {len(self._subscribers)} subscribers")

    def get_history(self) -> list[Calculation]:
        """Return a copy of the current calculation history."""
        return list(self._history)

    def save_history(self) -> None:
        """Persist the current in-memory history to the configured CSV file."""
        try:
            rows = [calc.to_dict() for calc in self._history]
            df = pd.DataFrame(rows)
            df.to_csv(self.config.history_file, index=False)
            logging.info(f"saved {len(self._history)} calculations to disk")
        except Exception as e:
            logging.error(f"could not save to file {e}")

    def shutdown(self) -> None:
        """Notify all subscribers of shutdown so they can flush state to disk."""
        logging.info("calculator is shutting down. sending final notify")
        for sub in self._subscribers:
            sub.update_on_shutdown(self)

    def clear_history(self) -> None:
        """Clear the in-memory history without touching the history file."""
        self._history.clear()
        logging.info("cleared history in memory")

    @staticmethod
    def get_supported_operations():
        return CalculationFactory.get_supported_operations()

    def undo(self):
        """Revert to the history state before the most recent calculation.

        Returns:
            True if a state was restored, False if the undo stack was empty.
        """
        if not self._undo_stack:
            return False
        memento = self._undo_stack.pop()
        self._redo_stack.append(CalculatorMemento(self))
        self._history = memento.get_history()
        return True

    def redo(self):
        """Re-apply the most recently undone calculation.

        Returns:
            True if a state was restored, False if the redo stack was empty.
        """
        if not self._redo_stack:
            return False
        memento = self._redo_stack.pop()
        self._undo_stack.append(CalculatorMemento(self))
        self._history = memento.get_history()
        return True
