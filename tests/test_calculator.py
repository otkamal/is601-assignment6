import os
import pandas as pd
import pytest
import logging
from unittest.mock import MagicMock, patch
from app.calculator import Calculator
from app.calculation import CalculationFactory
from app.calculator_config import CalculatorConfig
from app.observer import CalculationSubscriber, AutoSaveSubscriber

@pytest.fixture(autouse=True)
def reset_singleton():
    CalculatorConfig._instance = None
    yield
    CalculatorConfig._instance = None

@pytest.fixture(autouse=True)
def config(tmp_path, reset_singleton):
    (tmp_path / "logs").mkdir()
    (tmp_path / "history").mkdir()
    with patch.dict(os.environ, {
        'CALCULATOR_AUTO_SAVE': 'false',
        'CALCULATOR_BASE_DIR': str(tmp_path),
        'CALCULATOR_LOG_DIR': str(tmp_path / "logs"),
        'CALCULATOR_HIST_DIR': str(tmp_path / "history"),
        'CALCULATOR_HISTORY_FILE': str(tmp_path / "history"/ "history.csv"),
        "CALCULATOR_LOG_FILE": str(tmp_path / "logs" / "calculator.log")
    }):
        yield CalculatorConfig()

@pytest.fixture
def calculator(config):
    return Calculator(config)

def test_default_config_when_none_provided():
    assert Calculator(None).config is not None

def test_provided_config_is_used(calculator, config):
    assert calculator.config is config

def test_history_is_initially_empty(calculator):
    assert calculator.get_history() == []

def test_calcsubscriber_is_subscribed(calculator):
    assert any(isinstance(s, CalculationSubscriber) for s in calculator._subscribers)

def test_autosave_subscriber_subscribed_when_enabled(config, tmp_path):
    config.auto_save = True
    calc = Calculator(config)
    assert any(isinstance(s, AutoSaveSubscriber) for s in calc._subscribers)

def test_autosave_subscriber_not_subscribed_when_not_enabled(calculator):
    assert not any(isinstance(s, AutoSaveSubscriber) for s in calculator._subscribers)

def test_calculate_when_valid(calculator):
    calc = calculator.calculate('add', 1, 2)
    assert calc.result == 3

def test_raises_with_unknown_operation(calculator):
    with pytest.raises(ValueError):
        calculator.calculate('permutations', 5, 2)

def test_raises_when_divide_by_zero(calculator):
    with pytest.raises(ZeroDivisionError):
        calculator.calculate('divide', 5, 0)

def test_raises_when_max_value_a():
    c = Calculator()
    c.config.max_value = 5
    with pytest.raises(ValueError):
        c.calculate('add', 6, 2)

def test_raises_when_max_value_b():
    c = Calculator()
    c.config.max_value = 5
    with pytest.raises(ValueError):
        c.calculate('add', 2, 6)

def test_calculate_adds_to_history(calculator):
    calculator.calculate('add', 1, 2)
    assert len(calculator.get_history()) == 1

def test_history_rolls_over(calculator):
    calculator.config.history_size = 2
    for i in range(5):
        calculator.calculate('add', i, i)
    history = calculator.get_history()
    assert len(history) == 2
    assert history[0].operand_a == 3

def test_init_history_creates_file_with_autosave(config):
    config.auto_save = True
    c = Calculator(config)
    assert c.config.history_file.exists()

def test_init_history_does_not_create_file_without_autosave(config):
    assert not config.history_file.exists()

def test_init_history_loads_existing_file(config):
    config.history_file.parent.mkdir(parents=True, exist_ok=True)
    config.history_file.touch()
    config.history_file.write_text(
        "operation,operand_a,operand_b,result\n"
        "add,1.0,1.0,2.0\n",
        encoding=config.encoding
    )
    c = Calculator(config)
    assert len(c.get_history()) == 1

def test_load_history_empty(config):
    config.history_file.parent.mkdir(parents=True, exist_ok=True)
    config.history_file.touch()
    c = Calculator(config)
    assert c.get_history() == []

def test_load_history_nonempty(config):
    config.history_size = 2
    config.history_file.parent.mkdir(parents=True, exist_ok=True)
    config.history_file.touch()
    config.history_file.write_text(
        "operation,operand_a,operand_b,result\n"
        "add,1.0,1.0,2.0\n"
        "add,2.0,2.0,4.0\n"
        "add,3.0,3.0,6.0\n",
        encoding=config.encoding
    )
    c = Calculator(config)
    assert len(c.get_history()) == 2
    assert c.get_history()[0].operand_a == 2

def test_save_history_creates_file(calculator, config):
    calculator.calculate('add', 1, 2)
    calculator.save_history()
    assert config.history_file.exists()

def test_save_history_writes_content(calculator, config):
    calculator.calculate('add', 1, 2)
    calculator.save_history()
    df = pd.read_csv(config.history_file)
    assert len(df) == 1
    assert df.iloc[0]['operation'] == 'add'
    assert df.iloc[0]['operand_a'] == 1
    assert df.iloc[0]['operand_b'] == 2
    assert df.iloc[0]['result'] == 3

def test_save_history_empty(calculator, config):
    calculator.save_history()
    assert config.history_file.stat().st_size <= 1

def test_save_history_logs_on_error(calculator, caplog):
    with patch('pandas.DataFrame.to_csv', side_effect=PermissionError("no access")):
        with caplog.at_level(logging.ERROR):
            calculator.save_history()
    assert "could not save" in caplog.text

def test_load_history_logs_on_error(calculator, caplog):
    with patch('pandas.read_csv', side_effect=PermissionError("no access")):
        with caplog.at_level(logging.ERROR):
            calculator.load_history()
    assert "could not load" in caplog.text

def test_clear_history(calculator):
    for i in range(5):
        calculator.calculate('add', i, i)
    calculator.clear_history()
    assert len(calculator.get_history()) == 0

def test_shutdown_notifies_subscribers(calculator):
    mock_sub1 = MagicMock()
    mock_sub2 = MagicMock()
    calculator._add_subscriber(mock_sub1)
    calculator._add_subscriber(mock_sub2)
    calculator.shutdown()
    mock_sub1.update_on_shutdown.assert_called_once_with(calculator)
    mock_sub2.update_on_shutdown.assert_called_once_with(calculator)

def test_get_supported_operations(calculator):
    ops = calculator.get_supported_operations()
    dummy_calculation = CalculationFactory.get_supported_operations()
    for op in ops:
        assert op in dummy_calculation

def test_no_undo_on_new_calculator():
    c = Calculator()
    assert not c.undo()

def test_no_redo_on_new_calculator():
    c = Calculator()
    assert not c.redo()

def test_undo_on_single_calculation(calculator):
    init_history = calculator.get_history()
    calculator.calculate('add', 1, 1)
    calculator.undo()
    assert len(calculator.get_history()) == len(init_history)

def test_undo_on_stack(calculator):
    calculator.calculate('add', 1, 1)
    calculator.calculate('subtract', 1, 1)
    calculator.undo()
    assert len(calculator.get_history()) == 1
    calculator.undo()
    assert len(calculator.get_history()) == 0

def test_redo_on_single_calculation(calculator):
    calculator.calculate('add', 1, 1)
    h = calculator.get_history()
    calculator.undo()
    calculator.redo()
    assert len(h) == len(calculator.get_history())
    