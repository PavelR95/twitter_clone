from faker import Faker

faker = Faker()


class FactoryUser:
    """Генератор случайных данных пользователя
    """

    def __init__(self) -> None:
        self.name: str = faker.name()
        self.api_key: str = faker.text(max_nb_chars=10)

    def get_dict(self) -> dict[str, str]:
        return {"name": self.name, "api_key": self.api_key}


class FactoryTweets:
    """Генератор случайных данных для твита
    """

    def __init__(self) -> None:
        self.content: str = faker.text(max_nb_chars=100)

    def get_dict(self) -> dict[str, str]:
        return {"content": self.content}
