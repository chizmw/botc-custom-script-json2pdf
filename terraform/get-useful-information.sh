#!/bin/bash
set -e

commit_version="$(git describe --tags --always)"
project_dir="$(basename "$(git rev-parse --show-toplevel)")"
poetry_version="$(poetry version --short)"

jq -n \
    --arg commit_version "$commit_version" \
    --arg project_dir "$project_dir" \
    --arg poetry_version "$poetry_version" \
    '{"commit_version": $commit_version, "project_dir": $project_dir, "poetry_version": $poetry_version}'
