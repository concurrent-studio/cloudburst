# -*- coding: utf-8 -*-

import importlib


class LazyLoader:
    def __init__(self, lib_name):
        self.lib_name = lib_name
        self._mod = None

    def __getattrib__(self, name):
        if self._mod is None:
            self._mod = importlib.import_module(self.lib_name)
        return getattr(self._mod, name)
