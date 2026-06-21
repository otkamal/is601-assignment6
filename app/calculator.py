import logging
import pandas as pd
from app.calculation import Calculation, CalculationFactory
from app.observer import Subscriber, CalculationSubscriber, AutoSaveSubscriber
from app.calculator_config import CalculatorConfig

class Calculator():

    def __init__(self, config: CalculatorConfig = None):
        self.config = CalculatorConfig() \
            if config is None else config
    
        self._history: list[Calculation] = []
        self._subscribers: list[Subscriber] = []
        self._init_logging()
        self._init_history()
        self._log_config()
        self._add_subscriber(CalculationSubscriber())
        if self.config.auto_save:
            self._add_subscriber(AutoSaveSubscriber())

    def calculate(self, operation: str, operand_a: int, operand_b: int) -> Calculation:
        calc = CalculationFactory.build_calculation(operation, operand_a, operand_b)
        calc.execute()
        if len(self._history) == self.config.history_size:
            logging.info(
                f"max history size hit -> removing {self._history.pop(0)}"
        )
        self._history.append(calc)
        self._update_subscribers()
        return calc

    def _init_logging(self) -> None:
        logging.basicConfig(
            filename=self.config.log_file,
            encoding=self.config.encoding,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info(f"logging initialized at {self.config.log_file}")

    def _init_history(self) -> None:
        if self.config.history_file.exists():
            self._load_history()
        elif self.config.auto_save:
            self.config.history_file.touch()

    def _log_config(self) -> None:
        logging.info(f"history size set to {self.config.history_size}")
        logging.info(f"precision set to {self.config.precision}")
        logging.info(f"encoding set to {self.config.encoding}")
        logging.info(f"max value set to {self.config.max_value}")
        logging.info(f"auto-save set to {self.config.auto_save}")

    def _add_subscriber(self, sub: Subscriber) -> list[Subscriber]:
        logging.info(f"adding {sub.__class__.__name__}")
        self._subscribers.append(sub)
        return self._subscribers

    def _load_history(self) -> None:
        try:
            if self.config.history_file.stat().st_size == 0:
                logging.info("no history to load")
                return
            df = pd.read_csv(self.config.history_file, encoding=self.config.encoding)
            for _, row in df.iterrows():
                calc = CalculationFactory.from_dict(row.to_dict())
                self._history.append(calc)
            logging.info(f"loaded {len(self._history)} calculations from disk")
        except Exception as e:
            logging.error(f"could not load history: {e}")

    def get_last_calculation(self) -> Calculation:
        return self._history[-1] if len(self._history) > 0 else None
    
    def _update_subscribers(self):
        for sub in self._subscribers:
            sub.update(self)
        logging.info(f"notified {len(self._subscribers)} subscribers")

    def show_history(self) -> None:
        if not self._history:
            print("No history yet.")
            return
        for i, calc in enumerate(self._history, start=1):
            print(f"{i}. {calc}")

    def save_history(self) -> None:
        try:
            rows = [calc.to_dict() for calc in self._history]
            df = pd.DataFrame(rows)
            df.to_csv(self.config.history_file, index=False)
            logging.info(f"saved {len(self._history)} calculatons to disk")
        except Exception as e:
            logging.error(f"could not save to file {e}")

    def shutdown(self) -> None:
        for sub in self._subscribers:
            sub.update_on_shutdown(self)

    def clear_history(self) -> None:
        self._history.clear()
        logging.info("cleared history in memory")
