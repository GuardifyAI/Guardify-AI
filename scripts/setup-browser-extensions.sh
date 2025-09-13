#!/bin/bash

# Setup script for browser extensions required by video recording
# This script handles the installation of browser extensions needed for P2P video streaming

set -e

echo "🔧 Setting up browser extensions for video recording..."

# Check if Playwright browsers are installed
if [ ! -d "/home/guardify/.cache/ms-playwright" ]; then
    echo "📦 Installing Playwright browsers..."
    playwright install chromium
    echo "✅ Playwright browsers installed"
else
    echo "✅ Playwright browsers already installed"
fi

# Create extension directory
EXTENSION_DIR="/home/guardify/.cache/ms-playwright/extensions"
mkdir -p "$EXTENSION_DIR"

echo "📁 Extension directory: $EXTENSION_DIR"

# Note: The @WebClient_VPPlugin_v5_P2P.exe extension is typically:
# 1. Downloaded automatically when accessing the camera web interface
# 2. Or provided by the camera manufacturer
# 3. Or available from the Provision ISR system

if [ -n "$PROVISION_ISR_BASE_URL" ]; then
    echo "🌐 Camera system URL: $PROVISION_ISR_BASE_URL"
    echo "💡 The browser will attempt to download required extensions automatically"
    echo "   when accessing the camera interface for the first time"
fi

echo "⚠️  If video recording fails due to missing extensions:"
echo "   1. Check your camera system's web interface"
echo "   2. Download the @WebClient_VPPlugin_v5_P2P.exe from your camera provider"
echo "   3. Ensure your camera system supports headless browser access"

echo "✅ Browser extension setup complete"