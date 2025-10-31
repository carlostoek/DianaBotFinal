"""
Configuration validators for the Configuration Manager

This module provides validation functions for configuration data
against JSON schemas and custom business rules.
"""

import json
import logging
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)


def validate_config_data(schema: Dict[str, Any], data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate configuration data against a JSON schema
    
    Args:
        schema: JSON schema to validate against
        data: Configuration data to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    try:
        # Basic type validation
        if not isinstance(data, dict):
            errors.append("Configuration data must be a dictionary")
            return False, errors
        
        # Check required fields
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Required field '{field}' is missing")
        
        # Validate field types and constraints
        properties = schema.get('properties', {})
        for field_name, field_value in data.items():
            if field_name in properties:
                field_schema = properties[field_name]
                field_errors = _validate_field(field_name, field_value, field_schema)
                errors.extend(field_errors)
        
        # Validate custom business rules
        custom_errors = _validate_custom_rules(schema, data)
        errors.extend(custom_errors)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        logger.error(f"Error during configuration validation: {e}")
        return False, [f"Validation error: {str(e)}"]


def _validate_field(field_name: str, field_value: Any, field_schema: Dict[str, Any]) -> List[str]:
    """Validate a single field against its schema"""
    errors = []
    
    # Type validation
    expected_type = field_schema.get('type')
    if expected_type:
        if expected_type == 'string':
            if not isinstance(field_value, str):
                errors.append(f"Field '{field_name}' must be a string")
            else:
                # String length validation
                min_length = field_schema.get('minLength')
                max_length = field_schema.get('maxLength')
                if min_length and len(field_value) < min_length:
                    errors.append(f"Field '{field_name}' must be at least {min_length} characters")
                if max_length and len(field_value) > max_length:
                    errors.append(f"Field '{field_name}' must be at most {max_length} characters")
        
        elif expected_type == 'integer':
            if not isinstance(field_value, int):
                errors.append(f"Field '{field_name}' must be an integer")
            else:
                # Integer range validation
                minimum = field_schema.get('minimum')
                maximum = field_schema.get('maximum')
                if minimum is not None and field_value < minimum:
                    errors.append(f"Field '{field_name}' must be at least {minimum}")
                if maximum is not None and field_value > maximum:
                    errors.append(f"Field '{field_name}' must be at most {maximum}")
        
        elif expected_type == 'boolean':
            if not isinstance(field_value, bool):
                errors.append(f"Field '{field_name}' must be a boolean")
        
        elif expected_type == 'array':
            if not isinstance(field_value, list):
                errors.append(f"Field '{field_name}' must be an array")
            else:
                # Array length validation
                min_items = field_schema.get('minItems')
                max_items = field_schema.get('maxItems')
                if min_items and len(field_value) < min_items:
                    errors.append(f"Field '{field_name}' must have at least {min_items} items")
                if max_items and len(field_value) > max_items:
                    errors.append(f"Field '{field_name}' must have at most {max_items} items")
                
                # Item validation
                item_schema = field_schema.get('items')
                if item_schema:
                    for i, item in enumerate(field_value):
                        item_errors = _validate_field(f"{field_name}[{i}]", item, item_schema)
                        errors.extend(item_errors)
        
        elif expected_type == 'object':
            if not isinstance(field_value, dict):
                errors.append(f"Field '{field_name}' must be an object")
            else:
                # Object property validation
                properties = field_schema.get('properties', {})
                for prop_name, prop_value in field_value.items():
                    if prop_name in properties:
                        prop_errors = _validate_field(
                            f"{field_name}.{prop_name}", prop_value, properties[prop_name]
                        )
                        errors.extend(prop_errors)
    
    # Enum validation
    enum_values = field_schema.get('enum')
    if enum_values and field_value not in enum_values:
        errors.append(f"Field '{field_name}' must be one of: {enum_values}")
    
    return errors


def _validate_custom_rules(schema: Dict[str, Any], data: Dict[str, Any]) -> List[str]:
    """Validate custom business rules defined in the schema"""
    errors = []
    
    # Check for validation rules in the schema
    validation_rules = schema.get('validation_rules', [])
    
    for rule in validation_rules:
        rule_type = rule.get('type')
        condition = rule.get('condition')
        error_message = rule.get('error_message')
        
        if rule_type == 'dependency':
            # Check if field A requires field B
            field_a = rule.get('field_a')
            field_b = rule.get('field_b')
            if field_a in data and field_b not in data:
                errors.append(f"Field '{field_a}' requires field '{field_b}' to be set")
        
        elif rule_type == 'exclusive':
            # Check that only one of multiple fields is set
            fields = rule.get('fields', [])
            set_fields = [f for f in fields if f in data]
            if len(set_fields) > 1:
                errors.append(f"Only one of {fields} can be set")
        
        elif rule_type == 'range_balance':
            # Check balance between numeric fields
            field_a = rule.get('field_a')
            field_b = rule.get('field_b')
            min_ratio = rule.get('min_ratio')
            max_ratio = rule.get('max_ratio')
            
            if field_a in data and field_b in data:
                if data[field_b] > 0:  # Avoid division by zero
                    ratio = data[field_a] / data[field_b]
                    if min_ratio and ratio < min_ratio:
                        errors.append(f"Ratio between {field_a} and {field_b} is too low")
                    if max_ratio and ratio > max_ratio:
                        errors.append(f"Ratio between {field_a} and {field_b} is too high")
    
    return errors


def validate_references_exist(
    data: Dict[str, Any], 
    reference_checkers: Dict[str, callable]
) -> List[str]:
    """
    Validate that referenced entities (items, achievements, etc.) exist
    
    Args:
        data: Configuration data to validate
        reference_checkers: Dictionary mapping field names to validation functions
        
    Returns:
        List of error messages
    """
    errors = []
    
    for field_name, checker_func in reference_checkers.items():
        if field_name in data:
            field_value = data[field_name]
            
            if isinstance(field_value, list):
                for item in field_value:
                    if not checker_func(item):
                        errors.append(f"Referenced {field_name} '{item}' does not exist")
            elif isinstance(field_value, str):
                if not checker_func(field_value):
                    errors.append(f"Referenced {field_name} '{field_value}' does not exist")
    
    return errors


def validate_narrative_flow(fragments: List[Dict[str, Any]]) -> List[str]:
    """
    Validate narrative flow for cycles and unreachable fragments
    
    Args:
        fragments: List of narrative fragments with decisions
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if not fragments:
        errors.append("Narrative must have at least one fragment")
        return errors
    
    # Build graph of fragment connections
    fragment_keys = {fragment.get('fragment_key') for fragment in fragments}
    connections = {}
    
    for fragment in fragments:
        fragment_key = fragment.get('fragment_key')
        decisions = fragment.get('decisions', [])
        
        if not fragment_key:
            errors.append("Fragment missing fragment_key")
            continue
        
        connections[fragment_key] = []
        
        for decision in decisions:
            next_fragment = decision.get('next_fragment')
            if next_fragment:
                connections[fragment_key].append(next_fragment)
                
                # Check if next fragment exists
                if next_fragment not in fragment_keys:
                    errors.append(f"Decision in fragment '{fragment_key}' references non-existent fragment '{next_fragment}'")
    
    # Check for cycles using DFS
    visited = set()
    recursion_stack = set()
    
    def has_cycle(fragment_key):
        if fragment_key in recursion_stack:
            return True
        if fragment_key in visited:
            return False
            
        visited.add(fragment_key)
        recursion_stack.add(fragment_key)
        
        for neighbor in connections.get(fragment_key, []):
            if has_cycle(neighbor):
                return True
                
        recursion_stack.remove(fragment_key)
        return False
    
    for fragment_key in fragment_keys:
        if fragment_key not in visited:
            if has_cycle(fragment_key):
                errors.append(f"Cycle detected in narrative flow starting from fragment '{fragment_key}'")
    
    return errors