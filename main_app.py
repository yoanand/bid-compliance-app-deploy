import streamlit as st
import os
import tempfile
import subprocess
import base64
import re
from Documen_Parsing_Agent import doc_agent
from Compliance_Check_Agent import compliance_checking_agent
from Bid_Scoring_Agent import bid_scoring_agent, pdf_code_agent
from common_agents import summary_agent
import json
import fitz
from streamlit_autorefresh import st_autorefresh
import random



def extract_and_save_code(text, output_filename="pdf_app.py"):
    """
    Extracts Python code from a text block (typically containing markdown-style code blocks),
    replaces any usage of 'insert_html' with 'insert_htmlbox', and writes the cleaned code
    to a specified Python file.
    
    Parameters:
    - text (str): The input text containing Python code, possibly wrapped in triple backticks.
    - output_filename (str): The name of the file where the extracted code will be saved. Defaults to 'pdf_app.py'.
    """
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    code = match.group(1) if match else text
    code = re.sub(r'\binsert_html\b', 'insert_htmlbox', code)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(code)



def pdf_to_report(pdf_path, selected_file_name):
    """
    Processes a procurement bid PDF by running document extraction, compliance checking,
    bid scoring, and generating a PDF report. The function dynamically selects the appropriate
    audit file based on the selected supplier quote.

    Args:
        pdf_path (str): Path to the uploaded bid PDF file.
        selected_file_name (str): Name of the selected file (used to determine supplier).
    """
    progress = st.progress(0)
    col1, col2, col3, col4 = st.columns(4)

    with st.spinner("📄 Running Document Agent..."):
        # col1.info("📄 Document Agent is working...")
        doc_agent_response = doc_agent.tool.extract_pdf_to_json(pdf_path=pdf_path, output_path="output.json")
        col1.success("✅ Document Agent completed.")
        progress.progress(25)

    with st.spinner("🔍 Running Compliance Agent..."):
        # results_compliance_knowledgebase = compliance_checking_agent.tool.retrieve(
        #     text=f"Extract the compliance information from the Knowledge Base",
        #     numberOfResults=5,
        #     score=0.5,
        #     knowledgeBaseId="XWJWESUWGC",
        #     region="us-east-1",
        # )
        
        
        # with open("Audit_files/compliance_report.json", 'r', encoding='utf-8') as file:
        #     file_contents = file.read()
        #     compliance_report = json.loads(file_contents)
        
        with open("Audit_files/star-enterprise-audit-form.json", 'r', encoding='utf-8') as file1, \
        open("Audit_files/vendus-supplier-audit-form.json", 'r', encoding='utf-8') as file2:
            star_enterprise_data = json.load(file1)
            vendus_supplier_data = json.load(file2)
        compliance_report = {
            "star_enterprise_audit": star_enterprise_data,
            "vendus_supplier_audit": vendus_supplier_data
        }
        
        compliance_query = f"""
            Given the following procurement bid data extracted from a PDF (in JSON format):

            ```json
            {doc_agent_response}
            ```
            Analyze the data to extract and summarize all relevant information for compliance checking.
            The data includes supplier profiles, contacts, certifications, standards, pricing, quantities, delivery schedules, ESG and sustainability declarations, terms, conditions, and any other facts or entities present.
            Do not restrict yourself to specific keywords; include any detail that may be important for procurement, compliance, scoring, or audit.
            Ensure to organize the output in a clear, structured format (preferably JSON), grouping related information together. If you find tables, summarize their contents as well.

            The data is structured as follows:
            - Supplier Name
            - Compliance Table (criterion, status, evidence, reasoning, remediation)
            - Summary of compliance status
            - Recommendations for shipping and remediation
            - References to supporting documents
            - Any additional observations or risks identified

            The compliance checking agent is designed to analyze procurement bid data and extract relevant information for compliance checking.
            ```json
            {compliance_report}
            ```
            Return a comprehensive summary of all extracted information.
        """
        compliance_agent_response = compliance_checking_agent(compliance_query)
        col2.success("✅ Compliance Agent completed.")
        progress.progress(50)

    with st.spinner("📊 Running Bid Scoring Agent..."):
        
# Determine which audit file to load based on selected quote
        if "supplier1_quote" in selected_file_name.lower():
            audit_file_path = "Audit_files/supplier1_audit.json"
        elif "supplier2_quote" in selected_file_name.lower():
            audit_file_path = "Audit_files/supplier2_audit.json"
        else:
            st.error("❌ Could not determine the correct audit file.")
            return

        with open(audit_file_path, 'r', encoding='utf-8') as file:
            file_contents = file.read()
            audit_file_info = json.loads(file_contents)

        # results_bid_knowledgebase = bid_scoring_agent.tool.retrieve(
        # text=f"what are the audit criteria for the supplier information : {doc_agent_response}",
        # numberOfResults=6,
        # score=0.6,
        # knowledgeBaseId="LYBTVVJ3TA",
        # region="us-east-1",
        #     )
        # st.write("Bid Knowledge Base Results:", results_bid_knowledgebase)

        bid_query = f"""
        You will use the outputs from the Document Validation Agent and the Compliance Checking Agent to assess each bid independently and comparatively and analyze the audit information to provide accurate bid score.
        Supplier information is as follows: {doc_agent_response}
        Compliance Information : {compliance_agent_response}
        Audit Information: {audit_file_info}
        """
        bid_agent_response = bid_scoring_agent(bid_query)
        col3.success("✅ Bid Scoring completed.")
        progress.progress(75)

    with st.spinner("🧠 Generating PDF Report..."):
        # col4.info("🧠 PDF Code Agent is generating report...")
        attempt_count = 0
        success = False
        max_attempts = 5  # Set your maximum attempts here
        while not success and attempt_count < max_attempts:
            attempt_count += 1
            pdf_agent_response = pdf_code_agent(
                "You have to analyze the following bid evaluation data and extract and convert it into html and then use html to generate python code for the json given in response" + str(bid_agent_response)
            )
            extract_and_save_code(str(pdf_agent_response), "pdf_app.py")

            try:
                subprocess.run(["python", "pdf_app.py"], check=True)
                success = True
                col4.success(f"✅ PDF Report generated (attempt #{attempt_count})")
            except subprocess.CalledProcessError:
                col4.warning(f"⚠️ Attempt #{attempt_count} failed. Retrying...")
                
        if not success:
            st.error(f"❌ Failed to generate PDF report after {max_attempts} attempts.")
            return

    progress.progress(100)

    pdf_output_path = os.path.join(os.getcwd(), "bid_evaluation_report.pdf")
    if os.path.exists(pdf_output_path):
        with open(pdf_output_path, "rb") as f:
            pdf_bytes = f.read()
            b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_display = f'''
                <iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600px" type="application/pdf" style="border:none;"></iframe>
            '''
            st.markdown("#### 📑 Bid Evaluation Report")
            st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.error("❌ bid_evaluation_report.pdf not found.")

def fetch_latest_news():
    sample_news = [
        "Alert: New US-EU-China trade measures may delay autonomous procurement bids due to shifting eligibility and supply chain disruptions."    
        ]
    return sample_news

def main():
    """
    Main function to run the Autonomous Procurement Bid Agent Streamlit app.

    This function sets up the user interface for uploading procurement bid PDFs,
    extracting summaries using a document agent, and allowing users to process
    individual bids through compliance checking, bid scoring, and PDF report generation.

    Features:
    - Upload multiple PDF bid documents
    - Automatically extract and summarize each bid
    - Display summaries in a tabbed interface
    - Allow users to select and process a specific bid
    - Generate a final PDF report with compliance and scoring analysis
    """
    
    # --- Notification popup code start ---
    # Initialize news index in session state
    if "news_index" not in st.session_state:
        st.session_state.news_index = 0
    
    all_news = fetch_latest_news()
    news_items_js_array = str([str(item) for item in all_news])  # JS array of news

    notification_html = f"""
    <div id="supplyNews" style="
        position: fixed; top: 20px; right: 20px;
        background-color: #fff3cd;
        color: #856404;
        padding: 15px 20px;
        border: 1px solid #ffeeba;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 9999;
        width: 400px;
        font-size: 14px;
        max-width: 90vw;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <b>🔔 Supply Chain Alert</b>
            <span onclick="document.getElementById('supplyNews').style.display='none'" style="cursor:pointer;">✖️</span>
        </div>
        <div id="newsContent" style="margin-top: 5px;">{all_news[0]}</div>
    </div>

    <script>
        var newsList = {news_items_js_array};
        var idx = 0;
        function showNextNews() {{
            idx = (idx + 1) % newsList.length;
            document.getElementById('newsContent').innerText = newsList[idx];
        }}
        setInterval(showNextNews, 10000);
    }}
    </script>
    """
    st.markdown(notification_html, unsafe_allow_html=True)
        
    # # Add a manual refresh button in the sidebar
    # with st.sidebar:
    #     if st.button("🔄 Refresh News", key="refresh_news_btn"):
    #         st.session_state.news_index = (st.session_state.news_index + 1) % len(all_news)
    #         st.rerun()
    
    # --- Notification popup code end ---
    
    
    st.set_page_config(page_title="Autonomous Bid Agent", layout="wide")
    st.title("Autonomous Procurement Bid Agent")

    with st.sidebar:
        uploaded_files = st.file_uploader("📄 Upload Bid PDFs", type=["pdf"], accept_multiple_files=True)

    if not uploaded_files:
        st.info("📢 Upload the quotations to begin.")
        return

    # Store summaries and paths
    pdf_data = {}
    
    # Check if we've already processed these files to prevent re-processing on auto-refresh
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}
    
    # Only process files if they haven't been processed before
    files_to_process = []
    for pdf_file in uploaded_files:
        if pdf_file.name not in st.session_state.processed_files:
            files_to_process.append(pdf_file)
    
    # Process new files
    for idx, pdf_file in enumerate(files_to_process):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(pdf_file.read())
            pdf_path = tmp_pdf.name

        with st.spinner(f"📄 Processing pdf ..."):
            doc_agent_response = doc_agent.tool.extract_pdf_to_json(pdf_path=pdf_path, output_path=f"output_{idx}.json")
            summary_prompt = f"Summarize the following procurement bid data:\n\n{doc_agent_response}"
            summary_response = summary_agent(summary_prompt)

        pdf_data[pdf_file.name] = {
            "path": pdf_path,
            "summary": summary_response
        }
        # Mark this file as processed
        st.session_state.processed_files[pdf_file.name] = {
            "path": pdf_path,
            "summary": summary_response
        }
    
    # Load previously processed files
    for file_name, file_data in st.session_state.processed_files.items():
        if file_name not in pdf_data:
            pdf_data[file_name] = file_data

    # Tabs
    tab1, tab2 = st.tabs(["📋 Summary of All Bids", "⚙️ Process Bid Area"])

    with tab1:
        st.subheader("📄 Bid Summaries")
        for name, data in pdf_data.items():
            with st.expander(f"{name}"):
                st.markdown(f"**Summary:**\n\n{data['summary']}")

    with tab2:
        st.subheader("⚙️ Process a Bid")
        with st.sidebar:
            selected_file = st.radio("Select a bid to process:", list(pdf_data.keys()))
            process_btn = st.button("Process this bid")

        if process_btn and selected_file:
            st.markdown(f"### Processing: {selected_file}")
            pdf_to_report(pdf_data[selected_file]["path"], selected_file)


if __name__ == "__main__":
    main()
