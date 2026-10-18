import bcrypt

def hash_pw(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    password = hashed_password.decode()

    return password

def verify_pw(password: str, hashed_password: str) -> bool:
    password = password.encode()
    hashed_password = hashed_password.encode()

    return bcrypt.checkpw(password, hashed_password)