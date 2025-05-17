#!/bin/bash
# Setup script for Climate Data Analysis project

echo "Setting up Climate Data Analysis project..."

# Create a virtual environment (optional)
echo "Creating a virtual environment (optional)..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing required packages..."
pip install pandas numpy matplotlib seaborn requests
pip install fastapi uvicorn jinja2 plotly
pip install python-multipart aiofiles

# Ensure directories exist
echo "Creating necessary directories..."
mkdir -p data results static templates

echo "Setup complete! To run the FastAPI server, use:"
echo "  python app.py"
echo ""
echo "To run the data analysis script first:"
echo "  python climate_analysis.py"
echo ""
echo "After running the analysis, you can access the interactive dashboard at:"
echo "  http://localhost:8000" 