#!/bin/bash
set -e

head_sha="$(git describe --always --long --dirty=-dirty)"
project_dir="$(basename "$(git rev-parse --show-toplevel)")"
poetry_version="$(poetry version --short)"

jq -n \
    --arg head_sha "$head_sha" \
    --arg project_dir "$project_dir" \
    --arg poetry_version "$poetry_version" \
    '{"head_sha": $head_sha, "project_dir": $project_dir, "poetry_version": $poetry_version}'
