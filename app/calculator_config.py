import os
from decimal import Decimal
from pathlib import Path

class CalculatorConfig:

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
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        
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
