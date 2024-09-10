import os

class Config:
    REGION_NAME = os.environ.get('REGION_NAME')
    AGENT_ID = os.environ.get('AGENT_ID')
    AGENT_ALIAS_ID = os.environ.get('AGENT_ALIAS_ID')
    SERVICE_NAME = os.environ.get('SERVICE_NAME')
    ANTHROPIC_VERSION = os.environ.get('ANTHROPIC_VERSION')
    MODEL_ID = os.environ.get('MODEL_ID')
    AGENT_ARN = os.environ.get('AGENT_ARN')
    
    #DB config
    MONGODB_SETTINGS = {
        'host': 'mongodb://localhost:27017/openai'
    }