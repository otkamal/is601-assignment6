from app.calculator_config import CalculatorConfig

def test_singleton():
    c1 = CalculatorConfig()
    c2 = CalculatorConfig()
    assert c1 is c2

def test_setup_directories():
    c1 = CalculatorConfig()
    c1.setup_directories()
    assert c1.history_directory.exists()
    assert c1.log_directory.exists()
