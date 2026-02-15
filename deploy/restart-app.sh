#!/bin/bash

# Quick restart script for the application

echo "🔄 Restarting AI Call Intelligence app..."

# Pull latest changes
git pull

# Restart systemd service
sudo systemctl restart streamlit-app

# Show status
sleep 2
sudo systemctl status streamlit-app --no-pager

echo ""
echo "✅ App restarted!"
echo "📊 View logs: sudo journalctl -u streamlit-app -f"
