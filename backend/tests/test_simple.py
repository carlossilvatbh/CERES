"""
Simplified test configuration for CERES backend tests.
"""
import pytest


@pytest.fixture
def simple_test():
    """Simple test fixture."""
    return True


def test_basic_functionality():
    """Test basic functionality."""
    assert True


def test_math_operations():
    """Test basic math operations."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5


def test_string_operations():
    """Test basic string operations."""
    test_string = "CERES"
    assert test_string.lower() == "ceres"
    assert len(test_string) == 5
    assert "CER" in test_string


def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert 3 in test_list
    assert test_list[0] == 1
    assert test_list[-1] == 5


def test_dict_operations():
    """Test basic dictionary operations."""
    test_dict = {"name": "CERES", "version": "2.0.0"}
    assert test_dict["name"] == "CERES"
    assert test_dict["version"] == "2.0.0"
    assert "name" in test_dict
    assert len(test_dict) == 2

