#!/bin/bash
# Rollback script for VM
# This script rolls back to the previous version of the application

set -e

DEPLOY_DIR="/tmp/deploy"
IMAGE_NAME="hospital-management-app"
COMPOSE_FILE="docker-compose.yml"

echo "🔄 Starting rollback to previous version..."

cd $DEPLOY_DIR

# Check if backup exists
if [ ! -f "previous-image.tar.gz" ]; then
    echo "❌ No backup found, cannot rollback"
    exit 1
fi

echo "📥 Loading previous image..."
gunzip -c previous-image.tar.gz | docker load

echo "🛑 Stopping current containers..."
docker-compose -f $COMPOSE_FILE down || true

echo "🚀 Starting previous version..."
docker-compose -f $COMPOSE_FILE up -d

echo "⏳ Waiting for services to be healthy..."
sleep 15

# Health check
echo "✅ Checking previous version health..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8888/ > /dev/null 2>&1; then
        echo "✅ Previous version is healthy!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "⏳ Waiting for application... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Previous version health check failed!"
    docker-compose -f $COMPOSE_FILE logs
    exit 1
fi

echo "🎉 Rollback completed successfully!"

