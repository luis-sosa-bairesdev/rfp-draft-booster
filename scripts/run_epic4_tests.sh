#!/bin/bash
# Run Epic 4 tests and check coverage

set -e

echo "=========================================="
echo "🧪 Running Epic 4 Tests & Coverage"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test directories
MODEL_TESTS="tests/test_models/test_risk.py"
SERVICE_TESTS="tests/test_services/test_risk_detector.py"
UI_TESTS="tests/test_ui/test_risk_analysis_page.py"
INTEGRATION_TESTS="tests/test_integration/test_imports.py"

# Backend tests
echo ""
echo "📦 Running Backend Tests..."
echo "----------------------------------------"
echo "1. Risk Model Tests..."
python3 -m pytest $MODEL_TESTS -v --tb=short || { echo -e "${RED}❌ Model tests failed${NC}"; exit 1; }

echo ""
echo "2. Risk Detector Service Tests..."
python3 -m pytest $SERVICE_TESTS -v --tb=short || { echo -e "${RED}❌ Service tests failed${NC}"; exit 1; }

# Frontend tests
echo ""
echo "🎨 Running Frontend Tests..."
echo "----------------------------------------"
echo "3. Risk Analysis UI Tests..."
python3 -m pytest $UI_TESTS -v --tb=short || { echo -e "${RED}❌ UI tests failed${NC}"; exit 1; }

# Integration tests
echo ""
echo "🔗 Running Integration Tests..."
echo "----------------------------------------"
echo "4. Import Tests..."
python3 -m pytest $INTEGRATION_TESTS -v --tb=short || { echo -e "${RED}❌ Integration tests failed${NC}"; exit 1; }

# Coverage check
echo ""
echo "📊 Checking Code Coverage..."
echo "----------------------------------------"

# Backend coverage
echo "Backend Coverage (models + services):"
python3 -m pytest \
    $MODEL_TESTS $SERVICE_TESTS \
    --cov=src/models/risk \
    --cov=src/services/risk_detector \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/backend \
    --cov-fail-under=80 \
    -q || { echo -e "${RED}❌ Backend coverage below 80%${NC}"; exit 1; }

# Frontend coverage (UI logic)
echo ""
echo "Frontend Coverage (UI pages):"
python3 -m pytest \
    $UI_TESTS \
    --cov=pages \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/frontend \
    --cov-fail-under=80 \
    -q || { echo -e "${YELLOW}⚠️  Frontend coverage check (UI logic only)${NC}"; }

# All Epic 4 tests together
echo ""
echo "🎯 Running All Epic 4 Tests..."
echo "----------------------------------------"
python3 -m pytest \
    $MODEL_TESTS $SERVICE_TESTS $UI_TESTS $INTEGRATION_TESTS \
    -v --tb=short \
    || { echo -e "${RED}❌ Some tests failed${NC}"; exit 1; }

echo ""
echo -e "${GREEN}✅ All Epic 4 tests passed!${NC}"
echo ""
echo "📊 Coverage reports generated:"
echo "   - Backend: htmlcov/backend/index.html"
echo "   - Frontend: htmlcov/frontend/index.html"
echo ""
echo "=========================================="

