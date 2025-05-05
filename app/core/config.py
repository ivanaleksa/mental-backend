from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MAX_PROFILE_IMAGE_SIZE: int = 1 * 1024 * 1024  # 1MB
    ALLOWED_PROFILE_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}

    # SMTP settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool
    MAIL_SSL: bool
    CODE_EXPIRE_MINUTES: int

    MEDIA_DIRECTORY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
