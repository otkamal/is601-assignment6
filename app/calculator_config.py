import os
from decimal import Decimal
from pathlib import Path

class CalculatorConfig:
    """Singleton configuration for the calculator application.

    Reads settings from environment variables on first instantiation, falling
    back to the class-level defaults. Subsequent instantiations return the same
    object unchanged.

    Environment variables:
        CALCULATOR_BASE_DIR: Project root directory.
        CALCULATOR_MAX_HISTORY_SIZE: Maximum number of history entries (int).
        CALCULATOR_AUTO_SAVE: Whether to auto-save history ('true'/'false').
        CALCULATOR_PRECISION: Decimal places for calculations (int).
        CALCULATOR_MAX_INPUT_VALUE: Maximum allowed input value (Decimal).
        CALCULATOR_DEFAULT_ENCODING: File encoding (e.g. 'utf-8').
        CALCULATOR_LOG_DIR: Directory for log files.
        CALCULATOR_HIST_DIR: Directory for history files.
        CALCULATOR_HISTORY_FILE: Path to the history CSV file.
    """

    _instance = None
    _DEF_MAX_HIST_SIZE = '100'
    _DEF_DO_AUTO_SAVE = 'true'
    _DEF_PRECISION = '5'
    _DEF_MAX_VALUE = '1000'
    _DEF_ENCODING = 'utf-8'
    _DEF_BASE_DIR = str(Path(__file__).parent.parent)
    _DEF_LOG_DIR = str(Path(_DEF_BASE_DIR) / "logs")
    _DEF_HIST_DIR = str(Path(_DEF_BASE_DIR) / "history")
    _DEF_HIST_FILE = str(Path(_DEF_HIST_DIR) / "history.csv")

    def __new__(cls, *args, **kwargs):
        """Return the existing instance or create one if none exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration from environment variables and defaults.

        No-ops on subsequent calls so the singleton state is never overwritten.
        """
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True

        self.base_directory = Path(os.getenv('CALCULATOR_BASE_DIR', self._DEF_BASE_DIR))
        self.history_size = int(os.getenv('CALCULATOR_MAX_HISTORY_SIZE', self._DEF_MAX_HIST_SIZE))
        self.auto_save = os.getenv('CALCULATOR_AUTO_SAVE', self._DEF_DO_AUTO_SAVE).lower() == 'true'
        self.precision = int(os.getenv('CALCULATOR_PRECISION', self._DEF_PRECISION))
        self.max_value = Decimal(os.getenv('CALCULATOR_MAX_INPUT_VALUE', self._DEF_MAX_VALUE))
        self.encoding = os.getenv('CALCULATOR_DEFAULT_ENCODING', self._DEF_ENCODING)
        self.log_directory = Path(os.getenv('CALCULATOR_LOG_DIR', self._DEF_LOG_DIR))
        self.history_directory = Path(os.getenv('CALCULATOR_HIST_DIR', self._DEF_HIST_DIR))
        self.history_file = Path(os.getenv('CALCULATOR_HISTORY_FILE', self._DEF_HIST_FILE))
