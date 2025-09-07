# Bid Compliance Checking System

A Streamlit-based application for automated bid compliance checking and evaluation with AI-powered analysis.

## Features

- **Document Parsing**: Extract and analyze bid documents using AI agents
- **Compliance Checking**: Automated compliance verification with GPP, ESG, and CO₂ tracking
- **Bid Scoring**: AI-powered bid evaluation with weighted scoring model
- **PDF Report Generation**: Professional PDF reports instead of JSON files
- **Dual Mode Operation**: Demo mode for testing and AWS mode for production
- **Real-time Processing**: Live document analysis with progress indicators

## Live Demo

This application is deployed on Streamlit Cloud and can be accessed at:
[Deployment URL will be added after deployment]

## Usage

### Demo Mode (No AWS Credentials Required)
1. Enable "Demo Mode" in the sidebar
2. Upload any PDF document
3. Click "Analyze Document" to see sample results
4. Download formatted PDF compliance report

### AWS Mode (Full AI Analysis)
1. Enter your AWS credentials in the sidebar
2. Click "Validate Credentials" to verify access
3. Upload bid documents (PDF format)
4. Click "Analyze Document" for AI-powered analysis
5. Download comprehensive PDF analysis report

## Technical Stack

- **Frontend**: Streamlit with custom styling
- **Backend**: Python with AI agents (Strands Agents)
- **Document Processing**: PyMuPDF, pdfplumber, reportlab
- **Cloud Services**: AWS (Bedrock, S3, etc.)
- **Cloud Deployment**: Streamlit Cloud
- **Report Generation**: ReportLab for professional PDF reports

## Deployment on Streamlit Cloud

### Prerequisites
1. GitHub repository with your code
2. Streamlit Cloud account
3. AWS credentials (for full functionality)

### Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Streamlit Cloud deployment configuration"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Set main file path to: `app.py`
   - Add AWS secrets in the "Secrets" section:
     ```toml
     [aws]
     access_key_id = "YOUR_AWS_ACCESS_KEY_ID"
     secret_access_key = "YOUR_AWS_SECRET_ACCESS_KEY"
     region = "us-east-1"
     ```

3. **Configure App Settings**:
   - App URL: Choose your preferred URL
   - Python version: 3.9 or higher
   - Dependencies: `requirements.txt` (automatically detected)

### File Structure for Deployment
```
├── app.py                          # Main application file
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   └── secrets.toml.template      # AWS credentials template
├── .gitignore                     # Git ignore rules
├── Audit_Trail_Agent/             # AI agents
├── Bid_Scoring_Agent/
├── Compliance_Check_Agent/
├── Documen_Parsing_Agent/
├── common_agents/
└── sample_files/                  # Test documents
```

## Sample Files

The `sample_files/` directory contains example documents for testing:
- `Supplier1_quote.pdf` - Sample supplier quote
- `Supplier2_quote.pdf` - Another supplier quote  
- `star-enterprise-audit-form.pdf` - Audit form template

## Security Notes

- AWS credentials are stored securely in Streamlit Cloud secrets
- Demo mode allows testing without exposing credentials
- All sensitive files are excluded from version control via `.gitignore`

## Support

For issues or questions:
1. Check the demo mode first to verify basic functionality
2. Ensure AWS credentials have proper permissions
3. Verify all dependencies are installed correctly
4. Let's connect - www.linkedin.com/in/abhishek-anand-it-is
