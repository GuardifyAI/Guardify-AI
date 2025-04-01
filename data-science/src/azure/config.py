from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class AzureConfig:
    def __init__(
            self,
            api_key: Optional[str] = None,
            api_base: Optional[str] = None,
            api_version: Optional[str] = None,
            deployment_name: Optional[str] = None
    ):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_base = os.getenv("AZURE_OPENAI_API_BASE")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-13")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        print(self.api_key)
        print(self.api_base)
        print(self.api_version)
        print(self.deployment_name)

    def validate(self) -> bool:
        """Validate that all required configuration is present"""
        return all([
            self.api_key,
            self.api_base,
            self.api_version,
            self.deployment_name
        ])
