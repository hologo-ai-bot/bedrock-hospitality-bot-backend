from main.models.client import Client
import bcrypt
class ClientService:
    def clientRegister(self, username, email, password, first_name, last_name, tkns_remaining):
        try:
            client= Client(
            username=username,
            email=email,
            password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) ,
            first_name=first_name,
            last_name=last_name,
            tkns_remaining=tkns_remaining
            )
            client.save()
            return client
        except Exception:
            return None

    def clientLogin(self, email, password):
        try:
            client = Client.objects.get(email=email)
            if bcrypt.checkpw(password.encode('utf-8'), client.password.encode('utf-8') ):
                return True
            else:
                return False
        except Client.DoesNotExist:
            return None
    
    def returnClient(self, username):
        try:
            client = Client.objects.get(username=username)
            return client
        except Client.DoesNotExist:
            return None

    def returnTokenInfo(self, username):
        try:
            client = Client.objects.get(username=username)
            return f"Allocated tokens: {client.tkns_remaining + client.tkns_used}",f"Remaining tokens: {client.tkns_remaining}", f"tokens used: {client.tkns_used}"
        except Client.DoesNotExist:
            return None
        
    def updateClientToken(self, username, addition):
        try:
            client = Client.objects.get(username=username)
            # client.update(inc__tkns_remaining=add_tkn)
            client.tkns_remaining += addition
            client.save()
            return True
        except Client.DoesNotExist:
            return None        
    
    def deleteClient(self, clientId):
        try:
            client = Client.objects.get(id=clientId)
            client.delete()
            return True
        except Client.DoesNotExist:
            return None          
