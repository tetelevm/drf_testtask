"""
Utility file, only libraries and frameworks are allowed to import, not
application files.
"""

import re


__all__ = [
    "camel_to_snake",
]


def camel_to_snake(name: str) -> str:
    """
    Translates NameCamelCase to name_snake_case.
    """
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    return name.lower()
