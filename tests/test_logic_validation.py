"""
Test module for pure logic validation without database dependencies.
These tests verify business logic, validation functions, and utility methods.
"""
import pytest
from app.dal.assignments_dal import _validate_submit_status, _validate_category_type, _colour_from


@pytest.mark.ui
def test_submit_status_validation():
    """Test assignment submit status validation logic."""
    # Valid statuses should not raise
    _validate_submit_status("Not Started")
    _validate_submit_status("In Progress")
    _validate_submit_status("Done")
    _validate_submit_status("Skipped")
    
    # Invalid statuses should raise ValueError
    with pytest.raises(ValueError, match="Invalid status"):
        _validate_submit_status("Invalid Status")
    
    with pytest.raises(ValueError, match="Invalid status"):
        _validate_submit_status("completed")  # wrong case


@pytest.mark.ui
def test_category_type_validation():
    """Test assignment category and type validation logic."""
    # Valid combinations should not raise
    _validate_category_type("Formative", "Quiz")
    _validate_category_type("Formative", "Written assignment")
    _validate_category_type("Formative", "Practical")
    _validate_category_type("Exam", "Quiz")
    _validate_category_type("Exam", "Written exam")
    _validate_category_type("Exam", "Take-Home exam")
    
    # Invalid category should raise
    with pytest.raises(ValueError, match="Invalid category"):
        _validate_category_type("Invalid", "Quiz")
    
    # Invalid type for category should raise
    with pytest.raises(ValueError, match="not valid for category"):
        _validate_category_type("Formative", "Written exam")  # exam type for formative
    
    with pytest.raises(ValueError, match="not valid for category"):
        _validate_category_type("Exam", "Written assignment")  # formative type for exam


@pytest.mark.ui
def test_colour_assignment_logic():
    """Test assignment color coding logic."""
    # Not submitted should be yellow
    assert _colour_from("Not Started", None) == "Yellow"
    assert _colour_from("In Progress", None) == "Yellow"
    assert _colour_from("Skipped", None) == "Yellow"
    
    # Done but no score should be orange
    assert _colour_from("Done", None) == "Orange"
    
    # Done with passing score should be green
    assert _colour_from("Done", 50.0) == "Green"
    assert _colour_from("Done", 75.5) == "Green"
    assert _colour_from("Done", 100.0) == "Green"
    
    # Done with failing score should be red
    assert _colour_from("Done", 49.9) == "Red"
    assert _colour_from("Done", 0.0) == "Red"
    assert _colour_from("Done", 25.0) == "Red"