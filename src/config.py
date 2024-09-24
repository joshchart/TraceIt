from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str
    echo_sql: bool = True

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
