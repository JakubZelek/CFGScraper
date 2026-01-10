#!/bin/bash
REPO_URL=$1

mkdir -p /repos

cd /repos
git clone "$REPO_URL"

REPO_DIR=$(basename "$REPO_URL" .git)
BUILD_DIR="/repos/$REPO_DIR/build"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake -S .. -B . -DCMAKE_CXX_STANDARD=17 -DCMAKE_C_STANDARD=99 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON || true
cmake --build . || true

