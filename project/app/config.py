class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'  # или используйте PostgreSQL, MySQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'supersecretkey'  # Используйте более сильный ключ
    JWT_SECRET_KEY = 'your_jwt_secret_key'  # Для JWT
