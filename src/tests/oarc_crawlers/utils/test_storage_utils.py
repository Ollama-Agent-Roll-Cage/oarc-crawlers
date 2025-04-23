"""Tests for the storage_utils module."""
import pytest
from oarc_crawlers.utils.storage_utils import StorageUtils


class SampleObject:
    """Simple test object with attributes."""
    def __init__(self):
        self.name = "test"
        self.value = 10


class SampleObjectWithToDict:
    """Test object with to_dict method."""
    def __init__(self):
        self.name = "test_dict"
        self.value = 20
        
    def to_dict(self):
        return {"name": self.name, "value": self.value}


def test_convert_to_dict_with_dict_object():
    """Test converting a dictionary to dictionary."""
    test_dict = {"name": "test", "value": 10}
    result = StorageUtils.convert_to_dict(test_dict)
    assert result == test_dict
    assert isinstance(result, dict)


def test_convert_to_dict_with_object():
    """Test converting an object with __dict__ to dictionary."""
    test_obj = SampleObject()
    result = StorageUtils.convert_to_dict(test_obj)
    assert result == {"name": "test", "value": 10}
    assert isinstance(result, dict)


def test_convert_to_dict_with_to_dict_method():
    """Test converting an object with to_dict method."""
    test_obj = SampleObjectWithToDict()
    result = StorageUtils.convert_to_dict(test_obj)
    assert result == {"name": "test_dict", "value": 20}
    assert isinstance(result, dict)


def test_convert_to_dict_with_invalid_type():
    """Test converting an object that can't be converted to dictionary."""
    with pytest.raises(TypeError) as excinfo:
        StorageUtils.convert_to_dict(5)
    assert "Cannot convert" in str(excinfo.value)
