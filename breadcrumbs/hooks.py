"""
Module for hooks.
"""

from enum import Enum, auto
from typing import Dict, List, Callable, Any
from functools import wraps

# Global hooks
HOOKS: Dict['HookTypes', List[Callable]] = dict()




