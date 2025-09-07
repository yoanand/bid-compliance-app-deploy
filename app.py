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
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Bid Compliance Checking System",
    page_icon="📋",
    layout="wide"
)

def create_agents_with_credentials(aws_access_key, aws_secret_key, aws_region):
    """Create all agents with user-provided AWS credentials"""
    try:
        # Set environment variables for the session
        os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_key
        os.environ['AWS_REGION'] = aws_region
        
        # Import agents after setting credentials
        from Documen_Parsing_Agent import doc_agent
        from Compliance_Check_Agent import compliance_checking_agent
        from Bid_Scoring_Agent import bid_scoring_agent, pdf_code_agent
        from common_agents import summary_agent
        
        return {
            'doc_agent': doc_agent,
            'compliance_agent': compliance_checking_agent,
            'scoring_agent': bid_scoring_agent,
            'pdf_code_agent': pdf_code_agent,
            'summary_agent': summary_agent
        }
    except Exception as e:
        st.error(f"Error creating agents: {str(e)}")
        return None

def validate_aws_credentials(aws_access_key, aws_secret_key, aws_region):
    """Validate AWS credentials"""
    try:
        import boto3
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
        
        # Test credentials
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

def generate_pdf_report(results, filename="compliance_report.pdf"):
    """Generate a PDF report from analysis results"""
    try:
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Title
        story.append(Paragraph("Bid Compliance Analysis Report", title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Supplier Information
        if "Supplier Info" in results:
            story.append(Paragraph("Supplier Information", heading_style))
            supplier_info = results["Supplier Info"]
            for key, value in supplier_info.items():
                story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Compliance Check
        if "Compliance Check" in results:
            story.append(Paragraph("Compliance Status", heading_style))
            compliance = results["Compliance Check"]
            for criterion, status in compliance.items():
                story.append(Paragraph(f"<b>{criterion}:</b> {status}", styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Scoring Results
        if "Scoring" in results:
            story.append(Paragraph("Bid Scoring Results", heading_style))
            scoring = results["Scoring"]
            
            # Create scoring table
            table_data = [["Criterion", "Score (1-5)", "Weight (%)", "Weighted Score"]]
            for criterion, data in scoring.items():
                if criterion != "Final Score":
                    table_data.append([
                        criterion,
                        str(data["Score"]),
                        str(data["Weight"]),
                        str(data["Weighted Score"])
                    ])
            
            # Add final score row
            if "Final Score" in scoring:
                table_data.append(["<b>FINAL SCORE</b>", "", "", f"<b>{scoring['Final Score']}/5.0</b>"])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        # Read the generated PDF
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        # Clean up temporary file
        os.unlink(pdf_path)
        
        return pdf_data
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def generate_ai_analysis_pdf(results, filename="ai_analysis_report.pdf"):
    """Generate a PDF report from AI analysis results"""
    try:
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Title
        story.append(Paragraph("AI-Powered Bid Analysis Report", title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Document Summary
        if "summary" in results:
            story.append(Paragraph("Document Summary", heading_style))
            story.append(Paragraph(results["summary"], styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Compliance Analysis
        if "compliance" in results:
            story.append(Paragraph("Compliance Analysis", heading_style))
            story.append(Paragraph(results["compliance"], styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Bid Scoring
        if "scoring" in results:
            story.append(Paragraph("Bid Scoring Analysis", heading_style))
            story.append(Paragraph(results["scoring"], styles['Normal']))
            story.append(Spacer(1, 15))
        
        # PDF Data Information
        if "pdf_data" in results:
            story.append(Paragraph("Document Information", heading_style))
            for filename, data in results["pdf_data"].items():
                story.append(Paragraph(f"<b>File:</b> {filename}", styles['Normal']))
                story.append(Paragraph(f"<b>Path:</b> {data['path']}", styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Build PDF
        doc.build(story)
        
        # Read the generated PDF
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        # Clean up temporary file
        os.unlink(pdf_path)
        
        return pdf_data
        
    except Exception as e:
        st.error(f"Error generating AI analysis PDF: {str(e)}")
        return None

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
                        # Create agents with user credentials
                        agents = create_agents_with_credentials(
                            credentials['access_key'],
                            credentials['secret_key'],
                            credentials['region']
                        )
                        
                        if agents:
                            # Process with agents
                            with st.spinner(f"📄 Processing pdf ..."):
                                doc_agent_response = agents['doc_agent'].tool.extract_pdf_to_json(pdf_path)
                                summary_prompt = f"Summarize the following procurement bid document: {doc_agent_response}"
                                summary_response = agents['summary_agent'](summary_prompt)
                            
                            # Store PDF data
                            pdf_data = {uploaded_file.name: {
                                "path": pdf_path,
                                "extracted_data": doc_agent_response,
                                "summary": summary_response.content
                            }}
                            
                            # Compliance checking
                            with st.spinner("🔍 Running compliance check..."):
                                compliance_prompt = f"Check compliance for this bid: {doc_agent_response}"
                                compliance_response = agents['compliance_agent'](compliance_prompt)
                            
                            # Bid scoring
                            with st.spinner("📊 Calculating bid scores..."):
                                scoring_prompt = f"Score this bid: {doc_agent_response}"
                                scoring_response = agents['scoring_agent'](scoring_prompt)
                            
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
                            
                            # Download results
                            st.subheader("💾 Download Results")
                            results = {
                                "summary": summary_response.content,
                                "compliance": compliance_response.content,
                                "scoring": scoring_response.content,
                                "pdf_data": pdf_data
                            }
                            
                            # Generate PDF report
                            pdf_data = generate_ai_analysis_pdf(results)
                            if pdf_data:
                                st.download_button(
                                    label="📥 Download Analysis Report (PDF)",
                                    data=pdf_data,
                                    file_name=f"analysis_report_{uploaded_file.name.replace('.pdf', '')}.pdf",
                                    mime="application/pdf"
                                )
                            else:
                                st.error("Failed to generate PDF report")
                            
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
    pdf_data = generate_pdf_report(results)
    if pdf_data:
        st.download_button(
            label="📥 Download Compliance Report (PDF)",
            data=pdf_data,
            file_name="compliance_report.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Failed to generate PDF report")

if __name__ == "__main__":
    main()
