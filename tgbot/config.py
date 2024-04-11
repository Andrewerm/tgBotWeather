import os
from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DbConfig:
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    database : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """

    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    # For SQLAlchemy
    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None) -> str:
        """
        Constructs and returns a SQLAlchemy URL for this database configuration.
        """
        # TODO: If you're using SQLAlchemy, move the import to the top of the file!
        from sqlalchemy.engine.url import URL

        if not host:
            host = self.host
        if not port:
            port = self.port
        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )
        return uri.render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env):
        """
        Creates the DbConfig object from environment variables.
        """
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: list[int]
    use_redis: bool
    webhook_url: Optional[str]

    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = env.list("ADMINS", subcast=int)
        use_redis = env.bool("USE_REDIS")
        webhook_url = env("WEBHOOK_URL", default=None)

        return TgBot(token=token, admin_ids=admin_ids, use_redis=use_redis, webhook_url=webhook_url)


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_pass : Optional(str)
        The password used to authenticate with Redis.
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.
        """
        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(
            redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host
        )


@dataclass
class WeatherServiceConfig:
    api_key: str
    lang: str

    @staticmethod
    def from_env(env: Env):
        api_key = env.str("YA_WEATHER")
        lang = "ru_RU"
        return WeatherServiceConfig(api_key=api_key, lang=lang)


@dataclass
class GeoServiceConfig:
    api_key: str
    lang: str

    @staticmethod
    def from_env(env: Env):
        api_key = env.str("YA_GEO")
        lang = "ru_RU"
        return GeoServiceConfig(api_key=api_key, lang=lang)


@dataclass
class Miscellaneous:
    app_env: str
    """
    Miscellaneous configuration class.

    This class holds settings for various other parameters.
    It merely serves as a placeholder for settings that are not part of other categories.

    Attributes
    ----------
    other_params : str, optional
        A string used to hold other various parameters as required (default is None).
    """

    other_params: Optional[str] = None

    @staticmethod
    def from_env(env: Env):
        app_env = env.str("APP_ENV")
        return Miscellaneous(app_env=app_env)


@dataclass
class YandexGptConfig:
    api_key: str
    service_url: str
    gpt_lite_uri: str

    @staticmethod
    def from_env(env: Env):
        api_key = env.str('YA_CHAT_GPT')
        url = env.str('YA_GPT_URL')
        gpt_lite_uri = env.str('YA_GPT_LITE_URI')
        return YandexGptConfig(api_key=api_key, service_url=url, gpt_lite_uri=gpt_lite_uri)


@dataclass
class Config:
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    tg_bot : TgBot
        Holds the settings related to the Telegram Bot.
    misc : Miscellaneous
        Holds the values for miscellaneous settings.
    db : Optional[DbConfig]
        Holds the settings specific to the database (default is None).
    redis : Optional[RedisConfig]
        Holds the settings specific to Redis (default is None).
    """

    tg_bot: TgBot
    misc: Miscellaneous
    gpt: YandexGptConfig
    db: Optional[DbConfig] = None
    redis: Optional[RedisConfig] = None
    weather: Optional[WeatherServiceConfig] = None
    geo: Optional[GeoServiceConfig] = None


def load_config() -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """

    current_app_env: str = os.getenv('APP_ENV')
    if not current_app_env:
        raise Exception('Переменная окружения APP_ENV не указана')
    # Create an Env object.
    # The Env object will be used to read environment variables.
    env = Env()
    env.read_env()
    env.read_env('.env.' + current_app_env.lower())

    return Config(
        tg_bot=TgBot.from_env(env),
        # db=DbConfig.from_env(env),
        redis=RedisConfig.from_env(env),
        misc=Miscellaneous.from_env(env),
        weather=WeatherServiceConfig.from_env(env),
        geo=GeoServiceConfig.from_env(env),
        gpt=YandexGptConfig.from_env(env)
    )
