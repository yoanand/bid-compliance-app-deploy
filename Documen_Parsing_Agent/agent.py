from strands import Agent
from strands_tools import retrieve
from .doc_tool import extract_pdf_to_json 
import boto3
from strands.models import BedrockModel
from strands import Agent
import os
  
# Create a custom boto3 session
session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),  
    region_name=os.environ.get('AWS_REGION'),
)

# Create a Bedrock model instance
bedrock_model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",   # Nova Pro
    boto_session=session,
)
 
 
doc_agent = Agent(model=bedrock_model, tools=[extract_pdf_to_json],
        system_prompt=('''You are a helpful agent that can extract text from PDF files and save it as JSON.
                       You have to understand the what are topic and subtopic in the PDF file and treat as key and values for JSON.
                       You have to understand the structured of text in pdf and save each line as a separate JSON object.
                       You can also use other tools to assist in your tasks.
                       Return only the JSON object, using double quotes for all keys and values, and no explanation or markdown.
                       '''))
 
 