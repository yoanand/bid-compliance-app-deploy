# Streamlit Cloud Deployment Guide

## Deploying with main_app_with_cred.py as Main File

This guide will help you create a new Streamlit Cloud deployment using `main_app_with_cred.py` as the main application file.

## Step 1: Prepare Your Repository

Your repository is already prepared with:
- ✅ `main_app_with_cred.py` - Main application file
- ✅ `requirements.txt` - All dependencies including reportlab
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.streamlit/secrets.toml.template` - AWS credentials template
- ✅ `.gitignore` - Security and clean deployment

## Step 2: Create New Streamlit Cloud App

1. **Go to Streamlit Cloud**: [share.streamlit.io](https://share.streamlit.io)

2. **Click "New app"**

3. **Configure your new app**:
   - **Repository**: Select your GitHub repository (`bid-compliance-app-deploy`)
   - **Branch**: `main`
   - **Main file path**: `main_app_with_cred.py` ⚠️ **IMPORTANT: Use this instead of app.py**
   - **App URL**: Choose a new URL (e.g., `bid-compliance-checker-v2`)

4. **Add AWS Secrets** (in the "Secrets" section):
   ```toml
   [aws]
   access_key_id = "YOUR_ACTUAL_AWS_ACCESS_KEY_ID"
   secret_access_key = "YOUR_ACTUAL_AWS_SECRET_ACCESS_KEY"
   region = "us-east-1"
   ```

5. **Click "Deploy!"**

## Step 3: Verify Deployment

After deployment (2-5 minutes), verify:

### ✅ Interface Check
- Title: "🏢 Bid Compliance Checking System"
- Subtitle: "AI-Powered Document Analysis & Compliance Verification"
- Sidebar: AWS Configuration section
- Demo Mode: Toggle checkbox available

### ✅ Functionality Check
- **Demo Mode**: Upload any PDF → Get sample results → Download PDF report
- **AWS Mode**: Enter credentials → Upload PDF → Get AI analysis → Download PDF report

## Step 4: Test Both Modes

### Demo Mode (No AWS Credentials)
1. Enable "Demo Mode" in sidebar
2. Upload any PDF file
3. Click "Analyze Document"
4. Verify PDF download works

### AWS Mode (Full AI Analysis)
1. Enter AWS credentials in sidebar
2. Click "Validate Credentials"
3. Upload a bid document
4. Run full AI analysis
5. Download comprehensive PDF report

## Troubleshooting

### If Interface Looks Different
- Clear browser cache
- Try incognito mode
- Check deployment logs in Streamlit Cloud dashboard

### If PDF Generation Fails
- Verify `reportlab` is in requirements.txt
- Check deployment logs for import errors
- Test demo mode first

### If AWS Mode Fails
- Verify credentials are correct
- Check AWS permissions
- Test demo mode to verify basic functionality

## File Structure for This Deployment

```
├── main_app_with_cred.py          # ← Main file for this deployment
├── requirements.txt               # Dependencies
├── .streamlit/
│   ├── config.toml               # Streamlit configuration
│   └── secrets.toml.template     # AWS credentials template
├── .gitignore                    # Security
├── Audit_Trail_Agent/            # AI agents
├── Bid_Scoring_Agent/
├── Compliance_Check_Agent/
├── Documen_Parsing_Agent/
├── common_agents/
└── sample_files/                 # Test documents
```

## Key Differences from Previous Deployment

- **Main File**: `main_app_with_cred.py` instead of `app.py`
- **Same Functionality**: All PDF generation and AI features included
- **Same Interface**: Identical user experience
- **Better Organization**: Clear separation between local and deployment files

## Support

If you encounter issues:
1. Check the deployment logs in Streamlit Cloud
2. Verify all files are committed to GitHub
3. Test locally first: `streamlit run main_app_with_cred.py`
4. Ensure AWS credentials have proper permissions
