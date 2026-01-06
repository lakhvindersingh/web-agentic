"""Configuration loading from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    LLM_TYPE: str = os.getenv("LLM_TYPE", "gpt").lower()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    MODEL: str = os.getenv("MODEL", "")
    
    # MCP Configuration
    MCP_ENABLED: bool = os.getenv("MCP_ENABLED", "false").lower() == "true"
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default model based on LLM type."""
        defaults = {
            "gpt": "gpt-4o-mini",
            "gemini": "gemini-pro",
            "openai": "gpt-4o-mini",
        }
        return defaults.get(cls.LLM_TYPE, "gpt-4o-mini")
    
    @classmethod
    def get_model_name(cls) -> str:
        """Get the model name, using default if not specified."""
        model = cls.MODEL if cls.MODEL else cls.get_default_model()
        
        # Warn if model name doesn't match LLM type
        if cls.MODEL:
            if cls.LLM_TYPE in ["gpt", "openai"] and model.startswith("gemini"):
                raise ValueError(
                    f"Model '{model}' is not compatible with LLM_TYPE '{cls.LLM_TYPE}'. "
                    "Use a GPT model like 'gpt-4o-mini' or change LLM_TYPE to 'gemini'."
                )
            elif cls.LLM_TYPE == "gemini" and (model.startswith("gpt") or model.startswith("o1")):
                raise ValueError(
                    f"Model '{model}' is not compatible with LLM_TYPE '{cls.LLM_TYPE}'. "
                    "Use a Gemini model like 'gemini-pro' or change LLM_TYPE to 'gpt'."
                )
        
        return model
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if cls.LLM_TYPE == "gpt" or cls.LLM_TYPE == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY environment variable is required when LLM_TYPE is 'gpt' or 'openai'. "
                    "Set it in your .env file or environment."
                )
        elif cls.LLM_TYPE == "gemini":
            if not cls.GOOGLE_API_KEY:
                raise ValueError(
                    "GOOGLE_API_KEY environment variable is required when LLM_TYPE is 'gemini'. "
                    "Set it in your .env file or environment."
                )
        else:
            raise ValueError(
                f"Unsupported LLM_TYPE: {cls.LLM_TYPE}. "
                "Supported types: 'gpt', 'openai', 'gemini'"
            )

