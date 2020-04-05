#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cloudburst core testing"""

import cloudburst as cb

def test_query():
    assert cb.query(".", "jpg") == []