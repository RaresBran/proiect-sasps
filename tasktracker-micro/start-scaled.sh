#!/bin/bash
# Start microservices with scaled instances (3 replicas per service)

echo "=========================================="
echo "STARTING SCALED MICROSERVICES ARCHITECTURE"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

echo "Configuration:"
echo "  User Service: 3 replicas"
echo "  Task Service: 3 replicas"
echo "  Stats Service: 3 replicas"
echo "  API Gateway: 1 instance (load balances to services)"
echo ""

echo "Starting services with scaling..."
echo ""

# Stop any existing containers
docker compose down 2>/dev/null

# Start with replicas using the scale flag
docker compose -f docker-compose.scaled.yml up -d --build \
  --scale user-service=3 \
  --scale task-service=3 \
  --scale stats-service=3

echo ""
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "=========================================="
echo "SCALED MICROSERVICES STARTED!"
echo "=========================================="
echo ""
echo "Service Configuration:"
echo "  API Gateway: http://localhost:8000 (1 instance)"
echo "  User Service: 3 replicas (load balanced)"
echo "  Task Service: 3 replicas (load balanced)"
echo "  Stats Service: 3 replicas (load balanced)"
echo ""
echo "Total Service Instances: 10"
echo "  - 1 API Gateway"
echo "  - 3 User Service replicas"
echo "  - 3 Task Service replicas"
echo "  - 3 Stats Service replicas"
echo ""
echo "Check status with:"
echo "  docker compose -f docker-compose.scaled.yml ps"
echo ""
echo "View logs with:"
echo "  docker compose -f docker-compose.scaled.yml logs -f"
echo ""
echo "Stop with:"
echo "  docker compose -f docker-compose.scaled.yml down"
echo ""

