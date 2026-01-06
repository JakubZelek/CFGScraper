#!/bin/bash
FILEPATH=$1
python3 /app/src/language_scrapers/python/file_to_cfg.py --filepath "$FILEPATH"
