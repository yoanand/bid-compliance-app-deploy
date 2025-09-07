import streamlit as st
import os
import tempfile
import subprocess
import base64
import re
import json
import fitz
from streamlit_autorefresh import st_autorefresh
import random
import boto3
from strands.models import BedrockModel
from strands import Agent
from strands_tools import retrieve

# Set page config
st.set_page_config(
    page_title="Bid Compliance Checking System",
    page_icon="📋",
    layout="wide"
)

def create_agent_with_credentials(aws_access_key, aws_secret_key, aws_region, agent_type="summary"):
    """Create an agent with user-provided AWS credentials"""
    try:
        # Create a custom boto3 session with user credentials
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
        
        # Create a Bedrock model instance
        bedrock_model = BedrockModel(
            model_id="amazon.nova-pro-v1:0",
            boto_session=session,
        )
        
        if agent_type == "summary":
            return Agent(model=bedrock_model,
                        system_prompt="""
                        You are a smart document summarizer. Read the attached vendor invoice and generate a clear, concise summary in plain text. Include the following key details:
                        
                        Format the summary in a professional and readable paragraph or bullet points. If any information is missing, simply skip it without guessing.
                        """)
        elif agent_type == "compliance":
            return Agent(model=bedrock_model, tools=[retrieve],
                        system_prompt="""
                        Role:
                        You are a Compliance Checking Agent responsible for validating supplier bids against ESG, GPP, CSRD, and internal procurement policies.
                        
                        Tasks:
                        1. Review all supplier bid data and supporting documents.
                        2. Check for adherence to sustainability policies and sector-specific standards.
                        3. Compare supplier claims and credentials with industry-specific and regulatory requirements.
                        4. Identify any policy breach, gaps, inconsistencies, or non-compliance issues.
                        
                        Output Format:
                        Return a structured JSON including:
                        - Supplier Name
                        - Compliance Table (criterion, status, evidence, reasoning)
                        - Summary of compliance status
                        - Recommendations
                        """)
        elif agent_type == "scoring":
            return Agent(model=bedrock_model, tools=[retrieve],
                        system_prompt="""
                        Role:
                        You are a Bid Scoring Agent responsible for evaluating supplier bids using a structured, transparent, and auditable weighted average scoring model.
                        
                        Evaluation Criteria:
                        - CO₂ Emissions: 20%
                        - Circularity: 15%
                        - Cost: 25%
                        - Delivery Reliability: 20%
                        - Vendor Scorecard: 20%
                        
                        Output Format:
                        Return a structured JSON with scoring details and final weighted score.
                        """)
        
    except Exception as e:
        st.error(f"Error creating agent: {str(e)}")
        return None

def validate_aws_credentials(aws_access_key, aws_secret_key, aws_region):
    """Validate AWS credentials by attempting to create a session"""
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
        
        # Test credentials by listing regions (lightweight operation)
        sts_client = session.client('sts')
        sts_client.get_caller_identity()
        return True, "Credentials are valid"
    except Exception as e:
        return False, f"Invalid credentials: {str(e)}"

def extract_and_save_code(text, output_filename="pdf_app.py"):
    """Extract Python code from text and save it"""
    code_pattern = r'```python\n(.*?)\n```'
    matches = re.findall(code_pattern, text, re.DOTALL)
    
    if matches:
        code = matches[0]
        with open(output_filename, 'w') as f:
            f.write(code)
        return True
    return False

def main():
    st.title("🏢 Bid Compliance Checking System")
    st.subheader("AI-Powered Document Analysis & Compliance Verification")
    
    # Sidebar for AWS Credentials
    with st.sidebar:
        st.header("🔐 AWS Configuration")
        st.write("Enter your AWS credentials to enable AI-powered analysis:")
        
        aws_access_key = st.text_input(
            "AWS Access Key ID",
            type="password",
            help="Your AWS Access Key ID"
        )
        
        aws_secret_key = st.text_input(
            "AWS Secret Access Key", 
            type="password",
            help="Your AWS Secret Access Key"
        )
        
        aws_region = st.selectbox(
            "AWS Region",
            ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
            help="Select your AWS region"
        )
        
        # Validate credentials button
        if st.button("🔍 Validate Credentials", type="secondary"):
            if aws_access_key and aws_secret_key and aws_region:
                with st.spinner("Validating credentials..."):
                    is_valid, message = validate_aws_credentials(aws_access_key, aws_secret_key, aws_region)
                    if is_valid:
                        st.success("✅ " + message)
                        st.session_state.credentials_valid = True
                        st.session_state.aws_credentials = {
                            'access_key': aws_access_key,
                            'secret_key': aws_secret_key,
                            'region': aws_region
                        }
                    else:
                        st.error("❌ " + message)
                        st.session_state.credentials_valid = False
            else:
                st.warning("⚠️ Please fill in all credential fields")
        
        # Demo mode toggle
        st.markdown("---")
        demo_mode = st.checkbox("🎭 Demo Mode", value=True, help="Use demo data without AWS credentials")
        
        if demo_mode:
            st.info("🎭 Demo mode enabled - using sample data")
            st.session_state.demo_mode = True
        else:
            st.session_state.demo_mode = False
    
    # Main content area
    st.markdown("---")
    
    # Check if we have valid credentials or demo mode
    if not st.session_state.get('credentials_valid', False) and not st.session_state.get('demo_mode', True):
        st.warning("⚠️ Please configure AWS credentials or enable demo mode to continue")
        st.info("💡 **Demo Mode**: Check the demo mode checkbox to test the app with sample data")
        st.info("🔐 **AWS Mode**: Enter your AWS credentials and click 'Validate Credentials'")
        return
    
    # File upload section
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader(
        "Upload a bid document (PDF format)",
        type=['pdf'],
        help="Upload supplier quotes, audit forms, or compliance documents"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            pdf_path = tmp_file.name
        
        # Process button
        if st.button("🔍 Analyze Document", type="primary"):
            if st.session_state.get('demo_mode', True):
                # Demo mode processing
                with st.spinner("🎭 Processing in demo mode..."):
                    import time
                    time.sleep(2)
                    
                    # Demo results
                    demo_results = {
                        "Supplier Info": {
                            "Name": "Vendus Enterprise",
                            "Address": "Hyderabad, India, 500081",
                            "Commodity/Service Provided": "IT Applications"
                        },
                        "Compliance Check": {
                            "GPP Certification": "✅ Present",
                            "ESG Compliance": "✅ Demonstrated", 
                            "CO₂ Emissions": "✅ 12 kg per 100 units (< 15 kg limit)",
                            "Circularity Score": "✅ 8/10 (≥ 7 required)",
                            "Approved Supplier": "✅ Yes",
                            "Delivery Time": "✅ 8 days (< 10 days limit)"
                        },
                        "Scoring": {
                            "CO₂ Emissions": {"Score": 4, "Weight": 20, "Weighted Score": 0.8},
                            "Circularity": {"Score": 4, "Weight": 15, "Weighted Score": 0.6},
                            "Cost": {"Score": 3, "Weight": 25, "Weighted Score": 0.75},
                            "Delivery Reliability": {"Score": 4, "Weight": 20, "Weighted Score": 0.8},
                            "Vendor Scorecard": {"Score": 4, "Weight": 20, "Weighted Score": 0.8},
                            "Final Score": 3.75
                        }
                    }
                    
                    display_results(demo_results, "Demo Mode Results")
                    
            else:
                # AWS mode processing
                credentials = st.session_state.aws_credentials
                
                with st.spinner("🤖 Processing with AI agents..."):
                    try:
                        # Extract text from PDF
                        doc = fitz.open(pdf_path)
                        pdf_text = ""
                        for page in doc:
                            pdf_text += page.get_text()
                        doc.close()
                        
                        # Create agents
                        summary_agent = create_agent_with_credentials(
                            credentials['access_key'],
                            credentials['secret_key'], 
                            credentials['region'],
                            "summary"
                        )
                        
                        compliance_agent = create_agent_with_credentials(
                            credentials['access_key'],
                            credentials['secret_key'],
                            credentials['region'], 
                            "compliance"
                        )
                        
                        scoring_agent = create_agent_with_credentials(
                            credentials['access_key'],
                            credentials['secret_key'],
                            credentials['region'],
                            "scoring"
                        )
                        
                        if summary_agent and compliance_agent and scoring_agent:
                            # Process with agents
                            summary_prompt = f"Summarize the following procurement bid document: {pdf_text[:2000]}"
                            summary_response = summary_agent(summary_prompt)
                            
                            compliance_prompt = f"Check compliance for this bid document: {pdf_text[:2000]}"
                            compliance_response = compliance_agent(compliance_prompt)
                            
                            scoring_prompt = f"Score this bid document: {pdf_text[:2000]}"
                            scoring_response = scoring_agent(scoring_prompt)
                            
                            # Display results
                            st.success("✅ AI analysis completed!")
                            
                            # Summary
                            st.subheader("📋 Document Summary")
                            st.write(summary_response.content)
                            
                            # Compliance
                            st.subheader("✅ Compliance Analysis")
                            st.write(compliance_response.content)
                            
                            # Scoring
                            st.subheader("📊 Bid Scoring")
                            st.write(scoring_response.content)
                            
                        else:
                            st.error("❌ Failed to create AI agents. Please check your credentials.")
                            
                    except Exception as e:
                        st.error(f"❌ Error during processing: {str(e)}")
                        st.info("💡 Try enabling demo mode for testing")
                
                # Clean up temporary file
                os.unlink(pdf_path)
    
    else:
        st.info("👆 Please upload a PDF document to begin analysis")
        
        # Show features
        st.markdown("---")
        st.header("🚀 Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📄 Document Parsing")
            st.write("• PDF text extraction")
            st.write("• Structured data parsing")
            st.write("• Multi-format support")
        
        with col2:
            st.subheader("✅ Compliance Checking")
            st.write("• GPP certification verification")
            st.write("• ESG compliance validation")
            st.write("• CO₂ emissions tracking")
        
        with col3:
            st.subheader("📊 Bid Scoring")
            st.write("• Weighted scoring model")
            st.write("• Multi-criteria evaluation")
            st.write("• Transparent audit trail")

def display_results(results, title):
    """Display analysis results in a formatted way"""
    st.success(f"✅ {title}")
    
    # Supplier Information
    st.subheader("🏢 Supplier Information")
    supplier_info = results["Supplier Info"]
    for key, value in supplier_info.items():
        st.write(f"**{key}:** {value}")
    
    # Compliance Status
    st.subheader("✅ Compliance Status")
    compliance = results["Compliance Check"]
    for criterion, status in compliance.items():
        st.write(f"**{criterion}:** {status}")
    
    # Scoring Results
    st.subheader("📈 Bid Scoring Results")
    scoring = results["Scoring"]
    
    # Create a scoring table
    scoring_data = []
    for criterion, data in scoring.items():
        if criterion != "Final Score":
            scoring_data.append({
                "Criterion": criterion,
                "Score (1-5)": data["Score"],
                "Weight (%)": data["Weight"],
                "Weighted Score": data["Weighted Score"]
            })
    
    st.dataframe(scoring_data, use_container_width=True)
    
    # Final Score
    st.metric(
        label="🎯 Final Weighted Score",
        value=f"{scoring['Final Score']}/5.0",
        delta="Compliant"
    )
    
    # Download results
    st.subheader("💾 Download Results")
    results_json = json.dumps(results, indent=2)
    st.download_button(
        label="📥 Download Compliance Report (JSON)",
        data=results_json,
        file_name="compliance_report.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()
