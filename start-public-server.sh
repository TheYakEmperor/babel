#!/bin/bash
# Start Babel Admin Server with Caddy HTTPS proxy
# Run this to make the server publicly accessible at api.babelarchive.org

cd "$(dirname "$0")"

echo "Starting Babel Admin Server..."
echo ""

# Kill any existing processes
pkill -f "python3 admin_server.py" 2>/dev/null
pkill -f "caddy run" 2>/dev/null
sleep 1

# Start admin server in background
BABEL_HOST=0.0.0.0 BABEL_CORS_ORIGIN=https://babelarchive.org python3 admin_server.py &
ADMIN_PID=$!
echo "Admin server started (PID: $ADMIN_PID)"

# Wait a moment for server to start
sleep 2

# Start Caddy (needs sudo for port 443)
echo "Starting Caddy HTTPS proxy..."
echo "(You may be asked for your password for port 443 access)"
sudo caddy run --config Caddyfile &
CADDY_PID=$!

echo ""
echo "=================================================="
echo "  Babel is now publicly accessible!"
echo "=================================================="
echo "  Admin panel: https://babelarchive.org/admin.html"
echo "  API server:  https://api.babelarchive.org"
echo "=================================================="
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for either to exit
trap "kill $ADMIN_PID $CADDY_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
