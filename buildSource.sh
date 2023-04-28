#!/bin/bash
python3 updateChangelog.py
dpkg-buildpackage -S -sa
