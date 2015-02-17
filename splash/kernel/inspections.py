# -*- coding: utf-8 -*-
"""
Inspections for Lua code.
"""
from __future__ import absolute_import
import os
import glob
import json
from splash.kernel.lua_parser import (
    LuaParser,
    SplashMethod,
    SplashMethodOpenBrace,
    SplashAttribute
)


class Inspector(object):
    """ Inspector for Lua code """
    def __init__(self, lua):
        self.lua = lua
        self.docs = _SplashDocs()
        self.parser = LuaParser(lua)

    def parse(self, code, cursor_pos):
        return self.parser.parse(code, cursor_pos)

    def doc_repr(self, doc):
        if not doc.get("signature"):
            return doc["content"]

        parts = [doc["signature"]]
        if doc.get('short'):
            parts += [doc["short"]]

        if doc.get('params'):
            parts += ["Parameters:\n\n" + doc["params"]]

        if doc.get('returns'):
            parts += ["Returns: " + doc["returns"]]

        if doc.get('details'):
            parts += [doc["details"]]

        return "\n\n".join(parts)

    def help(self, code, cursor_pos, detail_level):
        # from .completer import _pp

        NO_RESULT = {
            'status': 'ok',
            'data': {},
            'metadata': {},
            'found': False,
        }

        m = self.parse(code, cursor_pos)
        if m is None:
            return NO_RESULT

        doc = None

        if isinstance(m, (SplashMethod, SplashMethodOpenBrace)):
            name = "splash:" + m.prefix
            doc = self.docs.get(name)

        elif isinstance(m, SplashAttribute):
            name = "splash." + m.prefix
            doc = self.docs.get(name)

        if doc is None:
            return NO_RESULT

        return {
            'status': 'ok',
            'data': {"text/plain": self.doc_repr(doc)},
            'metadata': {},
            'found': True,
        }


class _SplashDocs(object):
    def __init__(self, folder=None):
        if folder is None:
            folder = os.path.join(os.path.dirname(__file__), "inspections")

        self.info = {}
        files = sorted(glob.glob(folder + "/*.json"))
        for name in files:
            full_name = os.path.join(folder, name)
            with open(full_name, "rb") as f:
                info = json.load(f, encoding='utf8')
            self.info.update(info)

    def __getitem__(self, item):
        return self.info[item]

    def get(self, key, default=None):
        return self.info.get(key, default)
