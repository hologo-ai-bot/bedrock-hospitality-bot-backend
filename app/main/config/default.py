import os

class Config:
    SERVICE_NAME = os.environ.get('SERVICE_NAME')
    ANTHROPIC_VERSION = os.environ.get('ANTHROPIC_VERSION')
    MODEL_ID = os.environ.get('MODEL_ID')
    AGENT_ARN = os.environ.get('AGENT_ARN')
    
    #DB config
    MONGODB_SETTINGS = {
        'host': 'mongodb://localhost:27017/openai'
    }