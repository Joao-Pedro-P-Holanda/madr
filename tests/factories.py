# pyright: reportMissingTypeArgument=false
# pyright: reportIncompatibleVariableOverride=false
import factory
from sqlalchemy.orm import Session
from madr.core.security import hash_password
from madr.models import User
from madr.schema import UserCreate


class UserCreateFactory(factory.Factory):
    class Meta:
        model = UserCreate

    username = factory.Faker("name")
    email = factory.Faker("email")
    password = factory.Faker("password", length=8)
