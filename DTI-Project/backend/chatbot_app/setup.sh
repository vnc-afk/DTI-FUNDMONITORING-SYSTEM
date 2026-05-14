#!/bin/bash
# DTI Chatbot Setup Script
# Run this after cloning/pulling the repository

echo "========================================="
echo "DTI Chatbot Backend - Setup Script"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo -e "${YELLOW}Step 1: Checking Python version...${NC}"
python --version
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python found${NC}"
else
    echo -e "${RED}✗ Python not found. Please install Python 3.9+${NC}"
    exit 1
fi
echo ""

# Step 2: Check Django installation
echo -e "${YELLOW}Step 2: Checking Django installation...${NC}"
python -c "import django; print(f'Django {django.get_version()}')"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Django found${NC}"
else
    echo -e "${RED}✗ Django not found. Run: pip install -r requirements.txt${NC}"
    exit 1
fi
echo ""

# Step 3: Navigate to backend directory
echo -e "${YELLOW}Step 3: Navigating to backend directory...${NC}"
cd "$(dirname "$0")"
cd ../..  # Assuming script is in chatbot_app directory
echo -e "${GREEN}✓ Current directory: $(pwd)${NC}"
echo ""

# Step 4: Run migrations
echo -e "${YELLOW}Step 4: Creating database migrations...${NC}"
python manage.py makemigrations chatbot_app
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations created${NC}"
else
    echo -e "${RED}✗ Migration creation failed${NC}"
    exit 1
fi
echo ""

# Step 5: Apply migrations
echo -e "${YELLOW}Step 5: Applying migrations to database...${NC}"
python manage.py migrate chatbot_app
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations applied${NC}"
else
    echo -e "${RED}✗ Migration application failed${NC}"
    exit 1
fi
echo ""

# Step 6: Run tests
echo -e "${YELLOW}Step 6: Running chatbot tests...${NC}"
python manage.py test chatbot_app --keepdb
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}⚠ Some tests failed. Check output above.${NC}"
fi
echo ""

# Step 7: Summary
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup Complete! 🎉${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Start development server:"
echo "   python manage.py runserver"
echo ""
echo "2. Test the API:"
echo "   curl -X POST http://localhost:8000/api/chatbot/ \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\": \"What are the total funds?\"}'"
echo ""
echo "3. Access Django Admin:"
echo "   Create superuser: python manage.py createsuperuser"
echo "   Then visit: http://localhost:8000/admin/"
echo ""
echo "4. Read documentation:"
echo "   - README.md - Full API documentation"
echo "   - EXAMPLES.md - API usage examples"
echo "   - QUICKSTART.md - Quick setup guide"
echo ""
