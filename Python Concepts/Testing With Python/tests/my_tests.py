import source.my_functions as my_functions
import pytest

def test_add():
    result = my_functions.add_number(1,2)
    assert result == 3

def test_add_strings():
    result = my_functions.add_number("I like", " burgers")
    assert result == "I like burgers"


def test_divide():
    assert 5 == my_functions.divide_number(10, 2)

def test_divide_by_zero():
    # expecting an division error - that is the expected case, if it does not match then fail
    with pytest.raises(ZeroDivisionError):
        result = my_functions.divide_number(10, 0)

