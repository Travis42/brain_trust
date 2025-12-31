"""Configuration module for brain trust CLI application.

This module handles loading environment variables and creating
the OpenAI-compatible client for openrouter.ai models.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator


# Load environment variables from .env file if it exists
load_dotenv()


class Config(BaseModel):
    """Configuration model for brain trust CLI application.
    
    Attributes:
        api_key: The openrouter.ai API key (required)
        api_base: The openrouter.ai API base URL
        model: The model name to use
        temperature: Sampling temperature for generation
        top_p: Nucleus sampling parameter
    """
    
    api_key: str = Field(..., description="openrouter.ai API key")
    api_base: str = Field(
        default="https://openrouter.ai/api/v1",
        description="openrouter.ai API base URL"
    )
    model: str = Field(
        default="anthropic/claude-3.5-sonnet",
        description="Model name to use"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for generation"
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    
    @field_validator("temperature", "top_p")
    @classmethod
    def validate_range(cls, v: float, info) -> float:
        """Validate that numeric values are within expected ranges."""
        if info.field_name == "temperature" and not (0.0 <= v <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
        if info.field_name == "top_p" and not (0.0 <= v <= 1.0):
            raise ValueError("top_p must be between 0.0 and 1.0")
        return v


def load_config() -> Config:
    """Load configuration from environment variables.
    
    Returns:
        Config: Configuration object with values from environment
        
    Raises:
        ValueError: If OPENROUTER_API_KEY is not set in environment variables
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required but not set. "
            "Please set it in your environment or .env file."
        )
    
    return Config(
        api_key=api_key,
        api_base=os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"),
        model=os.getenv("MODEL", "anthropic/claude-3.5-sonnet"),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        top_p=float(os.getenv("TOP_P", "1.0")),
    )


def get_openai_client(config: Optional[Config] = None) -> ChatOpenAI:
    """Create and return a ChatOpenAI instance configured for openrouter.ai.
    
    Args:
        config: Optional Config object. If not provided, loads from environment.
        
    Returns:
        ChatOpenAI: Configured ChatOpenAI instance for openrouter.ai API
        
    Raises:
        ValueError: If OPENROUTER_API_KEY is not set in environment variables
    """
    if config is None:
        config = load_config()
    
    return ChatOpenAI(
        base_url=config.api_base,
        api_key=config.api_key,
        model=config.model,
        temperature=config.temperature,
        top_p=config.top_p,
    )
