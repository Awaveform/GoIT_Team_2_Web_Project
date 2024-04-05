from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Method verifies the password string with the hashed password string.

    :param plain_password: str: User password string.
    :type plain_password: str
    :param hashed_password: str: Hashed password.
    :type hashed_password: str
    :return: bool: True or False if the passwords are equal.
    :rtype: bool
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
