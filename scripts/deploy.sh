#!/bin/bash
# Deployment script for VM
# This script is used by GitHub Actions for deployment

set -e

DEPLOY_DIR="/tmp/deploy"
IMAGE_NAME="hospital-management-app"
COMPOSE_FILE="docker-compose.yml"

echo "🚀 Starting deployment..."

# Create deployment directory
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

# Backup current image before deployment
if docker images | grep -q "${IMAGE_NAME}:latest"; then
    echo "💾 Backing up current image..."
    docker save ${IMAGE_NAME}:latest | gzip > previous-image.tar.gz
    echo "✅ Backup saved"
fi

# Load Docker image
if [ -f "deploy-image.tar.gz" ]; then
    echo "📥 Loading Docker image..."
    gunzip -c deploy-image.tar.gz | docker load
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down || true

# Remove old images (optional, to save space)
echo "🧹 Cleaning up old images..."
docker image prune -f || true

# Start new containers
echo "🚀 Starting new containers..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 15

# Health check
echo "✅ Checking application health..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8888/ > /dev/null 2>&1; then
        echo "✅ Application is healthy!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "⏳ Waiting for application... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Application health check failed!"
    docker-compose -f $COMPOSE_FILE logs
    exit 1
fi

# Verify endpoints
echo "🔍 Verifying endpoints..."
curl -f http://localhost:8888/analytics > /dev/null 2>&1 && echo "✅ Analytics endpoint OK" || echo "⚠️  Analytics endpoint failed"
curl -f http://localhost:8888/stats > /dev/null 2>&1 && echo "✅ Stats endpoint OK" || echo "⚠️  Stats endpoint failed"

echo "🎉 Deployment completed successfully!"

