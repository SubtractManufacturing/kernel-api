#!/bin/bash

# Docker OpenCascade Test Script
# This script builds the Docker image and runs comprehensive tests

set -e

echo "======================================"
echo "Docker OpenCascade Build & Test"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        exit 1
    fi
}

# Step 1: Build Docker image
echo -e "\n${YELLOW}Step 1: Building Docker image...${NC}"
docker build -t kernel-api:test . --no-cache
print_status $? "Docker image built successfully"

# Step 2: Run OCP import test
echo -e "\n${YELLOW}Step 2: Testing OCP import in container...${NC}"
docker run --rm kernel-api:test python -c "import OCP; print('OCP version:', OCP.__version__ if hasattr(OCP, '__version__') else 'Unknown'); print('OCP imported successfully')"
print_status $? "OCP import test passed"

# Step 3: Run comprehensive tests
echo -e "\n${YELLOW}Step 3: Running comprehensive OpenCascade tests...${NC}"
docker run --rm -v $(pwd)/tests:/app/tests kernel-api:test python /app/tests/docker_opencascade_test.py
print_status $? "Comprehensive tests passed"

# Step 4: Start services with docker-compose
echo -e "\n${YELLOW}Step 4: Starting services with docker-compose...${NC}"
docker-compose up -d
print_status $? "Services started"

# Wait for API to be ready
echo -e "\n${YELLOW}Waiting for API to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_status 0 "API is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_status 1 "API failed to start in 30 seconds"
    fi
    sleep 1
    echo -n "."
done

# Step 5: Test API endpoints
echo -e "\n${YELLOW}Step 5: Testing API endpoints...${NC}"

# Test health endpoint
curl -s http://localhost:8000/api/v1/health | grep -q "healthy"
print_status $? "Health endpoint working"

# Test formats endpoint
curl -s http://localhost:8000/api/v1/formats | grep -q "step"
print_status $? "Formats endpoint lists STEP support"

# Step 6: Test STEP file conversion via API
echo -e "\n${YELLOW}Step 6: Testing STEP conversion via API...${NC}"

# Create a test STEP file using the container
docker exec kernel-api python -c "
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.STEPControl import STEPControl_Writer, STEPControl_StepModelType
box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
writer = STEPControl_Writer()
writer.Transfer(box, STEPControl_StepModelType.STEPControl_AsIs)
writer.Write('/app/test_box.step')
print('Test STEP file created')
"
print_status $? "Test STEP file created"

# Convert STEP to STL via API
echo -e "\n${YELLOW}Converting STEP to STL via API...${NC}"
response=$(curl -s -X POST "http://localhost:8000/api/v1/convert" \
  -F "file=@test_box.step;type=application/step" \
  -F "output_format=stl" \
  -F "quality=medium" \
  -o test_output.stl \
  -w "%{http_code}")

if [ "$response" = "200" ]; then
    print_status 0 "STEP to STL conversion successful"
    if [ -f test_output.stl ]; then
        file_size=$(stat -f%z test_output.stl 2>/dev/null || stat -c%s test_output.stl 2>/dev/null || echo "0")
        echo "  Output file size: $file_size bytes"
        rm -f test_output.stl
    fi
else
    print_status 1 "STEP to STL conversion failed (HTTP $response)"
fi

# Clean up test file
docker exec kernel-api rm -f /app/test_box.step

# Step 7: Check container logs for errors
echo -e "\n${YELLOW}Step 7: Checking container logs...${NC}"
errors=$(docker-compose logs api 2>&1 | grep -i error | wc -l)
if [ $errors -eq 0 ]; then
    print_status 0 "No errors in container logs"
else
    echo -e "${YELLOW}Warning: Found $errors error messages in logs${NC}"
fi

# Summary
echo -e "\n======================================"
echo -e "${GREEN}All tests completed successfully!${NC}"
echo "======================================"
echo ""
echo "OpenCascade is fully operational in Docker."
echo "The API is running at http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "To stop the services, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f"