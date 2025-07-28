from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from models import User

__all__ = ['UserSchemaCreate']


UserSchemaCreate = sqlalchemy_to_pydantic(User, exclude=['id'])
