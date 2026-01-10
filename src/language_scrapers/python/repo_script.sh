#!/bin/bash
REPO_URL=$1
mkdir -p /repos
cd /repos
git clone "$REPO_URL"