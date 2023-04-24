#!/bin/python3
import sys

v = sys.version_info.minor

if v <= 9:
    print("yes")
