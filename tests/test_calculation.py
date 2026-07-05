import pytest
from app.calculation import Calculation, CalculationFactory

@pytest.mark.parametrize(
    "op, a, b, expected",
    [
        ("add", 5, 10, 15),
        ("subtract", 17, 7, 10),
        ("divide", 10, 2, 5),
        ("multiply", 3, 3, 9),
        ("power", 5, 2, 25),
        ("modulus", 5, 3, 2),
        ("percent", 1, 2, 50),
        ("abs", 5, 3, 2),
        ("ADD", 4, 2, 6),
    ],
    ids=[
        "factory_add",
        "factory_subtract",
        "factory_divide",
        "factory_multiply",
        "factory_power",
        "factory_modulus",
        "factory_percent",
        "factory_abs",
        "factory_add_case_insensitive",
    ]
)
def test_factory_build_and_execute(op: str, a: float, b: float, expected: float) -> None:
    calculation = CalculationFactory.build_calculation(op, a, b)
    result = calculation.execute()
    assert result == expected, f"Expected {op}({a}, {b}) = {expected}. Got {result}."

@pytest.mark.parametrize(
    "op, a, b, expected",
    [
        ("add", 5, 10, "Addition(a = 5, b = 10, result = None)"),
        ("subtract", 5, 10, "Subtraction(a = 5, b = 10, result = None)"),
        ("multiply", 5, 10, "Multiplication(a = 5, b = 10, result = None)"),
        ("divide", 5, 10, "Division(a = 5, b = 10, result = None)"),
        ("power", 5, 2, "Power(a = 5, b = 2, result = None)"),
        ("modulus", 5, 2, "Modulus(a = 5, b = 2, result = None)")
    ],
    ids=
    [
        "string_add",
        "string_subtract",
        "string_multiply",
        "string_divide",
        "string_power",
        "string_modulus"
    ]
)
def test_calculation_string(op: str, a: float, b: float, expected: str) -> None:
    calculation = CalculationFactory.build_calculation(op, a, b)
    assert str(calculation) == expected, f"Expected {op}({a}, {b}) = {expected}. Got {str(calculation)}."

@pytest.mark.parametrize(
    "op, a, b, expected",
    [
        ("add", 5, 10, "Addition: operand_a = 5, operand_b = 10, result = None"),
        ("subtract", 5, 10, "Subtraction: operand_a = 5, operand_b = 10, result = None"),
        ("multiply", 5, 10, "Multiplication: operand_a = 5, operand_b = 10, result = None"),
        ("divide", 5, 10, "Division: operand_a = 5, operand_b = 10, result = None"),
        ("power", 5, 10, "Power: operand_a = 5, operand_b = 10, result = None"),
        ("modulus", 5, 2, "Modulus: operand_a = 5, operand_b = 2, result = None")
    ],
    ids=[
        "repr_add",
        "repr_subtract",
        "repr_multiply",
        "repr_divide",
        "repr_power",
        "repr_modulus"
    ]
)
def test_calculation_repr(op: str, a: float, b: float, expected: str) -> None:
    calculation = CalculationFactory.build_calculation(op, a, b)
    assert repr(calculation) == expected, f"Expected {op}({a}, {b}) = {expected}. Got {repr(calculation)}."

def test_duplicate_registration() -> None:
    with pytest.raises(ValueError, match="add is already registered."):
        @CalculationFactory.register_calculation('add')
        class Adddition(Calculation):
            def execute(self) -> float:
                return 0

def test_unsupported_operation() -> None:
    with pytest.raises(ValueError, match="is not a supported operation."):
        CalculationFactory.build_calculation("percent", 5, 100)

def test_faactory_division_by_zero() -> None:
    with pytest.raises(ZeroDivisionError, match="b cannot be 0."):
        CalculationFactory.build_calculation("divide", 10, 0).execute()

def test_supported_operations_list() -> None:
    factory = CalculationFactory()
    for op in ('add', 'subtract', 'multiply', 'divide', 'power', 'modulus'):
        assert op in factory.get_supported_operations(), f"{op} does not seem to be supported"

@pytest.mark.parametrize(
    "operation, a, b, expected", [
        ("add", 1, 2, 3),
        ("subtract", 5, 3, 2),
        ("multiply", 4, 5, 20),
        ("divide", 10, 2, 5)
    ],
    ids=[
        "to_add_dict",
        "to_subtract_dict",
        "to_multiply_dict",
        "to_divide_dict"
    ]
)
def test_to_dict(operation, a, b, expected):
    calc = CalculationFactory.build_calculation(operation, a, b)
    calc.execute()
    d = calc.to_dict()
    assert d["operation"] == operation
    assert d["operand_a"] == a
    assert d["operand_b"] == b
    assert d["result"] == expected

def test_from_dict():
    d = {
        "operation": "add",
        "operand_a": 1,
        "operand_b": 1,
        "result": 2
    }
    calc = CalculationFactory.from_dict(d)
    assert calc.operand_a == 1
    assert calc.operand_b == 1
    assert calc.result == 2

def test_dict_round_trip():
    calc = CalculationFactory.build_calculation("add", 1, 1)
    calc.execute()
    restored = CalculationFactory.from_dict(calc.to_dict())
    assert restored.operand_a == calc.operand_a
    assert restored.operand_b == calc.operand_b
    assert restored.result == calc.result
    