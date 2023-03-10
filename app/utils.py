from passlib.context import CryptContext


#  Encrypting the user password on the database
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


# Comparing the give password against the password stored in the database
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
