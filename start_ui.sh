#!/bin/bash

echo "======================================================================"
echo "STEM Diagram Generator - Web UI Startup"
echo "======================================================================"
echo ""

# Check if Flask is installed
echo "Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Flask is not installed"
    echo ""
    echo "Please install Flask dependencies:"
    echo "  pip3 install flask flask-cors"
    echo ""
    echo "If you're behind a proxy, try:"
    echo "  pip3 install --proxy=http://your-proxy:port flask flask-cors"
    echo ""
    echo "Or without proxy:"
    echo "  pip3 install --no-proxy=* flask flask-cors"
    exit 1
fi

python3 -c "import flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Flask-CORS is not installed"
    echo ""
    echo "Please install: pip3 install flask-cors"
    exit 1
fi

echo "✅ Python dependencies OK"
echo ""

# Check if Node.js dependencies are installed
if [ ! -d "diagram-ui/node_modules" ]; then
    echo "⚠️  Node.js dependencies not installed"
    echo ""
    echo "Please run:"
    echo "  cd diagram-ui"
    echo "  npm install"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Node.js dependencies OK"
echo ""

# Start Flask API in background
echo "Starting Flask API server on port 5000..."
python3 api_server.py &
API_PID=$!

# Wait for API to be ready
sleep 3

# Check if API is running
if ! ps -p $API_PID > /dev/null; then
    echo "❌ Flask API failed to start"
    exit 1
fi

echo "✅ Flask API started (PID: $API_PID)"
echo ""

# Start Next.js development server
echo "Starting Next.js development server on port 3000..."
cd diagram-ui
npm run dev &
UI_PID=$!

echo ""
echo "======================================================================"
echo "STEM Diagram Generator is running!"
echo "======================================================================"
echo ""
echo "Backend API:  http://localhost:5000"
echo "Frontend UI:  http://localhost:3000"
echo ""
echo "API PID:      $API_PID"
echo "UI PID:       $UI_PID"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "======================================================================"

# Trap Ctrl+C to kill both processes
trap "echo ''; echo 'Stopping servers...'; kill $API_PID $UI_PID; exit 0" INT

# Wait for both processes
wait
