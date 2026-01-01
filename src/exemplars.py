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
    """Represents a single exemplar with track record and notable actions.
    
    Attributes:
        name: The name of the exemplar
        track_record: Brief description of their achievements and status
        constraints: Contextual constraints they operated under
        notable_actions: List of specific actions they took
        public_refs: List of public references/links
    """
    
    def __init__(
        self,
        name: str,
        track_record: str,
        constraints: str,
        notable_actions: List[str],
        public_refs: List[str]
    ):
        self.name = name
        self.track_record = track_record
        self.constraints = constraints
        self.notable_actions = notable_actions
        self.public_refs = public_refs
    
    def format_for_prompt(self) -> str:
        """Format this exemplar for injection into persona prompts.
        
        Returns:
            A formatted string describing the exemplar's track record,
            constraints, and notable actions.
        """
        actions_text = "\n    - ".join(self.notable_actions)
        refs_text = ", ".join(self.public_refs) if self.public_refs else "No public references"
        
        return f"""{self.name}
  Track Record: {self.track_record}
  Constraints: {self.constraints}
  Notable Actions:
    - {actions_text}
  References: {refs_text}"""


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
    
    # Parse exemplars
    exemplars = []
    for exemplar_data in exemplars_data:
        try:
            exemplar = Exemplar(
                name=exemplar_data["name"],
                track_record=exemplar_data["track_record"],
                constraints=exemplar_data["constraints"],
                notable_actions=exemplar_data["notable_actions"],
                public_refs=exemplar_data.get("public_refs", [])
            )
            exemplars.append(exemplar)
        except KeyError as e:
            raise ValueError(
                f"Exemplar in {exemplar_file} missing required field: {e}"
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
    
    formatted = "\n\n".join([
        exemplar.format_for_prompt()
        for exemplar in exemplars
    ])
    
    return f"""=== EXEMPLARS ===
These are real people with proven track records whose actions and decisions
provide social proof for this persona's recommendations. When you provide advice,
you MUST look into your memory of these exemplars and cite specific actions
they took that support your recommendations.

{formatted}

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
