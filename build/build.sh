#!/usr/bin/env bash
set -euxo pipefail

: ${GIT_SHA?"GIT_SHA env variable is required"}

project="ring-downloader"

echo "Create package..."

mkdir ./packages || true

cp -a ../src/. ./packages
pip install -r requirements.txt -t ./packages

aws cloudformation package \
    --template-file="./cloudformation.yaml" \
    --output-template-file="./package.yaml" \
    --s3-prefix="${project}/${GIT_SHA}" \
    --s3-bucket="my-aws-code"

aws s3 cp "./package.yaml" "s3://my-aws-code/${project}/${GIT_SHA}/"