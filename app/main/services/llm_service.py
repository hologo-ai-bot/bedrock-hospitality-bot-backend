from main.models.client import Client
from threading import  Lock
import boto3
from botocore.client import BaseClient
from flask import current_app
import json
import tiktoken

class LLMService:
    
    def __init__(self,  region_name="us-east-1"):
        self.locks = {}
        self.region_name=region_name
        # self.queues = {}

    def get_lock(self, clientId):
        # print("get_lock")
        if clientId not in self.locks:
            self.locks[clientId] = Lock()
        return self.locks[clientId]
    
    def check_client_exists(self, client_id):
        return Client.objects.get(id=client_id) is not None

    def updateTokenUsage(self, clientId, tkns_used):
        # print("updateTokenUsage")
        with self.get_lock(clientId):
            client = Client.objects.get(id=clientId)
            client.tkns_used += tkns_used
            client.tkns_remaining -= tkns_used
            client.save()
            
    def _return_aws_service_client(self, resource_name='bedrock', run_time=True) -> BaseClient:
        if resource_name == "bedrock":
            if run_time:
                service_client = boto3.client(
                    service_name="bedrock-agent-runtime",
                    region_name=self.region_name)
            else:
                service_client = boto3.client(
                    service_name="bedrock-agent",
                    region_name=self.region_name)
        elif resource_name == "iam":
            service_client = boto3.resource("iam")
    
        return service_client 
             
    def process_request(self, message, clientId):
        try:
            service_name = current_app.config['SERVICE_NAME']
            anthropic_version = current_app.config['ANTHROPIC_VERSION']
            model_id = current_app.config['MODEL_ID']
            client = self._return_aws_service_client(run_time=True)
            bedrock = boto3.client(service_name=service_name)
            # response = client.retrieve(
            #     knowledgeBaseId="JSJBCTXXAL",
            #     retrievalQuery={'text': message},
            #     retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 2}},
            #     nextToken='booking'
            # )
            # Extract the relevant text from the retrieval response
            # retrieved_texts = [result['content']['text'] for result in response['retrievalResults']]
            # combined_retrieved_text = " ".join(retrieved_texts)
            # print("------------------------------")
            # print(response)
            # print("------------------------------")
            # # Step 2: Combine the retrieved information with the original message
            # input_message = f"{combined_retrieved_text}\n\nUser query: {message}"

            # Step 3: Invoke the bot or model with the combined input
            service_client = self._return_aws_service_client(resource_name='bedrock', run_time=True)
            
            
            
            body = json.dumps({
                        "max_tokens": 1000,
                        "messages": [{"role": "user", "content": message}],
                        "anthropic_version": anthropic_version
            })
            
            response = bedrock.invoke_model(body=body, modelId=model_id)
            
            response_body = json.loads(response['body'].read().decode('utf-8'))
            response_content = response_body.get("content")
            # response = bedrock.invoke_model(body=body, modelId=model_id)
            # # print("response : ", response)
            # # print("---------------------")
            # response_body = json.loads(response['body'].read().decode('utf-8'))
            # # print("response body: ", response_body)
            # # print("---------------------")
            # response_content = response_body.get("content")
            # print("response content: ", response_content)
            # print("---------------------")
            token_usage = response_body.get("usage").get("input_tokens") + response_body.get("usage").get("output_tokens")
            self.updateTokenUsage(clientId, token_usage)
            if isinstance(response_content, list) and len(response_content) > 0:
                text_content = response_content[0].get("text")
                return {
                    "message" : text_content,
                    "token usage" : token_usage
                }
        except Exception as e:  
            return {"error": str(e)} 

    def connectModel(self, message, clientId):
        try:    
            remaining_tkns = self.checkRemainingTokens(clientId)
            # msg_tkn = self.getTokenCount([{"role": "user", "content": message}])
            # if (msg_tkn * 2 >= remaining_tkns) or (remaining_tkns < 1000):
            if (remaining_tkns < 1000):
                return {"error": "Remaining tokens are too low. Please recharge to get replies"}
            if remaining_tkns <= 0:
                return {"error": "Token limit reached"}
            result = self.process_request(message, clientId)
            return result
        
        except Exception as e: 
            return {"error": "Unathorized access"}
        
    def checkRemainingTokens(self, clientId):
        return Client.objects.get(id=clientId).tkns_remaining

    def getTokenCount(self, messages):
        """Returns the number of tokens used by a list of messages."""
        try:
            model = current_app.config['OPENAI_MODEL']
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0125":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>
            return num_tokens
        else:
            raise NotImplementedError(f"""getTokenCount() is not presently implemented for model {model}.""")
