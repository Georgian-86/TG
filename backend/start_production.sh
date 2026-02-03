#!/bin/bash
#
# Production startup script for TeachGenie Backend
# Optimized for performance with multiple workers
#

echo "🚀 Starting TeachGenie Backend (Production Mode)"
echo "================================================"

# Configuration
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-8}"  # Increased from default 4
TIMEOUT="${TIMEOUT:-120}"  # 120 seconds for long-running requests

echo "Configuration:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS (2x default for better concurrency)"
echo "  Timeout: ${TIMEOUT}s"
echo ""

# Start Uvicorn with optimized settings
exec uvicorn app.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --timeout-keep-alive "$TIMEOUT" \
    --log-level info \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips='*'
