# 🚀 AWS Deployment Guide

Complete guide to deploy AI Call Intelligence on AWS EC2 with S3 storage.

---

## 📋 Prerequisites

- AWS Account
- Groq API Key
- Basic terminal/SSH knowledge
- Your local project committed to GitHub

---

## Phase 1: AWS Setup

### Step 1: Create S3 Bucket

1. **Login to AWS Console** → Navigate to **S3**
2. Click **"Create bucket"**
3. Configure bucket:
   - **Name**: `ai-call-intelligence-data` (must be globally unique)
   - **Region**: `us-east-1` (or your preferred region)
   - **Block Public Access**: ✅ Keep ALL enabled (security)
   - **Versioning**: ✅ Enable (recommended)
   - **Encryption**: ✅ Enable (recommended)
4. Click **"Create bucket"**

### Step 2: Create IAM User for S3

1. Go to **IAM** → **Users** → **Add users**
2. **Username**: `ai-call-app-s3-user`
3. **Access type**: ✅ Programmatic access
4. Click **Next: Permissions**
5. **Attach policies directly**:
   - Search and select: `AmazonS3FullAccess`
   - OR create custom policy (more secure):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject",
           "s3:PutObject",
           "s3:DeleteObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::ai-call-intelligence-data",
           "arn:aws:s3:::ai-call-intelligence-data/*"
         ]
       }
     ]
   }
   ```
6. Click **Next** → **Create user**
7. **IMPORTANT**: Download and save credentials:
   - Access Key ID
   - Secret Access Key
   - You won't see them again!

### Step 3: Launch EC2 Instance

1. Go to **EC2** → **Launch Instance**

2. **Configuration**:
   - **Name**: `AI-Call-Intelligence-Server`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**:
     - `t2.micro` (Free tier - testing only)
     - `t3.small` (Recommended - $15/month)
   - **Key Pair**: Create new → Download `.pem` file → Save securely

3. **Network Settings**:
   - ✅ Allow SSH (port 22) from My IP
   - ✅ Allow HTTP (port 80) from Anywhere
   - ✅ Allow Custom TCP (port 8501) from Anywhere

4. **Storage**: 20-30 GB gp3

5. Click **Launch Instance**

6. **Wait 2-3 minutes**, then:
   - Note your **Public IP address** (e.g., `54.123.45.67`)
   - Status should show: **Running** ✅

---

## Phase 2: Connect and Setup

### Step 1: Connect to EC2

**Windows PowerShell:**

```powershell
# Navigate to your key file
cd C:\path\to\your\keys

# Set permissions
icacls your-key.pem /inheritance:r
icacls your-key.pem /grant:r "%username%:R"

# Connect
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

**Mac/Linux:**

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 2: Run Setup Script

Once connected to EC2:

```bash
# Download setup script
wget https://raw.githubusercontent.com/thelakshyadubey/AI-Call-Intelligence/main/deploy/setup-ec2.sh

# Make executable
chmod +x setup-ec2.sh

# Run setup
./setup-ec2.sh
```

This script will:

- ✅ Update system packages
- ✅ Install Python 3.11, Git, Nginx
- ✅ Clone your repository
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Setup systemd service
- ✅ Configure Nginx (optional)

### Step 3: Configure Environment Variables

```bash
cd ~/AI-Call-Intelligence
nano .env
```

Add your credentials:

```env
# Groq API Key
GROQ_API_KEY=gsk_your_actual_groq_api_key

# Enable S3 Storage
USE_S3=true

# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA...your_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=ai-call-intelligence-data
S3_FILE_KEY=call_records.xlsx
```

Save: `Ctrl+O`, Exit: `Ctrl+X`

### Step 4: Switch to S3 Storage

```bash
# Make script executable
chmod +x deploy/switch-to-s3.sh

# Run switch script
./deploy/switch-to-s3.sh
```

This will:

- ✅ Backup local repository.py
- ✅ Switch to S3-based repository
- ✅ Optionally upload existing data to S3

---

## Phase 3: Start Application

### Option A: Manual Start (for testing)

```bash
cd ~/AI-Call-Intelligence
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Access: `http://YOUR_EC2_IP:8501`

Press `Ctrl+C` to stop.

### Option B: Run as Service (recommended for production)

```bash
# Start service
sudo systemctl start streamlit-app

# Enable auto-start on boot
sudo systemctl enable streamlit-app

# Check status
sudo systemctl status streamlit-app

# View live logs
sudo journalctl -u streamlit-app -f
```

Access: `http://YOUR_EC2_IP:8501`

---

## Phase 4: Optional - Setup Nginx (Port 80)

If you want to access without `:8501` port:

```bash
# Nginx should already be installed from setup script
# Edit nginx config
sudo nano /etc/nginx/sites-available/ai-call-app.conf

# Update server_name with your domain or IP
# Save and test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

Now access: `http://YOUR_EC2_IP` (no port needed)

---

## 🔧 Common Commands

### Application Management

```bash
# Restart app
sudo systemctl restart streamlit-app

# Stop app
sudo systemctl stop streamlit-app

# View logs
sudo journalctl -u streamlit-app -f

# Pull latest code and restart
cd ~/AI-Call-Intelligence
git pull
sudo systemctl restart streamlit-app
```

### Quick Restart Script

```bash
cd ~/AI-Call-Intelligence
chmod +x deploy/restart-app.sh
./deploy/restart-app.sh
```

---

## 🔒 Security Best Practices

1. **SSH Access**: Change security group to allow SSH only from your IP
2. **Firewall**: Configure UFW:
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 8501
   sudo ufw enable
   ```
3. **S3 Bucket**: Keep all public access blocked
4. **API Keys**: Never commit `.env` to git (already in `.gitignore`)
5. **Regular Updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## 💰 Cost Estimate

| Item           | Configuration   | Monthly Cost   |
| -------------- | --------------- | -------------- |
| EC2 (t3.small) | 2 vCPU, 2GB RAM | ~$15           |
| EBS Storage    | 30GB            | ~$3            |
| S3 Storage     | <1GB            | <$0.50         |
| Data Transfer  | Normal usage    | ~$1-2          |
| **Total**      |                 | **~$20/month** |

**Free Tier** (first 12 months):

- EC2 t2.micro: 750 hours/month free
- S3: 5GB storage + 20,000 requests free
- Estimated: **$0-5/month**

---

## 🐛 Troubleshooting

### App won't start

```bash
# Check service status
sudo systemctl status streamlit-app

# Check logs
sudo journalctl -u streamlit-app -n 50

# Common issues:
# 1. .env file missing or incorrect
# 2. S3 credentials invalid
# 3. Port already in use
```

### S3 Connection Error

```bash
# Test S3 access
python3 << EOF
import boto3, os
from dotenv import load_dotenv
load_dotenv()
s3 = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'))
print(s3.list_buckets())
EOF
```

### Switch Back to Local Storage

```bash
cd ~/AI-Call-Intelligence
cp data/repository_local_backup.py data/repository.py
nano .env  # Set USE_S3=false
sudo systemctl restart streamlit-app
```

---

## 📞 Support

- **GitHub Issues**: https://github.com/thelakshyadubey/AI-Call-Intelligence/issues
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Streamlit Docs**: https://docs.streamlit.io/

---

## ✅ Post-Deployment Checklist

- [ ] EC2 instance running
- [ ] S3 bucket created
- [ ] IAM credentials configured
- [ ] `.env` file populated
- [ ] S3 storage enabled
- [ ] Application accessible via browser
- [ ] Test upload and transcription
- [ ] Test trend analysis
- [ ] Verify data persists in S3
- [ ] Setup monitoring/alerts (optional)

---

**🎉 Congratulations! Your app is now live on AWS!**
