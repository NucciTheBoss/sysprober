#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Glob network information about underlying host."""

from __future__ import annotations

import ipaddress
import json
from typing import Any, Dict, List

from pydantic import BaseModel

from sysprober._base import Parser, readonlydict


class Inet(BaseModel):
    family: str
    address: ipaddress.IPv4Address | ipaddress.IPv6Address
    prefixlen: int
    broadcast: str | None
    scope: str
    temporary: bool | None
    dynamic: str | None
    mngtmpaddr: bool | None
    noprefixroute: bool | None
    label: str | None
    valid_life_time: str
    preferred_life_time: str


class Interface(BaseModel):
    flags: List[str]
    mtu: int
    qdisc: str
    master: str | None
    operstate: str
    group: str
    txqlen: str
    link_type: str
    address: str
    broadcast: str
    link_netnsid: int | None
    addr_info: List[Inet | str]


class _NetworkParser(Parser):
    @readonlydict
    def parse(self) -> Dict[str, Any]:
        """An opinionated parser for globbing network information about the host.

        Returns:
            Dict[str, Any]: Network configuration of the host.
        """
        return {
            "hostname": self.get("hostname"),
            "ifaces": self._filter(self._ip_parser(self.get("ip -j a"))),
        }

    def _filter(self, dirty: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out information that does not exist in host network.

        Args:
            dirty (Dict[str, Any]): Unclean network information.
            Contains settings that may not exist on host.

        Returns:
            Dict[str, Any]: Filtered network information.
        """
        return {k: v for k, v in dirty.items() if v is not None}

    def _ip_parser(self, ip_in: str) -> Dict[str, Any]:
        """Parse output from the Linux `ip` command.

        Args:
            ip_in (str): Captured output from the `ip` command.

        Returns:
            Dict[str, Any]: Parsed output of `ip` command.
        """
        ip_out = {}
        for i in json.loads(ip_in):
            ip_out.update(
                {
                    "name": i.get("ifname", None),
                    "info": Interface(
                        flags=i.get("flags", None),
                        mtu=i.get("mtu", None),
                        qdisc=i.get("qdisc", None),
                        master=i.get("master", None),
                        operstate=i.get("operstate", None),
                        group=i.get("group", None),
                        txqlen=i.get("txqlen", None),
                        link_type=i.get("link_type", None),
                        address=i.get("address", None),
                        broadcast=i.get("broadcast", None),
                        link_netnsid=i.get("link_netnsid", None),
                        addr_info=[self._addr_extract(a).dict() for a in i["addr_info"]],
                    ).dict(),
                }
            )
        return ip_out

    def _addr_extract(self, a: Dict[str, Any]) -> Inet:
        """Extract address information about interfaces on the host.

        Args:
            a (Dict[str, Any]): Interface address information.

        Returns:
            Inet: Extracted information address information from ip command.
        """
        return Inet(
            family=a.get("family", None),
            address=a.get("local", None),
            prefixlen=a.get("prefixlen", None),
            broadcast=a.get("broadcast", None),
            scope=a.get("scope", None),
            temporary=a.get("temporary", None),
            dynamic=a.get("dynamic", None),
            mngtmpaddr=a.get("mngtmpaddr", None),
            noprefixroute=a.get("npprefixaddr", None),
            label=a.get("label", None),
            valid_life_time=a.get("valid_life_time", None),
            preferred_life_time=a.get("preferred_life_time", None),
        )


class Network:
    def __init__(self) -> None:
        self.__parser = _NetworkParser()
        self.info = self.__parser.parse()

    def refresh(self) -> None:
        """Refresh host network information."""
        self.info = self.__parser.parse()
