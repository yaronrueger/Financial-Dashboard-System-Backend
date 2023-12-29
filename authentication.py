from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from passlib.hash import bcrypt

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128) 

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    
User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

## Prüft ob Username Passwort kombination richtig, also ob Anmeldung erfolgreich
async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user