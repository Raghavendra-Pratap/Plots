#!/bin/bash

echo "🚀 Starting UDS - React + Rust Application"
echo "=========================================="

# Function to cleanup background processes
cleanup() {
    echo -e "\n🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "🔧 Starting Rust backend..."
cd backend
cargo run &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🌐 Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Both services are starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend: http://127.0.0.1:3001"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait
