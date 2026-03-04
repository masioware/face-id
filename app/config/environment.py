from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FACEID_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ws_max_frame_bytes: int = 2_500_000
    ws_accept_text_messages: bool = False


settings = Settings()
