#!/usr/bin/env python3
"""Test script for exemplar loader module.

This script verifies that the exemplar loading and formatting
functions work correctly.
"""

import sys
import os
import json
import tempfile
from pathlib import Path

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

def test_import_exemplars():
    """Test that exemplars module can be imported."""
    try:
        import src.exemplars as exemplars
        assert exemplars is not None, "exemplars module is None"
        assert hasattr(exemplars, 'Exemplar'), "Exemplar class not found"
        assert hasattr(exemplars, 'load_exemplars_for_persona'), "load_exemplars_for_persona function not found"
        assert hasattr(exemplars, 'format_exemplars_for_prompt'), "format_exemplars_for_prompt function not found"
        assert hasattr(exemplars, 'get_exemplars_prompt_block'), "get_exemplars_prompt_block function not found"
    except ImportError as e:
        raise AssertionError(f"Failed to import exemplars module: {e}")


# ============================================================================
# EXEMPLAR CLASS TESTS
# ============================================================================

def test_exemplar_creation():
    """Test that Exemplar objects can be created with valid data."""
    from src.exemplars import Exemplar
    
    exemplar = Exemplar(
        name="Test Person",
        track_record="Test track record",
        constraints="Test constraints",
        notable_actions=["Action 1", "Action 2"],
        public_refs=["https://example.com"]
    )
    
    assert exemplar.name == "Test Person", "Name not set correctly"
    assert exemplar.track_record == "Test track record", "Track record not set correctly"
    assert exemplar.constraints == "Test constraints", "Constraints not set correctly"
    assert len(exemplar.notable_actions) == 2, "Notable actions not set correctly"
    assert len(exemplar.public_refs) == 1, "Public refs not set correctly"


def test_exemplar_format_for_prompt():
    """Test that Exemplar.format_for_prompt() returns correct format."""
    from src.exemplars import Exemplar
    
    exemplar = Exemplar(
        name="Jane Doe",
        track_record="CEO of Acme Corp",
        constraints="Budget constraints, 6-month timeline",
        notable_actions=["Pivoted to SaaS model", "Cut costs by 30%"],
        public_refs=["https://linkedin.com/in/janedoe"]
    )
    
    formatted = exemplar.format_for_prompt()
    
    assert "Jane Doe" in formatted, "Name not in formatted output"
    assert "CEO of Acme Corp" in formatted, "Track record not in formatted output"
    assert "Budget constraints" in formatted, "Constraints not in formatted output"
    assert "Pivoted to SaaS model" in formatted, "Action not in formatted output"
    assert "https://linkedin.com/in/janedoe" in formatted, "Public ref not in formatted output"


def test_exemplar_format_empty_refs():
    """Test that Exemplar.format_for_prompt() handles empty public refs."""
    from src.exemplars import Exemplar
    
    exemplar = Exemplar(
        name="Test Person",
        track_record="Test track record",
        constraints="Test constraints",
        notable_actions=["Action 1"],
        public_refs=[]
    )
    
    formatted = exemplar.format_for_prompt()
    
    assert "No public references" in formatted, "Should handle empty public refs"


# ============================================================================
# LOADER TESTS
# ============================================================================

def test_load_exemplars_nonexistent_file():
    """Test that load_exemplars_for_persona returns empty list for nonexistent file."""
    from src.exemplars import load_exemplars_for_persona
    
    # Use a temporary directory that doesn't have the file
    with tempfile.TemporaryDirectory() as temp_dir:
        exemplars = load_exemplars_for_persona("nonexistent_persona", temp_dir)
        assert exemplars == [], "Should return empty list for nonexistent file"


def test_load_exemplars_valid_json():
    """Test that load_exemplars_for_persona loads valid JSON correctly."""
    from src.exemplars import load_exemplars_for_persona, Exemplar
    
    # Create a temporary exemplar file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        exemplar_file = temp_path / "test_persona.json"
        
        test_data = {
            "persona": "test_persona",
            "exemplars": [
                {
                    "name": "Test Person 1",
                    "track_record": "Track record 1",
                    "constraints": "Constraints 1",
                    "notable_actions": ["Action 1", "Action 2"],
                    "public_refs": ["https://example.com/1"]
                },
                {
                    "name": "Test Person 2",
                    "track_record": "Track record 2",
                    "constraints": "Constraints 2",
                    "notable_actions": ["Action 3"],
                    "public_refs": ["https://example.com/2"]
                }
            ]
        }
        
        with open(exemplar_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load and verify
        exemplars = load_exemplars_for_persona("test_persona", temp_dir)
        
        assert len(exemplars) == 2, f"Expected 2 exemplars, got {len(exemplars)}"
        assert all(isinstance(e, Exemplar) for e in exemplars), "All items should be Exemplar instances"
        assert exemplars[0].name == "Test Person 1", "First exemplar name incorrect"
        assert exemplars[1].name == "Test Person 2", "Second exemplar name incorrect"


def test_load_exemplars_malformed_json():
    """Test that load_exemplars_for_persona raises ValueError for malformed JSON."""
    from src.exemplars import load_exemplars_for_persona
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        exemplar_file = temp_path / "test_persona.json"
        
        # Write invalid JSON
        with open(exemplar_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Should raise ValueError
        try:
            load_exemplars_for_persona("test_persona", temp_dir)
            raise AssertionError("Should have raised ValueError for malformed JSON")
        except ValueError as e:
            assert "Malformed JSON" in str(e), f"Error message should mention malformed JSON: {e}"


def test_load_exemplars_missing_field():
    """Test that load_exemplars_for_persona raises ValueError for missing required fields."""
    from src.exemplars import load_exemplars_for_persona
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        exemplar_file = temp_path / "test_persona.json"
        
        # Write JSON missing required field
        test_data = {
            "persona": "test_persona",
            "exemplars": [
                {
                    "name": "Test Person",
                    # Missing "track_record"
                    "constraints": "Constraints",
                    "notable_actions": ["Action 1"],
                    "public_refs": []
                }
            ]
        }
        
        with open(exemplar_file, 'w') as f:
            json.dump(test_data, f)
        
        # Should raise ValueError
        try:
            load_exemplars_for_persona("test_persona", temp_dir)
            raise AssertionError("Should have raised ValueError for missing field")
        except ValueError as e:
            assert "missing required field" in str(e), f"Error message should mention missing field: {e}"


def test_load_exemplars_no_exemplars_field():
    """Test that load_exemplars_for_persona returns empty list when no exemplars field."""
    from src.exemplars import load_exemplars_for_persona
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        exemplar_file = temp_path / "test_persona.json"
        
        # Write JSON without exemplars field
        test_data = {
            "persona": "test_persona"
        }
        
        with open(exemplar_file, 'w') as f:
            json.dump(test_data, f)
        
        exemplars = load_exemplars_for_persona("test_persona", temp_dir)
        assert exemplars == [], "Should return empty list when no exemplars field"


def test_load_exemplars_empty_exemplars_list():
    """Test that load_exemplars_for_persona returns empty list for empty exemplars."""
    from src.exemplars import load_exemplars_for_persona
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        exemplar_file = temp_path / "test_persona.json"
        
        # Write JSON with empty exemplars list
        test_data = {
            "persona": "test_persona",
            "exemplars": []
        }
        
        with open(exemplar_file, 'w') as f:
            json.dump(test_data, f)
        
        exemplars = load_exemplars_for_persona("test_persona", temp_dir)
        assert exemplars == [], "Should return empty list for empty exemplars"


# ============================================================================
# FORMATTING TESTS
# ============================================================================

def test_format_exemplars_for_prompt_empty():
    """Test that format_exemplars_for_prompt returns empty string for no exemplars."""
    from src.exemplars import format_exemplars_for_prompt
    
    formatted = format_exemplars_for_prompt([])
    assert formatted == "", "Should return empty string for no exemplars"


def test_format_exemplars_for_prompt_single():
    """Test that format_exemplars_for_prompt formats single exemplar correctly."""
    from src.exemplars import format_exemplars_for_prompt, Exemplar
    
    exemplar = Exemplar(
        name="Test Person",
        track_record="Test track record",
        constraints="Test constraints",
        notable_actions=["Action 1", "Action 2"],
        public_refs=["https://example.com"]
    )
    
    formatted = format_exemplars_for_prompt([exemplar])
    
    assert "=== EXEMPLARS ===" in formatted, "Should contain EXEMPLARS header"
    assert "=== END EXEMPLARS ===" in formatted, "Should contain EXEMPLARS footer"
    assert "Test Person" in formatted, "Should contain exemplar name"
    assert "Test track record" in formatted, "Should contain track record"
    assert "Action 1" in formatted, "Should contain action"


def test_format_exemplars_for_prompt_multiple():
    """Test that format_exemplars_for_prompt formats multiple exemplars correctly."""
    from src.exemplars import format_exemplars_for_prompt, Exemplar
    
    exemplars = [
        Exemplar(
            name="Person 1",
            track_record="Track 1",
            constraints="Constraints 1",
            notable_actions=["Action 1"],
            public_refs=[]
        ),
        Exemplar(
            name="Person 2",
            track_record="Track 2",
            constraints="Constraints 2",
            notable_actions=["Action 2"],
            public_refs=[]
        )
    ]
    
    formatted = format_exemplars_for_prompt(exemplars)
    
    assert "Person 1" in formatted, "Should contain first exemplar"
    assert "Person 2" in formatted, "Should contain second exemplar"
    assert formatted.count("Track Record:") == 2, "Should have track records for both"


def test_get_exemplars_prompt_block():
    """Test that get_exemplars_prompt_block combines loading and formatting."""
    from src.exemplars import get_exemplars_prompt_block
    
    # Test with nonexistent file (should return empty string)
    with tempfile.TemporaryDirectory() as temp_dir:
        formatted = get_exemplars_prompt_block("nonexistent", temp_dir)
        assert formatted == "", "Should return empty string for nonexistent persona"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_load_default_exemplars():
    """Test that default exemplars can be loaded from data/exemplars."""
    from src.exemplars import load_exemplars_for_persona
    
    # Test loading strategist exemplars (should exist)
    try:
        exemplars = load_exemplars_for_persona("strategist")
        # Should have at least one exemplar
        assert len(exemplars) > 0, "Should load at least one strategist exemplar"
        assert all(hasattr(e, 'name') for e in exemplars), "All exemplars should have name attribute"
    except FileNotFoundError:
        # This is okay if default exemplars don't exist yet
        print("  ⚠ Default exemplars not found (skipping integration test)")
    except Exception as e:
        raise AssertionError(f"Unexpected error loading default exemplars: {e}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests and report results."""
    print("=" * 70)
    print("Exemplar Loader Test Suite")
    print("=" * 70)
    
    # Import Tests
    print("\n[Import Tests]")
    run_test("Import exemplars module", test_import_exemplars)
    
    # Exemplar Class Tests
    print("\n[Exemplar Class Tests]")
    run_test("Exemplar creation", test_exemplar_creation)
    run_test("Exemplar format_for_prompt", test_exemplar_format_for_prompt)
    run_test("Exemplar format with empty refs", test_exemplar_format_empty_refs)
    
    # Loader Tests
    print("\n[Loader Tests]")
    run_test("Load nonexistent file", test_load_exemplars_nonexistent_file)
    run_test("Load valid JSON", test_load_exemplars_valid_json)
    run_test("Load malformed JSON", test_load_exemplars_malformed_json)
    run_test("Load missing field", test_load_exemplars_missing_field)
    run_test("Load no exemplars field", test_load_exemplars_no_exemplars_field)
    run_test("Load empty exemplars list", test_load_exemplars_empty_exemplars_list)
    
    # Formatting Tests
    print("\n[Formatting Tests]")
    run_test("Format empty exemplars", test_format_exemplars_for_prompt_empty)
    run_test("Format single exemplar", test_format_exemplars_for_prompt_single)
    run_test("Format multiple exemplars", test_format_exemplars_for_prompt_multiple)
    run_test("Get exemplars prompt block", test_get_exemplars_prompt_block)
    
    # Integration Tests
    print("\n[Integration Tests]")
    run_test("Load default exemplars", test_load_default_exemplars)
    
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
