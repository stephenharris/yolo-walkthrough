#!/bin/bash
set -e

echo "Uploading final weights to s3://${S3_BUCKET_NAME}/weights"

aws s3 sync . s3://${S3_BUCKET_NAME}/weights