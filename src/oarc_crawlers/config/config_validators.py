"""
Validators for OARC Crawlers configuration editor.

This module defines reusable validation classes for interactive configuration input,
ensuring user-provided values are correct and within expected constraints.
"""

from prompt_toolkit.validation import ValidationError, Validator

from oarc_utils.decorators import singleton


@singleton
class NumberValidator(Validator):
    """
    Validates that input is a valid number within an optional range.
    
    Provides validation for integer and float inputs with customizable
    minimum and maximum value constraints.
    """
    
    def validate(self, document, min_val=None, max_val=None):
        """
        Validate that the input is a valid number within specified bounds.
        
        Args:
            document: Input document or string to validate
            min_val: Minimum allowed value (optional)
            max_val: Maximum allowed value (optional)
            
        Returns:
            bool: True if valid
            
        Raises:
            ValidationError: If the input is not a valid number or outside bounds
        """
        # Handle both document objects and direct string inputs
        text = document.text if hasattr(document, 'text') else document
        
        try:
            value = int(text)
            if min_val is not None and value < min_val:
                raise ValidationError(
                    message=f"Value must be at least {min_val}",
                    cursor_position=len(text)
                )
            if max_val is not None and value > max_val:
                raise ValidationError(
                    message=f"Value must be at most {max_val}",
                    cursor_position=len(text)
                )
        except ValueError:
            min_max = ""
            if min_val is not None and max_val is not None:
                min_max = f" between {min_val} and {max_val}"
            elif min_val is not None:
                min_max = f" >= {min_val}"
            elif max_val is not None:
                min_max = f" <= {max_val}"
            raise ValidationError(
                message=f"Please enter a valid number{min_max}",
                cursor_position=len(text)
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
