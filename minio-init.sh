#!/bin/sh

set -e

echo "Waiting for MinIO to be ready..."
sleep 5

# Configure MinIO client
mc alias set myminio http://minio:${MINIO_INTERNAL_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Create bucket if it doesn't exist
BUCKET_NAME="uploads"
mc mb myminio/${BUCKET_NAME} --ignore-existing

# Check if initialization marker exists
MARKER_FILE="myminio/${BUCKET_NAME}/.initialized"
if mc stat ${MARKER_FILE} >/dev/null 2>&1; then
    echo "MinIO already initialized. Skipping file upload."
    exit 0
fi

echo "Initializing MinIO with files..."

# Upload the three files
mc cp /data/file-1.txt myminio/${BUCKET_NAME}/file-1.txt
mc cp /data/file-2.txt myminio/${BUCKET_NAME}/file-2.txt
mc cp /data/file-3.txt myminio/${BUCKET_NAME}/file-3.txt

# Create marker file to prevent re-initialization
echo "initialized" | mc pipe ${MARKER_FILE}

echo "MinIO initialization completed successfully!"
