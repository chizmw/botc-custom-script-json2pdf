#!/usr/bin/env bash

set -euo pipefail

docker build -t weasyprint .
docker create --name weasyprint weasyprint bash
docker cp weasyprint:/var/task/weasyprint_lambda_layer.zip ./

docker rm -f weasyprint
