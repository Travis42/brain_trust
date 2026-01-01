"""Exemplar loader module for brain trust CLI application.

This module handles loading and formatting exemplar data for persona prompts.
Exemplars are real people with track records that provide social proof for
persona recommendations.
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path


class Exemplar:
    """Represents a single exemplar with a name.
    
    Attributes:
        name: The name of the exemplar
    """
    
    def __init__(self, name: str):
        self.name = name
    
    def format_for_prompt(self) -> str:
        """Format this exemplar for injection into persona prompts.
        
        Returns:
            The exemplar's name.
        """
        return self.name


def load_exemplars_for_persona(
    persona_name: str,
    exemplars_dir: Optional[str] = None
) -> List[Exemplar]:
    """Load exemplars for a specific persona from JSON file.
    
    Args:
        persona_name: The name of the persona (e.g., "strategist")
        exemplars_dir: Optional path to exemplars directory. If None, uses
                      default "data/exemplars" relative to project root.
        
    Returns:
        List of Exemplar objects for the persona. Empty list if file not found
        or if persona has no exemplars.
        
    Raises:
        ValueError: If exemplars file exists but is malformed JSON.
    """
    # Determine exemplars directory
    if exemplars_dir is None:
        # Default to data/exemplars relative to project root
        project_root = Path(__file__).parent.parent
        exemplars_dir = project_root / "data" / "exemplars"
    else:
        exemplars_dir = Path(exemplars_dir)
    
    # Build path to persona's exemplar file
    exemplar_file = exemplars_dir / f"{persona_name}.json"
    
    # Return empty list if file doesn't exist (not an error)
    if not exemplar_file.exists():
        return []
    
    # Load and parse JSON file
    try:
        with open(exemplar_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Malformed JSON in exemplar file {exemplar_file}: {e}"
        )
    except Exception as e:
        raise ValueError(
            f"Error reading exemplar file {exemplar_file}: {e}"
        )
    
    # Validate basic structure
    if not isinstance(data, dict):
        raise ValueError(
            f"Exemplar file {exemplar_file} must contain a JSON object"
        )
    
    if "exemplars" not in data:
        return []
    
    exemplars_data = data["exemplars"]
    if not isinstance(exemplars_data, list):
        raise ValueError(
            f"'exemplars' field in {exemplar_file} must be a list"
        )
    
    # Parse exemplars - new format: list of names (strings)
    exemplars = []
    for exemplar_data in exemplars_data:
        if isinstance(exemplar_data, str):
            # New format: string name
            exemplar = Exemplar(name=exemplar_data)
            exemplars.append(exemplar)
        elif isinstance(exemplar_data, dict):
            # Backward compatibility: old format with dict
            try:
                exemplar = Exemplar(name=exemplar_data["name"])
                exemplars.append(exemplar)
            except KeyError as e:
                raise ValueError(
                    f"Exemplar in {exemplar_file} missing required field: {e}"
                )
        else:
            raise ValueError(
                f"Exemplar in {exemplar_file} must be a string or dict"
            )
    
    return exemplars


def format_exemplars_for_prompt(exemplars: List[Exemplar]) -> str:
    """Format a list of exemplars for injection into persona prompts.
    
    Args:
        exemplars: List of Exemplar objects
        
    Returns:
        A formatted string ready for injection into system prompts.
        Returns empty string if no exemplars provided.
    """
    if not exemplars:
        return ""
    
    # Get comma-separated list of names
    names = ", ".join([exemplar.name for exemplar in exemplars])
    
    return f"""=== EXEMPLARS ===
These are real people with proven track records whose expertise aligns with this
persona. When providing recommendations, research these individuals from your
knowledge base and cite specific actions, decisions, or approaches they took
that support your advice.

Exemplars: {names}

=== END EXEMPLARS ==="""


def get_exemplars_prompt_block(
    persona_name: str,
    exemplars_dir: Optional[str] = None
) -> str:
    """Load and format exemplars for a persona as a prompt block.
    
    This is a convenience function that combines loading and formatting.
    
    Args:
        persona_name: The name of the persona
        exemplars_dir: Optional path to exemplars directory
        
    Returns:
        A formatted string ready for injection into system prompts.
        Returns empty string if no exemplars found.
    """
    exemplars = load_exemplars_for_persona(persona_name, exemplars_dir)
    return format_exemplars_for_prompt(exemplars)
