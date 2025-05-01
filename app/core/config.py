from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # SMTP settings
    # MAIL_USERNAME: str = "your-email@gmail.com"
    # MAIL_PASSWORD: str = "your-app-password"
    # MAIL_FROM: str = "your-email@gmail.com"
    # MAIL_PORT: int = 587
    # MAIL_SERVER: str = "smtp.gmail.com"
    # MAIL_TLS: bool = True
    # MAIL_SSL: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
