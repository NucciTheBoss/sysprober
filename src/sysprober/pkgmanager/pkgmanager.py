#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Glob package manager information about underlying host."""

from __future__ import annotations

from shutil import which
from types import MappingProxyType
from typing import Dict, Set

from sysprober._base import Parser, readonlydict


class _Checker:
    def __init__(self, checklist: Set[str]) -> None:
        [setattr(self, p, which(p) is not None) for p in checklist]


class _PkgManagerParser(Parser):
    @readonlydict
    def parse(self) -> Dict[str, _Checker]:
        linux = {"apt", "dpkg", "snap"}
        python = {"conda", "pdm", "pip", "pip3", "poetry"}
        return {"linux": _Checker(linux), "python": _Checker(python)}


class PkgManager:
    def __init__(self) -> None:
        self.__parser = _PkgManagerParser()
        self.__data = self.__parser.parse()
        self.__mount()

    @property
    def _raw(self) -> MappingProxyType:
        return self.__data

    def __mount(self) -> None:
        [setattr(self, k, v) for k, v in self.__data.items()]

    def refresh(self) -> None:
        self.__data = self.__parser.parse()
        self.__mount()
