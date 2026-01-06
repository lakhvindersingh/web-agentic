"""LLM factory for creating different LLM providers."""
from langchain_core.language_models import BaseChatModel

from config import Config


def create_llm() -> BaseChatModel:
    """Create and return the appropriate LLM based on configuration."""
    llm_type = Config.LLM_TYPE
    model_name = Config.get_model_name()
    
    if llm_type == "gpt" or llm_type == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            api_key=Config.OPENAI_API_KEY,
            temperature=0,
        )
    elif llm_type == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0,
            )
        except ImportError:
            raise ImportError(
                "langchain-google-genai package is required for Gemini. "
                "Install it with: pip install langchain-google-genai"
            )
    else:
        raise ValueError(f"Unsupported LLM_TYPE: {llm_type}")

