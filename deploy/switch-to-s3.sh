#!/bin/bash

# Switch repository to use S3 storage

set -e

echo "=========================================="
echo "Switching to S3 Storage"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "data/repository.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Backup current repository.py
echo "📦 Backing up current repository.py..."
cp data/repository.py data/repository_local_backup.py

# Copy S3 version
echo "🔄 Switching to S3 repository..."
cp data/repository_s3.py data/repository.py

# Check if .env has S3 configuration
echo "🔍 Checking .env configuration..."
if ! grep -q "USE_S3=true" .env 2>/dev/null; then
    echo "⚠️  Warning: .env file missing or USE_S3 not set to true"
    echo ""
    echo "Please ensure your .env file contains:"
    echo "  USE_S3=true"
    echo "  AWS_ACCESS_KEY_ID=your_key"
    echo "  AWS_SECRET_ACCESS_KEY=your_secret"
    echo "  AWS_REGION=us-east-1"
    echo "  S3_BUCKET_NAME=your_bucket_name"
    echo ""
    read -p "Edit .env now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
    fi
fi

# Optional: Upload existing local data to S3
if [ -f "call_records.xlsx" ]; then
    read -p "📤 Upload existing call_records.xlsx to S3? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Uploading to S3..."
        source venv/bin/activate
        python3 << EOF
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

bucket = os.getenv('S3_BUCKET_NAME')
key = os.getenv('S3_FILE_KEY', 'call_records.xlsx')

with open('call_records.xlsx', 'rb') as f:
    s3.put_object(Bucket=bucket, Key=key, Body=f)

print(f"✅ Uploaded to s3://{bucket}/{key}")
EOF
    fi
fi

echo ""
echo "=========================================="
echo "✅ Successfully switched to S3 storage!"
echo "=========================================="
echo ""
echo "Your local backup is saved at: data/repository_local_backup.py"
echo ""
echo "To revert back to local storage:"
echo "  cp data/repository_local_backup.py data/repository.py"
echo "  Set USE_S3=false in .env"
echo ""
