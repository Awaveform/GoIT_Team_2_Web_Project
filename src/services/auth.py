from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Method verifies the password string with the hashed password string.

    :param plain_password: User password string.
    :param hashed_password: Hashed password.
    :return: True or False if the passwords are equal.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Method generate a hashed string from the passed password.

    :param password: User password string.
    :rtype password: str.
    :return: Hashed password.
    :rtype: str.
    """
    return pwd_context.hash(password)
