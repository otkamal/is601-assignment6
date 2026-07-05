import logging
import pytest
from unittest.mock import MagicMock
from app.observer import AutoSaveSubscriber, CalculationSubscriber

def test_update_on_shutdown_saves_history():
    mock_calculator = MagicMock()
    sub = AutoSaveSubscriber()
    sub.update_on_shutdown(mock_calculator)
    mock_calculator.save_history.assert_called_once()

def test_update_on_events_not_seen_threshold():
    mock_calculator = MagicMock()
    sub = AutoSaveSubscriber()
    sub.update(mock_calculator)
    mock_calculator.save_history.assert_not_called()
    
def test_update_on_events_seen_threshold():
    mock_calculator = MagicMock()
    sub = AutoSaveSubscriber()
    sub._events_seen = 1
    sub.update(mock_calculator)
    mock_calculator.save_history.assert_called_once()

def test_update_logs_on_calculation(caplog):
    mock_calculator = MagicMock()
    sub = CalculationSubscriber()
    mock_calculator.get_last_calculation.return_value = MagicMock()
    with caplog.at_level(logging.INFO):
        sub.update(mock_calculator)
    assert "calculation performed" in caplog.text

def test_update_does_not_log_on_noop(caplog):
    mock_calculator = MagicMock()
    sub = CalculationSubscriber()
    mock_calculator.get_last_calculation.return_value = None
    with caplog.at_level(logging.INFO):
        sub.update(mock_calculator)
    assert "calculation performed" not in caplog.text
