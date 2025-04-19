"""
Validation classes for OARC Crawlers configuration.

This module provides validators used for validating configuration inputs
in the interactive configuration editor.
"""

from prompt_toolkit.validation import ValidationError, Validator
from oarc_crawlers.decorators.singleton import singleton


@singleton
class NumberValidator(Validator):
    """Validator for integer inputs within a range."""


    def validate(self, document, min_val=0, max_val=100):
        """Validate that input is a number within the specified range."""
        try:
            value = int(document.text)
            if value < min_val or value > max_val:
                raise ValidationError(
                    message=f'Please enter a number between {min_val} and {max_val}',
                    cursor_position=len(document.text)
                )
        except ValueError:
            raise ValidationError(
                message='Please enter a valid number',
                cursor_position=len(document.text)
            )


@singleton
class PathValidator(Validator):
    """Validator for path inputs."""

    def validate(self, document):
        """Validate that input is a non-empty path string."""
        path_str = document.text
        if not path_str.strip():
            raise ValidationError(
                message='Path cannot be empty',
                cursor_position=len(document.text)
            )
