#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from jsonpath_ng import parse
from ph4runner import AsyncRunner

logger = logging.getLogger(__name__)


def try_fnc(fnc):
    try:
        return fnc()
    except:
        pass


def jsonpath(path, obj, allow_none=False):
    r = [m.value for m in parse(path).find(obj)]
    return r[0] if not allow_none else (r[0] if r else None)


def listize(obj):
    return obj if (obj is None or isinstance(obj, list)) else [obj]


def defval(val, default=None):
    """Returns val if is not None, default instead"""
    return val if val is not None else default


def defvalkey(js, key, default=None, take_none=True):
    """Returns js[key] if set, otherwise default. Note js[key] can be None."""
    if key not in js:
        return default
    if js[key] is None and not take_none:
        return default
    return js[key]


def get_runner(cli, args=None, cwd=None, shell=False, env=None):
    async_runner = AsyncRunner(cli, args=args, cwd=cwd, shell=shell, env=env)
    async_runner.log_out_after = False
    async_runner.log_out_during = False
    async_runner.preexec_setgrp = True
    return async_runner

