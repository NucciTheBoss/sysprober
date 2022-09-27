#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Abstract base class for parsers."""

import subprocess
from abc import ABC, abstractmethod
from typing import Dict


class Parser(ABC):
    @abstractmethod
    def parse() -> None:
        pass

    def _filterdict(self, dirty: Dict) -> Dict:
        """Filter `None` values out of a dictionary.

        Args:
            dirty (Dict): Dictionary with None values present.

        Returns:
            Dict: Dictionary with None values removed.
        """
        clean = {}
        for k, v in dirty.items():
            if v is not None:
                if isinstance(v, dict):
                    clean.update({k: self._filterdict(v)})
                elif isinstance(v, list):
                    placeholder = []
                    for i in v:
                        if i is not None:
                            if isinstance(i, dict):
                                placeholder.append(self._filterdict(i))
                            else:
                                placeholder.append(i)

                    clean.update({k: placeholder})
                else:
                    clean.update({k: v})

        return clean

    def _get(self, c: str) -> str:
        """Get the output of a shell command.

        Args:
            c (str): Command to execute in subprocess.

        Returns:
            str: stdout of subprocess.
        """
        out = subprocess.run(c.split(" "), capture_output=True, text=True)
        return out.stdout.strip("\n")
