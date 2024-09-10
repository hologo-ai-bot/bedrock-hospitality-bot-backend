from main.models.client import Client
from threading import  Lock
import boto3
import botocore
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from langchain_aws import ChatBedrock
from utils._tokenizers import TokenizerManager
from flask import current_app
import json
import tiktoken


class LLMService:
    
    def __init__(self ):
        self.locks = {}
        self.tokenizer_manager = TokenizerManager()
        # self.queues = {}
        
    def get_token_count(self, text: str) -> int:
        # Get the tokenizer instance
        tokenizer = self.tokenizer_manager.sync_get_tokenizer()
        # Tokenize the input text and get the token IDs
        encoding = tokenizer.encode(text)  # Use encode() to get token information
        
        # Return the number of tokens
        return len(encoding.ids)  # encoding.ids is a list of token IDs
    
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
                   
    def process_request(self, message, clientId):
        try:
            region_name = current_app.config['REGION_NAME']
            agent_id = current_app.config['AGENT_ID']
            agent_alias_id = current_app.config['AGENT_ALIAS_ID']
            model_id = current_app.config['MODEL_ID']
            session_id = "s03"

            completion = ""
            traces = []
            
            config = botocore.config.Config(
                read_timeout=900,
                connect_timeout=900,
                retries={"max_attempts": 0}
            )            
            bedrock_client = boto3.client(
                service_name="bedrock-agent-runtime",
                region_name=region_name,
                config=config
            )
            
            llm = ChatBedrock(client=bedrock_client, model_id=model_id)
            # input_tkns = llm.get_num_tokens(message)
            input_tkns = self.getTokenCount([{"role": "user", "content": message}])
            print("tkn in input : ", input_tkns)
           
            response = bedrock_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=message
            )
            print('response : ',response)
            for event in response.get("completion"):
                print(event)
                try:
                    trace = event["trace"]
                    traces.append(trace['trace'])
                except KeyError:
                    chunk = event["chunk"]
                    completion = completion + chunk["bytes"].decode()
                except Exception as e:
                    print(e)

        except ClientError as e:
            print(e)
        
        print('completion : ',completion)
        print(type(completion))
        # output_tkns = llm.get_num_tokens(completion)
        output_tkns = self.getTokenCount([{"role": "user", "content": completion}])
        self.updateTokenUsage(clientId, (input_tkns + output_tkns))
        print("tkn in output : ", output_tkns)
        return {
            "message": completion,
            "token usage" : input_tkns + output_tkns
        }

    def connectModel(self, message, clientId):
        try:    
            remaining_tkns = self.checkRemainingTokens(clientId)
            msg_tkn = self.getTokenCount([{"role": "user", "content": message}])
            if (msg_tkn * 2 >= remaining_tkns) or (remaining_tkns < 1000):
            # if (remaining_tkns < 1000):
                return {"error": "Remaining tokens are too low. Please recharge to get replies"}
            if remaining_tkns <= 0:
                return {"error": "Token limit reached"}
            result = self.process_request(message, clientId)
            return result
        
        except Exception as e: 
            return {"error": str(e)}
        
    def checkRemainingTokens(self, clientId):
        return Client.objects.get(id=clientId).tkns_remaining

    def getTokenCount(self, messages):
        """Returns the number of tokens used by a list of messages."""
        try:
            model = "gpt-3.5-turbo-0125"
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
