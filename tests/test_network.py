#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Tests for the Network class."""

from sysprober.network import Network


class TestNetwork:
    def test_get_info(self) -> None:
        net = Network()
        print(net.info)

    def test_readonly(self) -> None:
        net = Network()
        try:
            net.info["hostname"] = "test"
        except TypeError:
            print("Dictionary is successfully marked as read-only.")
