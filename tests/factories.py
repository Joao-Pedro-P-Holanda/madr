# pyright: reportMissingTypeArgument=false
# pyright: reportIncompatibleVariableOverride=false
import factory

from madr.schema import AuthorCreate, BookCreate, UserCreate

factory.Faker._DEFAULT_LOCALE = "pt_BR"


def num_to_roman(n: int) -> str:
    """
    Fonte: https://www.geeksforgeeks.org/python/python-program-to-convert-integer-to-roman/
    """
    num = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]
    sym = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12

    s = ""

    while n:
        div = n // num[i]
        n %= num[i]

        while div:
            s += sym[i]
            div -= 1
        i -= 1
    return s


class UserCreateFactory(factory.Factory):
    class Meta:
        model = UserCreate

    username = factory.Faker("name")
    email = factory.Sequence(lambda n: f"email{n}@test.com")
    password = factory.Faker("password", length=8)


class BookCreateFactory(factory.Factory):
    class Meta:
        model = BookCreate

    isbn = factory.Faker("isbn13", separator="")

    @factory.sequence
    def name(n):
        return f"Livro {num_to_roman(n)}"

    year = factory.Faker("year")


class AuthorCreateFactory(factory.Factory):
    class Meta:
        model = AuthorCreate

    @factory.sequence
    def name(n):
        return f"Autor {num_to_roman(n)}"

    birth_date = factory.Faker("date")
    nationality = factory.Faker("country")
