#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Starting deployment process..."

# Note: Make sure you've manually pulled the latest changes before running this script
# Run: git pull origin main (or your branch name)
echo "⚠️  Make sure you have the latest code from GitHub before deploying!"
echo ""

# Stop and remove existing containers
echo "🛑 Stopping existing containers..."
sudo docker stop mae-eliot-frontend mae-eliot-backend mae-eliot-mongodb 2>/dev/null || true
sudo docker rm mae-eliot-frontend mae-eliot-backend mae-eliot-mongodb 2>/dev/null || true

# Remove existing network
echo "🌐 Removing existing network..."
sudo docker network rm mae-eliot-network 2>/dev/null || true

# Create network
echo "🌐 Creating Docker network..."
sudo docker network create mae-eliot-network

# Start MongoDB container
echo "🗄️  Starting MongoDB container..."
sudo docker run -d \
  --name mae-eliot-mongodb \
  --network mae-eliot-network \
  -v /volume1/docker/mae-eliot/mongodb_data:/data/db \
  -p 27017:27017 \
  --restart unless-stopped \
  mongo:4.4

echo "⏳ Waiting for MongoDB to be ready..."
sleep 10

# Build and start backend
echo "🔧 Building backend container..."
sudo docker build -t mae-eliot-backend:latest ./backend

echo "🚀 Starting backend container..."
sudo docker run -d \
  --name mae-eliot-backend \
  --network mae-eliot-network \
  -p 8001:8001 \
  -e MONGO_URL="mongodb://mae-eliot-mongodb:27017/mae_eliot" \
  -e DB_NAME="mae_eliot" \
  -e SECRET_KEY="your-super-secret-jwt-key-change-this-in-production" \
  --restart unless-stopped \
  mae-eliot-backend:latest

echo "⏳ Waiting for backend to start..."
sleep 5

# Build and start frontend
echo "🎨 Building frontend container..."
sudo docker build -t mae-eliot-frontend:latest ./frontend

echo "🚀 Starting frontend container..."
sudo docker run -d \
  --name mae-eliot-frontend \
  --network mae-eliot-network \
  -p 3000:80 \
  --restart unless-stopped \
  mae-eliot-frontend:latest

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo ""
echo "📊 Container Status:"
sudo docker ps --filter "name=mae-eliot" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "📝 Checking logs..."
echo ""
echo "=== Backend Logs ==="
sudo docker logs mae-eliot-backend --tail 20
echo ""
echo "=== Frontend Logs ==="
sudo docker logs mae-eliot-frontend --tail 10
echo ""
echo -e "${YELLOW}🌐 Your application should be accessible at: https://mae.synology.me${NC}"
echo ""
echo "💡 To view live logs, use:"
echo "   Backend:  sudo docker logs -f mae-eliot-backend"
echo "   Frontend: sudo docker logs -f mae-eliot-frontend"
echo "   MongoDB:  sudo docker logs -f mae-eliot-mongodb"
