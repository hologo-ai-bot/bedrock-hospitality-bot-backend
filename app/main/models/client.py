from mongoengine import Document, StringField, EmailField, DateTimeField, IntField, BooleanField
import datetime

class Client(Document):
    meta = {'collection': 'clients'}  # Collection name in MongoDB

    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True)
    password = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    tkns_remaining = IntField(default=0)
    tkns_used = IntField(default=0)
    is_active = BooleanField(default=True) 
    # version = IntField(default=0) 
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f"<Client {self.username}>"
    
    # def save(self, *args, **kwargs):
    #     self.version += 1
    #     super(Client, self).save(*args, **kwargs)

    def to_json(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "tokens remaining": self.tkns_remaining,
            "tokens used": self.tkns_used,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
