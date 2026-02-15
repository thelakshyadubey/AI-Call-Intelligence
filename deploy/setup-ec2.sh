#!/bin/bash

# AI Call Intelligence - EC2 Setup Script
# Run this script on your EC2 instance after SSH connection

set -e  # Exit on error

echo "=========================================="
echo "AI Call Intelligence - EC2 Setup"
echo "=========================================="
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Git
echo "📥 Installing Git..."
sudo apt install -y git

# Install Nginx (optional, for port 80 access)
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Clone repository
echo "📂 Cloning repository..."
cd ~
if [ -d "AI-Call-Intelligence" ]; then
    echo "⚠️  Directory already exists. Pulling latest changes..."
    cd AI-Call-Intelligence
    git pull
else
    git clone https://github.com/thelakshyadubey/AI-Call-Intelligence.git
    cd AI-Call-Intelligence
fi

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Groq API Key (REQUIRED)
GROQ_API_KEY=your_groq_api_key_here

# AWS S3 Configuration
USE_S3=true
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=ai-call-intelligence-data
S3_FILE_KEY=call_records.xlsx
EOF
    echo "⚠️  Please edit .env file with your actual credentials:"
    echo "    nano .env"
fi

# Setup systemd service
echo "⚙️  Setting up systemd service..."
sudo cp deploy/systemd/streamlit-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable streamlit-app.service

# Setup Nginx (optional)
read -p "📊 Setup Nginx reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo cp deploy/nginx/ai-call-app.conf /etc/nginx/sites-available/
    sudo ln -sf /etc/nginx/sites-available/ai-call-app.conf /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
    echo "✅ Nginx configured! Access at http://your-ec2-ip"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Switch to S3 storage:"
echo "   ./deploy/switch-to-s3.sh"
echo ""
echo "3. Start the application:"
echo "   sudo systemctl start streamlit-app"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status streamlit-app"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u streamlit-app -f"
echo ""
echo "6. Access your app:"
echo "   http://your-ec2-public-ip:8501"
echo ""
