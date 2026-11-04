from argon2 import PasswordHasher

passwordhasher = PasswordHasher()

def hash_pw(password: str) -> str:
    hashed_password = passwordhasher.hash(password)
    return hashed_password

def verify_pw(password: str, hashed_password: str) -> bool:
    return passwordhasher.verify(hashed_password, password)