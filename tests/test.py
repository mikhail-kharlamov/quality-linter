import pytest
from app.func_for_test import func


def test_func():
    assert func(2, 3) == [5, 6, -1, 0]
    assert func(10, 5) == [15, 50, 5, 2]
    assert func(0, 0) == [0, 0, 0, 0]
    assert func(-1, -1) == [-2, 1, 0, 1]
    assert func(100, 0) == [100, 0, 100, 0]
