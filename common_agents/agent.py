import boto3
from strands.models import BedrockModel
from strands import Agent
import os
from strands import Agent

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
 

## Bid Scoring Agent
summary_agent = Agent(model=bedrock_model,
                          system_prompt = """
You are a smart document summaizer. Read the attached vendor invoice and generate a clear, concise summary in plain text. Include the following key details:
 
Format the summary in a professional and readable paragraph or bullet points. If any information is missing, simply skip it without guessing.
"""
 )










