from dotenv.main import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    :param sqlalchemy_database_url: str: The URL for the SQLAlchemy database.
    :type sqlalchemy_database_url: str
    :param sqlalchemy_test_database_url: str: The URL for the test database used for testing.
    :type sqlalchemy_test_database_url: str
    :param rate_limit_requests_per_minute: int: The maximum number of requests allowed per minute for rate limiting.
    :type rate_limit_requests_per_minute: int
    :param redis_host: str: The host address for the Redis server.
    :type redis_host: str
    :param redis_port: int: The port number for the Redis server.
    :type redis_port: int
    :param redis_password: str: The host address for the Redis server.
    :type redis_password: str
    :param authjwt_secret_key: str: The secret key used for JWT authentication.
    :type authjwt_secret_key: str
    :param authjwt_algorithm: str: The algorithm used for JWT authentication.
    :type authjwt_algorithm: str
    :param cloudinary_name: str: The Cloudinary account name.
    :type cloudinary_name: str
    :param cloudinary_api_key: str: The API key for accessing Cloudinary services.
    :type cloudinary_api_key: str
    :param cloudinary_api_secret: str: The API secret key for accessing Cloudinary services.
    :type cloudinary_api_secret: str
    :param secret_key: str: The secret key used for encryption and decryption.
    :type secret_key: str
    :param algorithm: str: The encryption algorithm used for encryption and decryption.
    :type algorithm: str
    :param rate_limit_requests_per_minute: int: The maximum number of requests allowed per minute for rate limiting.
    :type rate_limit_requests_per_minute: int
    """
    sqlalchemy_database_url: str
    sqlalchemy_test_database_url: str
    rate_limit_requests_per_minute: int
    redis_host: str
    redis_port: int
    redis_password: str

    authjwt_secret_key: str
    authjwt_algorithm: str

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    secret_key: str
    algorithm: str

    rate_limit_requests_per_minute: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
