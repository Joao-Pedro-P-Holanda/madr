# pyright: reportMissingTypeArgument=false
# pyright: reportIncompatibleVariableOverride=false
import factory

from madr.schema import AuthorCreate, BookCreate, UserCreate

factory.Faker._DEFAULT_LOCALE = "pt_BR"


class UserCreateFactory(factory.Factory):
    class Meta:
        model = UserCreate

    username = factory.Faker("name")
    email = factory.Faker("email")
    password = factory.Faker("password", length=8)


class BookCreateFactory(factory.Factory):
    class Meta:
        model = BookCreate

    isbn = factory.Faker("isbn13", separator="")
    name = factory.Faker("catch_phrase")
    year = factory.Faker("year")


class AuthorCreateFactory(factory.Factory):
    class Meta:
        model = AuthorCreate

    name = factory.Faker("name")
    birth_date = factory.Faker("date")
    nationality = factory.Faker("country")
