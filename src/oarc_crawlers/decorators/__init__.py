"""Global decorators for the project"""
from .asyncio_run import asyncio_run
from .handle_error import handle_error
from .singleton import singleton

__all__ = [
    "singleton",
    "asyncio_run",
    "handle_error",
]