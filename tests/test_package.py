from __future__ import annotations

import importlib.metadata

import predicator as m


def test_version():
    assert importlib.metadata.version("predicator") == m.__version__
