#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Glob memory information about underlying host."""

from __future__ import annotations

import math
from types import MappingProxyType
from typing import Dict, List

from sysprober._base import Parser, ParserException, readonlydict


class MemoryUnitMismatchError(ParserException):
    """Raised when unit of measure for memory entries is not in kilobytes."""

    def __init__(self, entry: str, desc: str = "Unit of measure for entry is not in kB.") -> None:
        self.entry = entry
        self.desc = desc
        super().__init__(self.desc)

    def __repr__(self) -> str:
        """String representation of MemoryUnitMismatchError."""
        return f"{self.entry}: {self.desc}"


class _MemoryParser(Parser):
    def __init__(self) -> None:
        self.__store = {}

    @readonlydict
    def parse(self) -> Dict[str, int]:
        self._meminfo_parse(open("/proc/meminfo", "rt").readlines())
        return self.__store

    def _meminfo_parse(self, meminfo_in: List[str]) -> None:
        check_unit = (
            lambda entry, unit: MemoryUnitMismatchError(entry) if unit.lower() != "kb" else None
        )
        for line in meminfo_in:
            holder = line.strip("\n").split(":")
            lexeme = [i.strip(" ").split(" ") for i in holder]
            token = self._flatten(lexeme)
            try:
                check_unit(token[0], token[2])
            except IndexError:
                pass
            self.__store.update({self._filter_attr(token[0]): int(token[1])})

    def _filter_attr(self, a: str) -> str:
        """Convert attribute to valid Python syntax.

        Args:
            a (str): Unfiltered attribute.

        Returns:
            str: Syntactically valid attribute.
        """
        clip_paranthesis = lambda x: x[:-1] if x.endswith(")") else x

        holder = a.replace("(", "_")
        holder = clip_paranthesis(holder)
        return holder.replace(")", "_").lower()

    def _flatten(self, l: List) -> List:
        """Flatten a list.

        Args:
            l (List): A list with nested lists.

        Returns:
            List: A flattened list.
        """
        flat = []
        for i in l:
            if isinstance(i, list):
                flat.extend(self._flatten(i))
            else:
                flat.append(i)

        return flat


class Memory:
    def __init__(self) -> None:
        self.__parser = _MemoryParser()
        self.__data = self.__parser.parse()
        self.unit = "KiB"
        self.__mount()

    @property
    def _raw(self) -> MappingProxyType:
        """Direct access to the parsed output from `/proc/meminfo`.

        Returns:
            MappingProxyType: Raw memory data.
        """
        return self.__data

    def __calc(self, v: int | float, unit: str, floor: bool) -> int | float:
        """Convert bytes to new unit of measure.

        Args:
            v (int | float): Value to convert.
            unit (str): Unit of measure to convert to.
            floor (bool): Floor the converted value to the nearest integer if True;
            preserve original float if False.

        Returns:
            int | float: Converted value.
        """
        convert = lambda c, p: c * 1024 / math.pow(1024, p)
        if unit == "mb":
            return math.floor(convert(v, 2)) if floor else convert(v, 2)

    def __mount(self) -> None:
        """Mount properties onto class after parsing `/proc/meminfo`."""
        for k, v in self.__data.items():
            setattr(self, k, v)

    def convert(self, unit: str = "MB", floor: bool = True) -> None:
        """_summary_

        Args:
            unit (str, optional): Unit of measure to convert to. Defaults to "MB".
            floor (bool, optional): Floor the converted value to the nearest integer if True;
            preserve original float if False. Defaults to True.
        """
        blacklist = {"hugepages_total", "hugepages_free", "hugepages_rsvd", "hugepages_surp"}
        holder = dict(self.__data)
        for k, v in holder.items():
            if k not in blacklist:
                holder.update({k: self.__calc(v, unit.lower(), floor)})
        self.__data = MappingProxyType(holder)
        self.unit = unit
        self.__mount()

    def refresh(self) -> None:
        """Refresh current memory information by reparsing `/proc/meminfo`.

        Warnings:
            Resets current unit to KiB (kibibyte). Conversions will need to be reapplied.
        """
        self.__data = self.__parser.parse()
        self.__mount()
