#!/bin/bash
# AutoTestDesign — one-command setup script

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "=============================="
echo "  AutoTestDesign Setup"
echo "=============================="
echo ""

# ---------- Check prerequisites ----------

check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        echo "ERROR: $1 is not installed. Please install it and retry."
        exit 1
    fi
}

echo "Checking prerequisites..."
check_cmd python3
check_cmd node
check_cmd npm
echo "  python3: $(python3 --version)"
echo "  node:    $(node --version)"
echo "  npm:     $(npm --version)"
echo ""

# ---------- Backend ----------

echo "--- Setting up backend ---"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
deactivate
echo "Backend setup complete."
echo ""

# ---------- Frontend ----------

echo "--- Setting up frontend ---"
cd "$FRONTEND_DIR"

echo "Installing Node.js dependencies..."
npm install --silent
echo "Frontend setup complete."
echo ""

# ---------- Done ----------

echo "=============================="
echo "  Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend && source venv/bin/activate && python3 run_server.py"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "API docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo "=============================="
