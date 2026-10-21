#!/usr/bin/env python3
"""Wrapper: judge demo is built by build-editorial-demo-video.py."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("build-editorial-demo-video.py")), run_name="__main__")
