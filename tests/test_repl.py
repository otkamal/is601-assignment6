import pytest
from unittest.mock import MagicMock
from app.repl import start_repl

@pytest.mark.parametrize(
        "bad_input", [
            "add 1",
            "add 1 2 3",
            "add 1 one",
            "notanop"
        ],
        ids=[
            "too_few_args",
            "too_many_args",
            "non_numeric_input",
            "invalid_single_word_op"
        ]
)
def test_invalid_operation(bad_input, monkeypatch, capsys):
    mock_calculator = MagicMock()
    inputs = iter([bad_input, "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    start_repl(mock_calculator)
    output = capsys.readouterr().out

    assert "Error:" in output
    mock_calculator.calculate.assert_not_called()

@pytest.mark.parametrize(
        "input", [
            "add 1 1",
            "subtract 1 1",
            "multiply 1 1",
            "divide 1 1"
        ],
        ids=[
            "do_add",
            "do_subtract",
            "do_multiply",
            "do_divide"
        ]
)
def test_valid_operations(input, monkeypatch, capsys):
    mock_calculator = MagicMock()
    inputs = iter([input, "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    start_repl(mock_calculator)
    assert "Result:" in capsys.readouterr().out

def test_division_by_zero(monkeypatch, capsys):
    mock_calculator = MagicMock()
    mock_calculator.calculate.side_effect = ZeroDivisionError("b cannot be 0")
    inputs = iter(["divide 1 0", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    start_repl(mock_calculator)
    assert "Error:" in capsys.readouterr().out

def test_save_history(monkeypatch, capsys):
    mock_calculator = MagicMock()
    inputs = iter(["save", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    start_repl(mock_calculator)
    mock_calculator.save_history.assert_called_once()
    assert "History saved to disk." in capsys.readouterr().out

def test_clear_history(monkeypatch, capsys):
    mock_calculator = MagicMock()
    inputs = iter(["clear", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    start_repl(mock_calculator)
    mock_calculator.clear_history.assert_called_once()
    assert "History has been cleared." in capsys.readouterr().out

def test_get_no_history(monkeypatch, capsys):
    mock_calculator = MagicMock()
    mock_calculator.get_history.return_value = []
    inputs = iter(["history", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    start_repl(mock_calculator)
    mock_calculator.get_history.assert_called_once()
    assert "No history yet" in capsys.readouterr().out

def test_get_history(monkeypatch, capsys):
    mock_calculator = MagicMock()
    mock_calc = MagicMock()
    mock_calc.__str__ = lambda self: "1. Addition(a = 1.0, b = 1.0, result = 2.0)"
    mock_calculator.get_history.return_value = [mock_calc]
    inputs = iter(["history", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    start_repl(mock_calculator)
    mock_calculator.get_history.assert_called_once()
    assert "1. Addition(a = 1.0, b = 1.0, result = 2.0)" in capsys.readouterr().out

def test_load_history():
    pass

def test_undo_history():
    pass

def test_redo_history():
    pass

def test_help():
    pass