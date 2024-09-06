from mongoengine import Document, StringField, EmailField, DateTimeField, IntField, BooleanField
import datetime

class Hologo(Document):
    meta = {'collection': 'hologo'}  # Collection name in MongoDB

    username = StringField(required=True, unique=True, max_length=50)
    tkns_remaining = IntField(default=0)
    tkn_used = IntField(default=0)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f"<Hologo {self.username}>"

    def to_json(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "Remaining tokens": self.tkns_remaining ,
            "tokens used": self.tkn_used ,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
