"""
Contains type definitions for use in annotations.
"""

from typing import Union

Json = Union[None, int, float, str, list["Json"], dict[str, "Json"]]
