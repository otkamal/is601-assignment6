import pytest
from app.operations import addition, subtraction, multiplication, division

def test_addition_positive():
    """Test positive cases for addition"""
    assert addition(1, 1) == 2
    assert addition(0, 0) == 0
    assert addition(2, -1) == 1

def test_addition_negative():
    """Test negative cases for addition"""
    assert addition(0, -1) == -1
    assert addition(-5, -5) == -10

def test_subtraction_positive():
    """Test positive cases for subtraction"""
    assert subtraction(1, 1) == 0
    assert subtraction(5, 1) == 4
    assert subtraction(1, 0) == 1
    assert subtraction(-1, -1) == 0

def test_subtraction_negative():
    """Test negative cases for subtraction"""
    assert subtraction(0, 1) == -1
    assert subtraction(1, 5) == -4
    assert subtraction(-1, 5) == -6

def test_multiplication_postive():
    """Test positive cases for multiplication"""
    assert multiplication(1, 1) == 1
    assert multiplication(-5, -5) == 25
    assert multiplication(4, 0) == 0

def test_multiplication_negative():
    """Test negative cases for multiplication"""
    assert multiplication(1, -1) == -1
    assert multiplication(5, -5) == -25
    assert multiplication(-7, 5) == -35

def test_division_positive():
    """Test positive cases for division"""
    assert division(5, 1) == 5
    assert division(0, 5) == 0

def test_division_negative():
    """Test negative cases for division"""
    assert division(6, -2) == -3
    assert division(-6, 2) == -3
    assert division(0, -7) == 0

def test_division_zero():
    """Test division by zero for division"""
    with pytest.raises(ZeroDivisionError, match="Error: b cannot be 0."):
        assert division(4, 0)