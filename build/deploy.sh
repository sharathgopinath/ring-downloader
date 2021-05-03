#!/usr/bin/env bash
set -euxo pipefail

: ${GIT_SHA?"GIT_SHA env variable is required"}
: ${VERSION?"VERSION env variable is required"}
: ${BRANCH?"BRANCH env variable is required"}
project="ring-downloader"
stack_name=${project}-${BRANCH}

echo "Deploying ${project}"
aws s3 cp "s3://my-aws-code/${project}/${GIT_SHA}/package.yaml" package.yaml
aws cloudformation deploy \
    --template-file package.yaml \
    --capabilities="CAPABILITY_NAMED_IAM" \
    --stack-name ${stack_name} \
    --no-fail-on-empty-changeset \
    --parameter-overrides \
        BranchName="${BRANCH}" \
    --tags PROJECT=${project} STACK=${stack_name} \
    || ( aws cloudformation describe-stack-events --stack-name $stack_name; echo "Stack failed to deploy"; exit 1 )