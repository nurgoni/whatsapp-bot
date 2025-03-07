from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str
    
    API_URL: str
    WHATSAPP_API_TOKEN: str
    WHATSAPP_CLOUD_NUMBER_ID: str
    VERIFY_TOKEN: str
    OPENAI_API_KEY: str
    API_URL_OPENAI: str

    @property
    def API_URL_WHATSAPP(self):
        return f"{self.API_URL}{self.WHATSAPP_CLOUD_NUMBER_ID}"

    class Config(SettingsConfigDict):
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
