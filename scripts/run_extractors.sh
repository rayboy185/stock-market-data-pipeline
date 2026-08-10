#!/bin/bash
set -e
python scripts/extract_stocks_v2.py
python scripts/extract_macro.py