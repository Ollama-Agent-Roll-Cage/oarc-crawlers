from oarc_crawlers.config.config_validators import NumberValidator, PathValidator
import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError

def test_number_validator_valid():
    validator = NumberValidator()
    doc = Document("5")
    # Should not raise
    validator.validate(doc, min_val=1, max_val=10)

def test_number_validator_invalid():
    validator = NumberValidator()
    doc = Document("abc")
    with pytest.raises(ValidationError):
        validator.validate(doc, min_val=1, max_val=10)

def test_number_validator_out_of_range():
    validator = NumberValidator()
    doc = Document("0")
    with pytest.raises(ValidationError):
        validator.validate(doc, min_val=1, max_val=10)

def test_path_validator_valid():
    validator = PathValidator()
    doc = Document("some/path")
    # Should not raise
    validator.validate(doc)

def test_path_validator_empty():
    validator = PathValidator()
    doc = Document("")
    with pytest.raises(ValidationError):
        validator.validate(doc)
