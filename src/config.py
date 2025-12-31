"""Configuration module for brain trust CLI application.

This module handles loading environment variables and creating
the OpenAI-compatible client for z.ai GLM models.
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
        api_key: The z.ai API key (required)
        api_base: The z.ai API base URL
        model: The model name to use
        temperature: Sampling temperature for generation
        top_p: Nucleus sampling parameter
    """
    
    api_key: str = Field(..., description="z.ai API key")
    api_base: str = Field(
        default="https://api.z.ai/v1",
        description="z.ai API base URL"
    )
    model: str = Field(
        default="glm-4",
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
        ValueError: If ZAI_API_KEY is not set in environment variables
    """
    api_key = os.getenv("ZAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "ZAI_API_KEY environment variable is required but not set. "
            "Please set it in your environment or .env file."
        )
    
    return Config(
        api_key=api_key,
        api_base=os.getenv("ZAI_API_BASE", "https://api.z.ai/v1"),
        model=os.getenv("MODEL", "glm-4"),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        top_p=float(os.getenv("TOP_P", "1.0")),
    )


def get_openai_client(config: Optional[Config] = None) -> ChatOpenAI:
    """Create and return a ChatOpenAI instance configured for z.ai.
    
    Args:
        config: Optional Config object. If not provided, loads from environment.
        
    Returns:
        ChatOpenAI: Configured ChatOpenAI instance for z.ai API
        
    Raises:
        ValueError: If ZAI_API_KEY is not set in environment variables
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
