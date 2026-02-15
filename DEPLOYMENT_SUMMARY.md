# 🚀 Quick Start: AWS Deployment

Your project is now ready for AWS deployment! Follow these steps:

## ✅ What Was Done

1. **Added S3 Storage Support**
   - Created `data/repository_s3.py` - S3-based storage implementation
   - Added `boto3` to requirements.txt
   - Supports both local (Excel) and S3 storage
   - Controlled via `USE_S3=true/false` in .env

2. **Created Deployment Scripts**
   - `deploy/setup-ec2.sh` - Automated EC2 setup script
   - `deploy/switch-to-s3.sh` - Switch between local/S3 storage
   - `deploy/restart-app.sh` - Quick restart utility

3. **Added Service Configurations**
   - `deploy/systemd/streamlit-app.service` - Run as 24/7 service
   - `deploy/nginx/ai-call-app.conf` - Port 80 reverse proxy

4. **Documentation**
   - `AWS_DEPLOYMENT.md` - Complete deployment guide
   - `.env.example` - Environment variables template

---

## 🎯 Next Steps

### For Local Development (Current Setup)

✅ **No changes needed!** Your app still works with local Excel storage.

- `USE_S3=false` in your `.env` file
- Data stored in `call_records.xlsx`

### For AWS Deployment

#### Step 1: Create AWS Resources

Follow the guide in [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md):

1. Create S3 bucket
2. Create IAM user with S3 access
3. Launch EC2 instance
4. Configure security groups

#### Step 2: Deploy to EC2

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Download and run setup script
wget https://raw.githubusercontent.com/thelakshyadubey/AI-Call-Intelligence/main/deploy/setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh

# Edit .env with your AWS credentials
nano .env

# Switch to S3 storage
./deploy/switch-to-s3.sh

# Start the application
sudo systemctl start streamlit-app
```

#### Step 3: Access Your App

- **With port**: `http://YOUR_EC2_IP:8501`
- **Without port** (after nginx): `http://YOUR_EC2_IP`

---

## 📝 Important Notes

### Environment Variables

**Local Development** (current .env):

```env
GROQ_API_KEY=your_key
USE_S3=false
```

**AWS Production** (.env on EC2):

```env
GROQ_API_KEY=your_key
USE_S3=true
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=ai-call-intelligence-data
S3_FILE_KEY=call_records.xlsx
```

### Cost Estimate

- **Free Tier** (first 12 months): $0-5/month
- **After Free Tier**: ~$20/month
- See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for detailed breakdown

### Storage Behavior

- **Local** (`USE_S3=false`): Saves to `call_records.xlsx` in project folder
- **S3** (`USE_S3=true`): Saves to S3 bucket, downloads on read

---

## 🔄 Testing S3 Locally (Optional)

Want to test S3 integration before deploying?

```powershell
# Install boto3
pip install boto3

# Update .env
USE_S3=true
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name
S3_FILE_KEY=call_records.xlsx

# Switch to S3 repository
Copy-Item data\repository_s3.py data\repository.py

# Run app
streamlit run app.py
```

To revert:

```powershell
# Restore backup if you made one, or re-clone from GitHub
git checkout data/repository.py
# Set USE_S3=false in .env
```

---

## 📚 Full Documentation

- **Complete AWS Guide**: [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
- **Deployment Scripts**: `deploy/` folder
- **Environment Template**: `.env.example`

---

## 🆘 Need Help?

1. **Check AWS_DEPLOYMENT.md** - Step-by-step guide with screenshots
2. **Troubleshooting section** - Common issues and fixes
3. **Open GitHub Issue** - For technical support

---

**Your code is pushed to GitHub and ready for deployment! 🎉**

Repository: https://github.com/thelakshyadubey/AI-Call-Intelligence
