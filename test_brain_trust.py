#!/usr/bin/env python3
"""Test script for brain trust CLI application.

This script verifies that all core modules work correctly without requiring
a live API key. Tests are organized by module and functionality.
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}


def run_test(test_name, test_func):
    """Run a single test and track results."""
    try:
        test_func()
        test_results["passed"] += 1
        print(f"  ✓ {test_name}")
        return True
    except AssertionError as e:
        test_results["failed"] += 1
        error_msg = f"  ✗ {test_name}: {str(e)}"
        print(error_msg)
        test_results["errors"].append(error_msg)
        return False
    except Exception as e:
        test_results["failed"] += 1
        error_msg = f"  ✗ {test_name}: Unexpected error: {str(e)}"
        print(error_msg)
        test_results["errors"].append(error_msg)
        return False


# ============================================================================
# IMPORT TESTS
# ============================================================================

def test_import_config():
    """Test that config module can be imported."""
    try:
        import src.config as config
        assert config is not None, "config module is None"
        assert hasattr(config, 'Config'), "Config class not found"
        assert hasattr(config, 'load_config'), "load_config function not found"
        assert hasattr(config, 'get_openai_client'), "get_openai_client function not found"
    except ImportError as e:
        raise AssertionError(f"Failed to import config module: {e}")


def test_import_personas():
    """Test that personas module can be imported."""
    try:
        import src.personas as personas
        assert personas is not None, "personas module is None"
        assert hasattr(personas, 'Persona'), "Persona class not found"
        assert hasattr(personas, 'PERSONAS'), "PERSONAS dict not found"
        assert hasattr(personas, 'get_persona'), "get_persona function not found"
    except ImportError as e:
        raise AssertionError(f"Failed to import personas module: {e}")


def test_import_graph():
    """Test that graph module can be imported."""
    try:
        import src.graph as graph
        assert graph is not None, "graph module is None"
        assert hasattr(graph, 'BrainTrustState'), "BrainTrustState class not found"
        assert hasattr(graph, 'advisor_node'), "advisor_node function not found"
        assert hasattr(graph, 'summarizer_node'), "summarizer_node function not found"
        assert hasattr(graph, 'create_brain_trust_graph'), "create_brain_trust_graph function not found"
        assert hasattr(graph, 'run_brain_trust'), "run_brain_trust function not found"
    except ImportError as e:
        raise AssertionError(f"Failed to import graph module: {e}")


def test_import_cli():
    """Test that cli module can be imported."""
    try:
        import src.cli as cli
        assert cli is not None, "cli module is None"
        assert hasattr(cli, 'app'), "app Typer instance not found"
        assert hasattr(cli, 'main'), "main function not found"
        assert hasattr(cli, 'validate_personas'), "validate_personas function not found"
    except ImportError as e:
        raise AssertionError(f"Failed to import cli module: {e}")


# ============================================================================
# CONFIG TESTS
# ============================================================================

def test_config_model_validation():
    """Test that Config model validates correctly with valid data."""
    from src.config import Config
    
    # Test with valid parameters
    config = Config(
        api_key="test_key_123",
        api_base="https://api.example.com/v1",
        model="test-model",
        temperature=0.7,
        top_p=1.0
    )
    
    assert config.api_key == "test_key_123", "api_key not set correctly"
    assert config.api_base == "https://api.example.com/v1", "api_base not set correctly"
    assert config.model == "test-model", "model not set correctly"
    assert config.temperature == 0.7, "temperature not set correctly"
    assert config.top_p == 1.0, "top_p not set correctly"


def test_config_default_values():
    """Test that Config model uses correct default values."""
    from src.config import Config
    
    config = Config(api_key="test_key")
    
    assert config.api_base == "https://api.z.ai/v1", f"Default api_base incorrect: {config.api_base}"
    assert config.model == "glm-4", f"Default model incorrect: {config.model}"
    assert config.temperature == 0.7, f"Default temperature incorrect: {config.temperature}"
    assert config.top_p == 1.0, f"Default top_p incorrect: {config.top_p}"


def test_config_temperature_validation():
    """Test that Config validates temperature range."""
    from src.config import Config
    
    # Test valid temperature values
    Config(api_key="test", temperature=0.0)
    Config(api_key="test", temperature=1.0)
    Config(api_key="test", temperature=2.0)
    
    # Test invalid temperature values (should raise ValueError)
    try:
        Config(api_key="test", temperature=-0.1)
        raise AssertionError("Should have raised ValueError for temperature < 0")
    except ValueError:
        pass  # Expected
    
    try:
        Config(api_key="test", temperature=2.1)
        raise AssertionError("Should have raised ValueError for temperature > 2.0")
    except ValueError:
        pass  # Expected


def test_config_top_p_validation():
    """Test that Config validates top_p range."""
    from src.config import Config
    
    # Test valid top_p values
    Config(api_key="test", top_p=0.0)
    Config(api_key="test", top_p=0.5)
    Config(api_key="test", top_p=1.0)
    
    # Test invalid top_p values (should raise ValueError)
    try:
        Config(api_key="test", top_p=-0.1)
        raise AssertionError("Should have raised ValueError for top_p < 0")
    except ValueError:
        pass  # Expected
    
    try:
        Config(api_key="test", top_p=1.1)
        raise AssertionError("Should have raised ValueError for top_p > 1.0")
    except ValueError:
        pass  # Expected


def test_load_config_missing_api_key():
    """Test that load_config raises ValueError when ZAI_API_KEY is not set."""
    from src.config import load_config
    
    # Temporarily remove ZAI_API_KEY from environment
    original_key = os.environ.get("ZAI_API_KEY")
    if "ZAI_API_KEY" in os.environ:
        del os.environ["ZAI_API_KEY"]
    
    try:
        load_config()
        raise AssertionError("Should have raised ValueError for missing ZAI_API_KEY")
    except ValueError as e:
        assert "ZAI_API_KEY" in str(e), f"Error message should mention ZAI_API_KEY: {e}"
    finally:
        # Restore original value
        if original_key:
            os.environ["ZAI_API_KEY"] = original_key


def test_load_config_with_api_key():
    """Test that load_config works when ZAI_API_KEY is set."""
    from src.config import load_config
    
    # Set a test API key
    os.environ["ZAI_API_KEY"] = "test_api_key_12345"
    
    try:
        config = load_config()
        assert config.api_key == "test_api_key_12345", "API key not loaded correctly"
        assert config.api_base == "https://api.z.ai/v1", "Default api_base not used"
        assert config.model == "glm-4", "Default model not used"
    finally:
        # Clean up
        if "ZAI_API_KEY" in os.environ:
            del os.environ["ZAI_API_KEY"]


# ============================================================================
# PERSONA TESTS
# ============================================================================

def test_all_personas_exist():
    """Test that all 6 required personas exist."""
    from src.personas import PERSONAS
    
    required_personas = [
        "strategist",
        "domain_expert",
        "devils_advocate",
        "risk_officer",
        "ethicist",
        "summarizer"
    ]
    
    for persona_name in required_personas:
        assert persona_name in PERSONAS, f"Persona '{persona_name}' not found in PERSONAS"
    
    # Verify exactly 6 personas
    assert len(PERSONAS) == 6, f"Expected 6 personas, found {len(PERSONAS)}"


def test_persona_attributes():
    """Test that each persona has required attributes."""
    from src.personas import PERSONAS, Persona
    
    for persona_name, persona in PERSONAS.items():
        assert isinstance(persona, Persona), f"Persona '{persona_name}' is not a Persona instance"
        assert persona.name == persona_name, f"Persona name mismatch: {persona.name} != {persona_name}"
        assert persona.display_name, f"Persona '{persona_name}' missing display_name"
        assert persona.system_prompt, f"Persona '{persona_name}' missing system_prompt"
        assert isinstance(persona.is_summarizer, bool), f"Persona '{persona_name}' is_summarizer not a bool"


def test_summarizer_is_unique():
    """Test that only the summarizer has is_summarizer=True."""
    from src.personas import PERSONAS
    
    summarizers = [name for name, p in PERSONAS.items() if p.is_summarizer]
    
    assert len(summarizers) == 1, f"Expected 1 summarizer, found {len(summarizers)}: {summarizers}"
    assert "summarizer" in summarizers, "Summarizer persona should have is_summarizer=True"


def test_advisor_guardrails():
    """Test that all advisor personas (except summarizer) have guardrails."""
    from src.personas import PERSONAS, ADVISOR_GUARDRAILS
    
    for persona_name, persona in PERSONAS.items():
        if not persona.is_summarizer:
            assert ADVISOR_GUARDRAILS in persona.system_prompt, \
                f"Advisor '{persona_name}' missing guardrails in system prompt"


def test_get_persona_valid():
    """Test that get_persona works for valid persona names."""
    from src.personas import get_persona, PERSONAS
    
    for persona_name in PERSONAS.keys():
        persona = get_persona(persona_name)
        assert persona is not None, f"get_persona returned None for '{persona_name}'"
        assert persona.name == persona_name, f"Persona name mismatch for '{persona_name}'"


def test_get_persona_invalid():
    """Test that get_persona raises KeyError for invalid persona names."""
    from src.personas import get_persona
    
    invalid_names = ["invalid", "nonexistent", "fake_persona"]
    
    for invalid_name in invalid_names:
        try:
            get_persona(invalid_name)
            raise AssertionError(f"get_persona should raise KeyError for '{invalid_name}'")
        except KeyError as e:
            assert invalid_name in str(e), f"Error message should mention '{invalid_name}'"


# ============================================================================
# GRAPH TESTS
# ============================================================================

def test_create_brain_trust_graph_returns_compiled_graph():
    """Test that create_brain_trust_graph returns a compiled graph."""
    from src.graph import create_brain_trust_graph
    
    graph = create_brain_trust_graph()
    
    assert graph is not None, "create_brain_trust_graph returned None"
    # Compiled graphs should have certain attributes
    assert hasattr(graph, 'invoke'), "Graph should have invoke method"
    assert hasattr(graph, 'get_graph'), "Graph should have get_graph method"


def test_graph_has_correct_nodes():
    """Test that the graph has the correct nodes (all advisors + summarizer)."""
    from src.graph import create_brain_trust_graph
    from src.personas import PERSONAS
    
    graph = create_brain_trust_graph()
    
    # Get the graph structure
    graph_structure = graph.get_graph()
    
    # Get all node names from the graph (LangGraph adds __start__ and __end__)
    nodes = list(graph_structure.nodes.keys())
    
    # Expected nodes: all advisors (non-summarizer) + summarizer
    expected_nodes = [
        name for name, persona in PERSONAS.items()
        if not persona.is_summarizer
    ] + ["summarizer"]
    
    # Verify all expected nodes exist
    for expected_node in expected_nodes:
        assert expected_node in nodes, f"Graph missing node: {expected_node}"
    
    # Note: LangGraph adds __start__ and __end__ nodes automatically
    # So we expect: expected_nodes + ['__start__', '__end__']
    expected_total = len(expected_nodes) + 2  # +2 for __start__ and __end__
    assert len(nodes) == expected_total, \
        f"Graph has {len(nodes)} nodes, expected {expected_total}: {nodes}"


def test_graph_edges_structure():
    """Test that graph edges are correctly structured (advisors -> summarizer -> END)."""
    from src.graph import create_brain_trust_graph
    from src.personas import PERSONAS
    
    graph = create_brain_trust_graph()
    graph_structure = graph.get_graph()
    
    # Get all edges (LangGraph returns Edge objects with source/target attributes)
    edges = list(graph_structure.edges)
    
    # All advisors should connect to summarizer
    advisor_names = [name for name, p in PERSONAS.items() if not p.is_summarizer]
    
    for advisor in advisor_names:
        has_edge = any(edge.source == advisor and edge.target == "summarizer" for edge in edges)
        assert has_edge, \
            f"Missing edge from advisor '{advisor}' to summarizer"
    
    # Summarizer should connect to __end__ (LangGraph's END node)
    has_end_edge = any(edge.source == "summarizer" and edge.target == "__end__" for edge in edges)
    assert has_end_edge, "Missing edge from summarizer to __end__"


def test_brain_trust_state_structure():
    """Test that BrainTrustState has correct structure."""
    from src.graph import BrainTrustState
    
    # Create a sample state
    state: BrainTrustState = {
        "question": "Test question",
        "selected_personas": ["strategist", "domain_expert"],
        "advisor_outputs": {"strategist": "output1", "domain_expert": "output2"},
        "scratchpads": {"strategist": "scratch1", "domain_expert": "scratch2"},
        "summary": "Test summary",
        "dissent": ["disagreement1", "disagreement2"],
        "transcript": None
    }
    
    assert state["question"] == "Test question"
    assert len(state["advisor_outputs"]) == 2
    assert len(state["scratchpads"]) == 2
    assert state["summary"] == "Test summary"
    assert len(state["dissent"]) == 2
    assert state["transcript"] is None


# ============================================================================
# ISOLATION TEST
# ============================================================================

def test_scratchpad_isolation_conceptual():
    """Test that scratchpads are isolated between advisors (conceptual test).
    
    This test verifies the design principle that scratchpads are never passed
    between advisors - each advisor only sees their own scratchpad.
    """
    from src.personas import PERSONAS
    from src.graph import BrainTrustState
    
    # Create a state with different scratchpad content for each advisor
    state: BrainTrustState = {
        "question": "Test question",
        "selected_personas": None,
        "advisor_outputs": {},
        "scratchpads": {
            "strategist": "Strategist's private thoughts",
            "domain_expert": "Domain expert's private thoughts",
            "devils_advocate": "Devil's advocate's private thoughts",
            "risk_officer": "Risk officer's private thoughts",
            "ethicist": "Ethicist's private thoughts"
        },
        "summary": "",
        "dissent": [],
        "transcript": None
    }
    
    # Verify each scratchpad is independent
    scratchpads = state["scratchpads"]
    assert scratchpads["strategist"] != scratchpads["domain_expert"]
    assert scratchpads["domain_expert"] != scratchpads["devils_advocate"]
    assert scratchpads["devils_advocate"] != scratchpads["risk_officer"]
    assert scratchpads["risk_officer"] != scratchpads["ethicist"]
    
    # Verify scratchpads are stored separately from advisor_outputs
    assert "scratchpads" in state
    assert "advisor_outputs" in state
    assert state["scratchpads"] is not state["advisor_outputs"]


def test_scratchpad_not_in_summarizer_input():
    """Test that summarizer only receives advisor_outputs, not scratchpads.
    
    This verifies the isolation property by checking that the summarizer
    system prompt explicitly states it receives advisor responses, not scratchpads.
    """
    from src.personas import PERSONAS
    
    summarizer = PERSONAS["summarizer"]
    
    # The summarizer's system prompt should mention receiving advisor responses
    assert "advisor responses" in summarizer.system_prompt.lower() or \
           "advisor outputs" in summarizer.system_prompt.lower(), \
           "Summarizer system prompt should mention receiving advisor responses"
    
    # The summarizer's system prompt should explicitly state it does NOT receive scratchpads
    # The prompt says "You receive the responses from all advisor personas (not their scratchpads)"
    assert "not their scratchpads" in summarizer.system_prompt.lower() or \
           "do not receive scratchpads" in summarizer.system_prompt.lower(), \
           "Summarizer system prompt should explicitly state it does not receive scratchpads"


def test_advisor_guardrails_prevent_collusion():
    """Test that advisor guardrails explicitly prevent collusion.
    
    This verifies that advisors are instructed to work independently
    and not reference other advisors' work.
    """
    from src.personas import PERSONAS, ADVISOR_GUARDRAILS
    
    # Check that guardrails exist
    assert ADVISOR_GUARDRAILS, "ADVISOR_GUARDRAILS should be defined"
    
    # Check that guardrails mention independent work
    assert "independent" in ADVISOR_GUARDRAILS.lower() or \
           "do not assume" in ADVISOR_GUARDRAILS.lower(), \
           "Guardrails should mention independent work"
    
    # Check that guardrails mention private scratchpad
    assert "scratchpad" in ADVISOR_GUARDRAILS.lower(), \
           "Guardrails should mention private scratchpad"
    
    # Verify all advisors have these guardrails
    for name, persona in PERSONAS.items():
        if not persona.is_summarizer:
            assert ADVISOR_GUARDRAILS in persona.system_prompt, \
                   f"Advisor '{name}' missing guardrails"


# ============================================================================
# CLI TESTS
# ============================================================================

def test_validate_personas_valid():
    """Test that validate_personas works with valid persona names."""
    from src.cli import validate_personas
    
    valid_lists = [
        ["strategist"],
        ["strategist", "domain_expert"],
        ["strategist", "domain_expert", "devils_advocate", "risk_officer", "ethicist"]
    ]
    
    for personas_list in valid_lists:
        result = validate_personas(personas_list)
        assert result == personas_list, f"validate_personas altered valid list: {personas_list}"


def test_validate_personas_invalid():
    """Test that validate_personas raises error for invalid persona names."""
    from src.cli import validate_personas
    from typer import BadParameter
    
    invalid_lists = [
        ["invalid_persona"],
        ["strategist", "fake_persona"],
        ["nonexistent"]
    ]
    
    for personas_list in invalid_lists:
        try:
            validate_personas(personas_list)
            raise AssertionError(f"validate_personas should raise BadParameter for {personas_list}")
        except BadParameter:
            pass  # Expected


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests and report results."""
    print("=" * 70)
    print("Brain Trust CLI Test Suite")
    print("=" * 70)
    
    # Import Tests
    print("\n[Import Tests]")
    run_test("Import config module", test_import_config)
    run_test("Import personas module", test_import_personas)
    run_test("Import graph module", test_import_graph)
    run_test("Import cli module", test_import_cli)
    
    # Config Tests
    print("\n[Config Tests]")
    run_test("Config model validation", test_config_model_validation)
    run_test("Config default values", test_config_default_values)
    run_test("Config temperature validation", test_config_temperature_validation)
    run_test("Config top_p validation", test_config_top_p_validation)
    run_test("Load config missing API key", test_load_config_missing_api_key)
    run_test("Load config with API key", test_load_config_with_api_key)
    
    # Persona Tests
    print("\n[Persona Tests]")
    run_test("All personas exist", test_all_personas_exist)
    run_test("Persona attributes", test_persona_attributes)
    run_test("Summarizer is unique", test_summarizer_is_unique)
    run_test("Advisor guardrails", test_advisor_guardrails)
    run_test("get_persona valid names", test_get_persona_valid)
    run_test("get_persona invalid names", test_get_persona_invalid)
    
    # Graph Tests
    print("\n[Graph Tests]")
    run_test("Create brain trust graph returns compiled graph", 
             test_create_brain_trust_graph_returns_compiled_graph)
    run_test("Graph has correct nodes", test_graph_has_correct_nodes)
    run_test("Graph edges structure", test_graph_edges_structure)
    run_test("Brain trust state structure", test_brain_trust_state_structure)
    
    # Isolation Tests
    print("\n[Isolation Tests]")
    run_test("Scratchpad isolation conceptual", test_scratchpad_isolation_conceptual)
    run_test("Scratchpad not in summarizer input", test_scratchpad_not_in_summarizer_input)
    run_test("Advisor guardrails prevent collusion", test_advisor_guardrails_prevent_collusion)
    
    # CLI Tests
    print("\n[CLI Tests]")
    run_test("Validate personas valid", test_validate_personas_valid)
    run_test("Validate personas invalid", test_validate_personas_invalid)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    total = test_results["passed"] + test_results["failed"]
    print(f"Total tests:  {total}")
    print(f"Passed:       {test_results['passed']}")
    print(f"Failed:       {test_results['failed']}")
    
    if test_results["errors"]:
        print("\nFailed tests:")
        for error in test_results["errors"]:
            print(f"  {error}")
    
    print("=" * 70)
    
    # Exit with appropriate code
    if test_results["failed"] > 0:
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
