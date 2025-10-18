import bcrypt


def hash_password(password: str) -> str:
    password = password.encode()
    password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
    return password_hash.decode()

def check_password(password: str, hashed_password: str) -> bool:
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password, hashed_password)