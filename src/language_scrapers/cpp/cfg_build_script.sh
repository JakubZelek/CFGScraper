#!/bin/bash
FILEPATH=$1

BASE_DIR="$REPO_FOLDER"
REPO_DIR=$(echo "$FILEPATH" | sed "s|^\($BASE_DIR/[^/]*\)/.*|\1|")

COMPILE_COMMANDS="$REPO_DIR/build/compile_commands.json"
python3 /app/src/language_scrapers/cpp/file_to_cfg.py --filepath "$FILEPATH" --compile-commands "$COMPILE_COMMANDS"
