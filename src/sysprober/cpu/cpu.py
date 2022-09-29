#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

# NOTE: Scrap this for right now - taking up too much time this week. Maybe next.

"""Glob cpu information about underlying host."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from pydantic import BaseModel

from sysprober._base import Parser, readonlydict


class CacheMapping(BaseModel):
    caches: str
    mapping: str


class CPUData(BaseModel):
    bogomips: float
    cpu: int
    core: int
    socket: int
    cluster: str | None
    node: int
    book: str | None
    drawer: str | None
    cache_mapping: CacheMapping
    polarization: str | None
    address: str | None
    configured: str | None
    online: bool
    mhz: float
    maxmhz: float
    minmhz: float


class _CPUParser(Parser):
    @readonlydict
    def parse(self) -> Dict[str, Any]:
        # TODO: Parse the output of `lscpu --extended --all --output-all -J`
        pass

    def _lscpu_parser(self, lscpu_in: str) -> List[CPUData]:
        cpu_store = []
        dash_filter = lambda x: None if x == "-" else x
        online_filter = lambda x: True if x == "yes" else False
        cache_filter = lambda k, v: CacheMapping(caches=k, mapping=v)

        data = json.loads(lscpu_in)
        for cpu in data["cpus"]:
            cpu_store.append(
                CPUData(
                    bogomips=cpu["bogomips"],
                    cpu=cpu["cpu"],
                    core=cpu["core"],
                    socket=cpu["socket"],
                    cluster=dash_filter(cpu["cluster"]),
                )
            )


class CPU:
    def __init__(self) -> None:
        raise NotImplementedError("CPU prober has not been implemented yet.")
