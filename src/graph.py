"""LangGraph module for brain trust CLI application.

This module implements the LangGraph topology with parallel advisors
and private scratchpads for multi-agent deliberation.
"""

from typing import Annotated, TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.config import get_openai_client
from src.personas import PERSONAS, Persona


class BrainTrustState(TypedDict):
    """State schema for the brain trust deliberation graph.
    
    Attributes:
        question: The user's question or topic for deliberation
        selected_personas: Optional list of persona names to use (None = all)
        advisor_outputs: Dictionary mapping persona names to their advisor responses
        scratchpads: Dictionary mapping persona names to their private scratchpad content
        summary: Executive summary produced by the Summarizer
        dissent: List of disagreements identified by the Summarizer
        transcript: Optional transcript for verbose logging
    """
    question: str
    selected_personas: Optional[list[str]]
    advisor_outputs: dict[str, str]
    scratchpads: dict[str, str]
    summary: str
    dissent: list[str]
    transcript: Optional[list[dict]]


def advisor_node(persona_name: str):
    """Create a LangGraph node function for a specific advisor persona.
    
    Args:
        persona_name: The name of the persona (must exist in PERSONAS)
        
    Returns:
        A LangGraph node function that processes the state and updates
        advisor_outputs and scratchpads for this persona
    """
    persona = PERSONAS[persona_name]
    
    def node(state: BrainTrustState) -> BrainTrustState:
        """Process the state as this advisor persona."""
        # Get the LLM client
        llm = get_openai_client()
        
        # Get current scratchpad content for this persona (or empty string if not exists)
        current_scratchpad = state.get("scratchpads", {}).get(persona_name, "")
        
        # Build the prompt with system prompt, question, and current scratchpad
        messages = [
            SystemMessage(content=persona.system_prompt),
            HumanMessage(content=f"""Question: {state['question']}

Your private scratchpad (for your reasoning only, do not include in your final response):
{current_scratchpad if current_scratchpad else "[Empty - start fresh]"}

Please provide your analysis following the structure in your system prompt.

IMPORTANT: Your response should include two parts:
1. Your advisor output (the structured response as specified in your system prompt)
2. Your updated scratchpad (your private reasoning notes)

Format your response as:
=== ADVISOR OUTPUT ===
[your structured advisor response here]

=== SCRATCHPAD ===
[your updated private reasoning notes here]""")
        ]
        
        # Invoke the LLM
        response = llm.invoke(messages)
        response_text = response.content
        
        # Parse the response to extract advisor output and scratchpad
        advisor_output = ""
        updated_scratchpad = ""
        
        if "=== ADVISOR OUTPUT ===" in response_text and "=== SCRATCHPAD ===" in response_text:
            # Split the response
            parts = response_text.split("=== SCRATCHPAD ===")
            advisor_part = parts[0].replace("=== ADVISOR OUTPUT ===", "").strip()
            updated_scratchpad = parts[1].strip() if len(parts) > 1 else ""
            advisor_output = advisor_part
        else:
            # Fallback: treat entire response as advisor output, keep scratchpad unchanged
            advisor_output = response_text
            updated_scratchpad = current_scratchpad
        
        # Update state
        state["advisor_outputs"] = state.get("advisor_outputs", {})
        state["advisor_outputs"][persona_name] = advisor_output
        
        state["scratchpads"] = state.get("scratchpads", {})
        state["scratchpads"][persona_name] = updated_scratchpad
        
        # Add to transcript if verbose logging is enabled
        if state.get("transcript") is not None:
            state["transcript"].append({
                "node": persona_name,
                "advisor_output": advisor_output,
                "scratchpad": updated_scratchpad
            })
        
        return state
    
    # Set the node name for LangGraph
    node.__name__ = persona_name
    return node


def summarizer_node(state: BrainTrustState) -> BrainTrustState:
    """Process the state as the Summarizer persona.
    
    The Summarizer receives all advisor outputs (NOT scratchpads) and produces:
    - An executive summary
    - A list of disagreements (dissent)
    
    Args:
        state: Current state with advisor_outputs populated
        
    Returns:
        Updated state with summary and dissent fields populated
    """
    # Get the Summarizer persona
    summarizer = PERSONAS["summarizer"]
    
    # Get the LLM client
    llm = get_openai_client()
    
    # Build the prompt with all advisor outputs (NOT scratchpads)
    advisor_outputs_text = ""
    for persona_name, output in state.get("advisor_outputs", {}).items():
        persona = PERSONAS.get(persona_name)
        display_name = persona.display_name if persona else persona_name
        advisor_outputs_text += f"\n\n=== {display_name} ({persona_name}) ===\n{output}\n"
    
    messages = [
        SystemMessage(content=summarizer.system_prompt),
        HumanMessage(content=f"""Question: {state['question']}

Advisor Responses:
{advisor_outputs_text}

Please provide your synthesis following the structure in your system prompt.

IMPORTANT: Your response should include two parts:
1. Your summary (executive summary, convergences, divergences, next actions)
2. A list of disagreements (one per line, starting with "- ")

Format your response as:
=== SUMMARY ===
[your summary here]

=== DISSENT ===
- [disagreement 1]
- [disagreement 2]
- [disagreement 3]
...""")
    ]
    
    # Invoke the LLM
    response = llm.invoke(messages)
    response_text = response.content
    
    # Parse the response to extract summary and dissent
    summary = ""
    dissent = []
    
    if "=== SUMMARY ===" in response_text and "=== DISSENT ===" in response_text:
        # Split the response
        parts = response_text.split("=== DISSENT ===")
        summary_part = parts[0].replace("=== SUMMARY ===", "").strip()
        dissent_part = parts[1].strip() if len(parts) > 1 else ""
        summary = summary_part
        
        # Parse dissent lines
        for line in dissent_part.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                dissent.append(line[2:].strip())
            elif line and not line.startswith("-"):
                dissent.append(line)
    else:
        # Fallback: treat entire response as summary, no dissent
        summary = response_text
    
    # Update state
    state["summary"] = summary
    state["dissent"] = dissent
    
    # Add to transcript if verbose logging is enabled
    if state.get("transcript") is not None:
        state["transcript"].append({
            "node": "summarizer",
            "summary": summary,
            "dissent": dissent
        })
    
    return state


def create_brain_trust_graph():
    """Create and compile the brain trust LangGraph.
    
    The graph structure:
    - All advisor nodes run in parallel
    - All advisors connect to the summarizer node
    - Summarizer connects to END
    
    Returns:
        A compiled StateGraph ready for invocation
    """
    # Create the state graph
    graph = StateGraph(BrainTrustState)
    
    # Add advisor nodes for all personas except Summarizer
    advisor_names = [
        name for name, persona in PERSONAS.items()
        if not persona.is_summarizer
    ]
    
    for advisor_name in advisor_names:
        graph.add_node(advisor_name, advisor_node(advisor_name))
    
    # Add the summarizer node
    graph.add_node("summarizer", summarizer_node)
    
    # Connect all advisors to the summarizer (parallel execution)
    for advisor_name in advisor_names:
        graph.add_edge(advisor_name, "summarizer")
    
    # Connect summarizer to END
    graph.add_edge("summarizer", END)
    
    # Set the entry point - we'll use the first advisor as entry,
    # but all advisors will run in parallel
    if advisor_names:
        graph.set_entry_point(advisor_names[0])
        # Connect entry to all other advisors for parallel execution
        for advisor_name in advisor_names[1:]:
            graph.add_edge(advisor_names[0], advisor_name)
    
    # Compile the graph
    return graph.compile()


def run_brain_trust(
    question: str,
    selected_personas: Optional[list[str]] = None,
    verbose: bool = False
) -> BrainTrustState:
    """Run the brain trust deliberation on a question.
    
    Args:
        question: The user's question or topic for deliberation
        selected_personas: Optional list of persona names to use.
                          If None, all non-summarizer personas are used.
        verbose: If True, includes a transcript of all node executions
        
    Returns:
        The final state with advisor_outputs, summary, and dissent populated
    """
    # Initialize state
    initial_state: BrainTrustState = {
        "question": question,
        "selected_personas": selected_personas,
        "advisor_outputs": {},
        "scratchpads": {},
        "summary": "",
        "dissent": [],
        "transcript": [] if verbose else None
    }
    
    # Create and invoke the graph
    graph = create_brain_trust_graph()
    final_state = graph.invoke(initial_state)
    
    return final_state
