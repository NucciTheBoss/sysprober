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
    broadcast: ipaddress.IPv4Address | ipaddress.IPv6Address | None
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
    address: ipaddress.IPv4Address | ipaddress.IPv6Address | str
    broadcast: ipaddress.IPv4Address | ipaddress.IPv6Address | str
    link_netnsid: int | None
    addr_info: List[Inet | str]


class _NetworkParser(Parser):
    @readonlydict
    def parse(self, filter: bool = True) -> Dict[str, Any]:
        """An opinionated parser for globbing network information about the host.

        Returns:
            Dict[str, Any]: Network configuration of the host.
        """
        result = {
            "hostname": self._get("hostname"),
        }

        if filter:
            result.update({"ifaces": self._filter(self._ip_parser(self._get("ip -j a")))})
        else:
            result.update({"ifaces": self._ip_parser(self._get("ip -j a"))})

        return result

    def _filter(self, dirty: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out information that does not exist in host network information.

        Args:
            dirty (Dict[str, Any]): Unclean network information.
            Contains settings that may not exist on host.

        Returns:
            List[Dict[str, Any]]: Filtered network information.
        """
        return [self._filterdict(d) for d in dirty]

    def _ip_parser(self, ip_in: str) -> List[Dict[str, Any]]:
        """Parse output from the Linux `ip` command.

        Args:
            ip_in (str): Captured output from the `ip` command.

        Returns:
            List[Dict[str, Any]]: Parsed output of `ip` command.
        """
        ip_out = []
        for i in json.loads(ip_in):
            ip_out.append(
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
        self.raw_info = self.__parser.parse(filter=False)

    def refresh(self) -> None:
        """Refresh host network information."""
        self.info = self.__parser.parse()
        self.raw_info = self.__parser.parse(filter=False)
