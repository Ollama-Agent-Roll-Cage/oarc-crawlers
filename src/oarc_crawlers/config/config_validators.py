"""
Validators for OARC Crawlers configuration editor.

This module defines reusable validation classes for interactive configuration input,
ensuring user-provided values are correct and within expected constraints.
"""

from prompt_toolkit.validation import ValidationError, Validator

from oarc_utils.decorators import singleton


@singleton
class NumberValidator(Validator):
    """Validator for integer inputs within a range."""


    def validate(self, document, min_val=0, max_val=100):
        """
        Validate that input is a number within the specified range.

        Args:
            document: prompt_toolkit Document object containing user input.
            min_val (int): Minimum allowed value (inclusive).
            max_val (int): Maximum allowed value (inclusive).

        Raises:
            ValidationError: If input is not a valid integer or out of range.
        """
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
        """
        Validates that the provided document contains a non-empty, plausible path string.

        Args:
            document (prompt_toolkit.document.Document): The document object containing the user input to validate.

        Raises:
            ValidationError: If the input path string is empty or contains only whitespace.
        """
        path_str = document.text
        if not path_str.strip():
            raise ValidationError(
                message='Path cannot be empty',
                cursor_position=len(document.text)
            )
