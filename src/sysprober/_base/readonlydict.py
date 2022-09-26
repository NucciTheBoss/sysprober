#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Read-only dictionary for lossless information."""

from functools import wraps
from types import MappingProxyType
from typing import Any


def readonlydict(func: Any) -> MappingProxyType:
    @wraps(func)
    def wrapper(*args, **kwargs):
        return MappingProxyType(func(*args, **kwargs))

    return wrapper
