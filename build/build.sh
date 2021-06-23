#!/usr/bin/env bash
set -euxo pipefail

: ${GIT_SHA?"GIT_SHA env variable is required"}
: ${AWS_ACCOUNT_ID?"ACCOUNT_ID env variable is required"}
: ${ECR_REGISTRY?"ECR_REGISTRY env variable is required"}
project="ring-downloader"

echo "Build and tag..."

image_uri="${ECR_REGISTRY}/${project}:${GIT_SHA}"
docker build -t "${image_uri}" -f ../dockerfile ../

echo "Pushing to ECR..."
docker push $image_uri