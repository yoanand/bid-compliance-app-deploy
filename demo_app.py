import streamlit as st
import json
import fitz  # PyMuPDF
import tempfile
import os

# Set page config
st.set_page_config(
    page_title="Bid Compliance Checking System - Demo",
    page_icon="📋",
    layout="wide"
)

st.title("🏢 Bid Compliance Checking System")
st.subheader("AI-Powered Document Analysis & Compliance Verification")

# Demo data
demo_audit_data = {
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

def extract_pdf_text(pdf_file):
    """Extract text from PDF file"""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def main():
    st.markdown("---")
    
    # File upload section
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader(
        "Upload a bid document (PDF format)",
        type=['pdf'],
        help="Upload supplier quotes, audit forms, or compliance documents"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Extract text from PDF
        with st.spinner("📄 Processing document..."):
            pdf_text = extract_pdf_text(uploaded_file)
            
        if pdf_text:
            st.subheader("📋 Extracted Content")
            with st.expander("View extracted text"):
                st.text(pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text)
            
            # Process button
            if st.button("🔍 Analyze Document", type="primary"):
                with st.spinner("🤖 Running compliance analysis..."):
                    # Simulate processing time
                    import time
                    time.sleep(2)
                    
                    # Display results
                    st.success("✅ Analysis completed!")
                    
                    # Compliance Results
                    st.header("📊 Compliance Analysis Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🏢 Supplier Information")
                        supplier_info = demo_audit_data["Supplier Info"]
                        for key, value in supplier_info.items():
                            st.write(f"**{key}:** {value}")
                    
                    with col2:
                        st.subheader("✅ Compliance Status")
                        compliance = demo_audit_data["Compliance Check"]
                        for criterion, status in compliance.items():
                            st.write(f"**{criterion}:** {status}")
                    
                    # Scoring Results
                    st.subheader("📈 Bid Scoring Results")
                    scoring = demo_audit_data["Scoring"]
                    
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
                    
                    # Audit Trail
                    st.subheader("📝 Audit Trail")
                    audit_trail = [
                        {"Timestamp": "2024-01-15 10:30:00", "Agent": "Document Parser", "Action": "Extracted text from PDF", "Status": "✅ Success"},
                        {"Timestamp": "2024-01-15 10:30:15", "Agent": "Compliance Checker", "Action": "Verified GPP certification", "Status": "✅ Pass"},
                        {"Timestamp": "2024-01-15 10:30:30", "Agent": "Compliance Checker", "Action": "Checked CO₂ emissions", "Status": "✅ Pass"},
                        {"Timestamp": "2024-01-15 10:30:45", "Agent": "Bid Scorer", "Action": "Calculated weighted scores", "Status": "✅ Success"},
                        {"Timestamp": "2024-01-15 10:31:00", "Agent": "Audit Trail", "Action": "Generated compliance report", "Status": "✅ Complete"}
                    ]
                    
                    st.dataframe(audit_trail, use_container_width=True)
                    
                    # Download results
                    st.subheader("💾 Download Results")
                    results_json = json.dumps(demo_audit_data, indent=2)
                    st.download_button(
                        label="📥 Download Compliance Report (JSON)",
                        data=results_json,
                        file_name=f"compliance_report_{uploaded_file.name}.json",
                        mime="application/json"
                    )
    
    else:
        st.info("👆 Please upload a PDF document to begin analysis")
        
        # Show sample files
        st.subheader("📁 Sample Documents")
        st.write("You can test with these sample documents:")
        
        sample_files = [
            "Supplier1_quote.pdf",
            "Supplier2_quote.pdf", 
            "star-enterprise-audit-form.pdf"
        ]
        
        for file in sample_files:
            if os.path.exists(f"sample_files/{file}"):
                with open(f"sample_files/{file}", "rb") as f:
                    st.download_button(
                        label=f"📄 Download {file}",
                        data=f.read(),
                        file_name=file,
                        mime="application/pdf"
                    )
    
    # Features section
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

if __name__ == "__main__":
    main()
