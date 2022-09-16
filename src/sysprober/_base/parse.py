#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Abstract base class for parsers."""

import subprocess
from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def parse() -> None:
        pass

    def get(self, c: str) -> str:
        """Get the output from a shell command.

        Args:
            c (str): Command to execute in subprocess.

        Returns:
            str: stdout of subprocess.
        """
        out = subprocess.run(c.split(" "), capture_output=True, text=True)
        return out.stdout.strip("\n")
