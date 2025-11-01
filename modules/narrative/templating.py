#!/usr/bin/env python3
"""
Templating system for narrative content personalization
Handles variable interpolation and conditional text based on user state
"""

import re
from typing import Any, Dict, Optional
from database.connection import get_db
from database.models import UserNarrativeProgress
from .flags import get_narrative_flag


class NarrativeTemplating:
    """Handles template interpolation for narrative content"""
    
    def __init__(self):
        self.variable_pattern = re.compile(r'{{\s*(.*?)\s*}}')
        self.conditional_pattern = re.compile(r'{{\s*(.*?)\s*\?\s*(.*?)\s*:\s*(.*?)\s*}}')
    
    def interpolate_text(self, text: str, user_id: int) -> str:
        """
        Interpolate variables and conditionals in narrative text
        
        Args:
            text: The template text with variables
            user_id: User ID for context
            
        Returns:
            Interpolated text with variables replaced
        """
        if not text:
            return text
        
        # First handle conditional expressions
        text = self._process_conditionals(text, user_id)
        
        # Then handle simple variable replacements
        text = self._process_variables(text, user_id)
        
        return text
    
    def _process_conditionals(self, text: str, user_id: int) -> str:
        """Process conditional expressions in template"""
        def replace_conditional(match):
            condition = match.group(1).strip()
            true_value = match.group(2).strip()
            false_value = match.group(3).strip()
            
            if self._evaluate_condition(condition, user_id):
                return true_value
            else:
                return false_value
        
        return self.conditional_pattern.sub(replace_conditional, text)
    
    def _process_variables(self, text: str, user_id: int) -> str:
        """Process simple variable replacements"""
        def replace_variable(match):
            variable_expr = match.group(1).strip()
            return self._get_variable_value(variable_expr, user_id)
        
        return self.variable_pattern.sub(replace_variable, text)
    
    def _evaluate_condition(self, condition: str, user_id: int) -> bool:
        """Evaluate a conditional expression"""
        # Handle comparison operators
        operators = ['>=', '<=', '>', '<', '==', '!=']
        
        for op in operators:
            if op in condition:
                left, right = condition.split(op, 1)
                left = left.strip()
                right = right.strip()
                
                left_value = self._get_variable_value(left, user_id)
                right_value = self._get_variable_value(right, user_id)
                
                # Try to convert to numbers if possible
                try:
                    left_num = float(left_value) if left_value else 0
                    right_num = float(right_value) if right_value else 0
                    
                    if op == '>=':
                        return left_num >= right_num
                    elif op == '<=':
                        return left_num <= right_num
                    elif op == '>':
                        return left_num > right_num
                    elif op == '<':
                        return left_num < right_num
                    elif op == '==':
                        return left_num == right_num
                    elif op == '!=':
                        return left_num != right_num
                except (ValueError, TypeError):
                    # Fall back to string comparison
                    if op == '==':
                        return str(left_value) == str(right_value)
                    elif op == '!=':
                        return str(left_value) != str(right_value)
        
        # Handle boolean flags
        flag_value = self._get_variable_value(condition, user_id)
        return bool(flag_value)
    
    def _get_variable_value(self, variable_expr: str, user_id: int) -> str:
        """Get the value of a variable expression"""
        # Handle narrative flags
        if variable_expr.startswith('flag:'):
            flag_name = variable_expr[5:].strip()
            flag_value = get_narrative_flag(user_id, flag_name)
            return str(flag_value) if flag_value is not None else ""
        
        # Handle user state variables
        if variable_expr.startswith('user:'):
            field_name = variable_expr[5:].strip()
            return self._get_user_field(user_id, field_name)
        
        # Default: treat as narrative flag
        flag_value = get_narrative_flag(user_id, variable_expr)
        return str(flag_value) if flag_value is not None else ""
    
    def _get_user_field(self, user_id: int, field_name: str) -> str:
        """Get user-specific field value"""
        db = next(get_db())
        try:
            user_progress = db.query(UserNarrativeProgress).filter(
                UserNarrativeProgress.user_id == user_id
            ).first()
            
            if not user_progress:
                return ""
            
            # Map field names to actual attributes
            field_mapping = {
                'besitos': lambda u: str(u.besitos) if hasattr(u, 'besitos') else "0",
                'level': lambda u: str(u.current_level) if hasattr(u, 'current_level') else "1",
                'fragments_completed': lambda u: str(len(u.completed_fragments)) if hasattr(u, 'completed_fragments') else "0",
            }
            
            if field_name in field_mapping:
                return field_mapping[field_name](user_progress)
            
            return ""
        finally:
            db.close()


# Global instance
templating = NarrativeTemplating()


def interpolate_narrative_text(text: str, user_id: int) -> str:
    """
    Convenience function to interpolate narrative text
    
    Args:
        text: Template text with variables
        user_id: User ID for context
        
    Returns:
        Interpolated text
    """
    return templating.interpolate_text(text, user_id)


# Example usage and tests
if __name__ == "__main__":
    # Test the templating system
    test_cases = [
        ("Hello {{flag:trusted_lucien ? 'friend' : 'stranger'}}", 1),
        ("Your trust level: {{user:besitos}}", 1),
        ("{{trust_level_diana > 5 ? 'Dear friend' : 'Visitor'}}", 1),
        ("You have completed {{user:fragments_completed}} fragments", 1),
    ]
    
    for template, user_id in test_cases:
        result = interpolate_narrative_text(template, user_id)
        print(f"Template: {template}")
        print(f"Result: {result}")
        print("---")