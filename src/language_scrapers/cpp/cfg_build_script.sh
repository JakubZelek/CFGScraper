#!/bin/bash
FILEPATH=$1

# Extract repo directory from filepath (e.g., /repos/RepoName/src/file.cpp -> /repos/RepoName)
REPO_DIR=$(echo "$FILEPATH" | sed 's|^\(/repos/[^/]*\)/.*|\1|')
COMPILE_COMMANDS="$REPO_DIR/build/compile_commands.json"

python3 /app/src/language_scrapers/cpp/file_to_cfg.py --filepath "$FILEPATH" --compile-commands "$COMPILE_COMMANDS"

