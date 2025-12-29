#!/bin/sh
set -e

# Generate runtime config.js from environment variables
# This allows configuration at container startup without rebuilding

CONFIG_FILE="/usr/share/nginx/html/config.js"

echo "Generating runtime config..."

cat > "$CONFIG_FILE" << CONFIGEOF
// Runtime configuration - Generated at container startup
// DO NOT EDIT - This file is regenerated on each container start
window.__APP_CONFIG__ = {
  API_BASE_URL: "${API_BASE_URL:-http://localhost:8000}",
};
CONFIGEOF

echo "Config generated with API_BASE_URL: ${API_BASE_URL:-http://localhost:8000}"

# Execute the main command (nginx)
exec "$@"
