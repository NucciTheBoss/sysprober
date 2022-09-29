#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Glob memory information about underlying host."""

from __future__ import annotations

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
            a (str): Unfiltered attribute

        Returns:
            str: Syntactically valid attribute
        """
        clip_paranthesis = lambda x: x[:-1] if x.endswith(")") else x

        holder = a.replace("(", "_")
        holder = clip_paranthesis(holder)
        return holder.replace(")", "_").lower()

    def _flatten(self, l: List) -> List:
        """Flatten a list.

        Args:
            l (List): A list with nested lists

        Returns:
            List: A flattened list
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
        self.unit = "kB"
        self.__mount()

    def __mount(self) -> None:
        """Mount properties onto class after parsing `/proc/meminfo`."""
        for k, v in self.__data.items():
            setattr(self, k, v)

    def refresh(self) -> None:
        self.__data = self.__parser.parse()
        self.__mount()
