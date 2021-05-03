#!/usr/bin/env bash
set -euxo pipefail

: ${GIT_SHA?"GIT_SHA env variable is required"}
: ${VERSION?"VERSION env variable is required"}
project="ring-downloader"

echo "Building..."

mkdir ./packages || true

image_name="${project}:${GIT_SHA}"
docker build -f ../dockerfile -t $image_name --build-arg VERSION=${VERSION} ../
container_id=$(docker create $image_name)
docker cp $container_id:./app/init.py ./packages/init.py
docker rm -v $container_id

echo "Publishing package..."
aws cloudformation package \
    --template-file="./cloudformation.yaml" \
    --output-template-file="./package.yaml" \
    --s3-prefix="${project}/${GIT_SHA}" \
    --s3-bucket="my-aws-code"

aws s3 cp "./package.yaml" "s3://my-aws-code/${project}/${GIT_SHA}/"