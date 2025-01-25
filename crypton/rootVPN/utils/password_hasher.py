import bcrypt

def hash_password(password: str) -> str:
    # Генерируем соль
    salt = bcrypt.gensalt()
    # Хэшируем пароль с использованием соли
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    # Проверяем, соответствует ли введенный пароль хэшу
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
