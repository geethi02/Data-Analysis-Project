"""
Calculator Tool - Allows agents to perform calculations
"""
import math
import re
from typing import Dict, Any, Union


class CalculatorTool:
    """Tool for mathematical calculations"""
    
    # Safe functions available for calculations
    SAFE_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,
        'sqrt': math.sqrt,
        'log': math.log,
        'log10': math.log10,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'pi': math.pi,
        'e': math.e,
    }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression safely
        
        Args:
            expression: Mathematical expression string
            
        Returns:
            Dictionary with result or error
        """
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Remove any potentially dangerous characters
            if re.search(r'[a-zA-Z_][a-zA-Z_0-9]*\s*\(', expression):
                # Check if function calls are safe
                for match in re.finditer(r'([a-zA-Z_][a-zA-Z_0-9]*)\s*\(', expression):
                    func_name = match.group(1)
                    if func_name not in self.SAFE_FUNCTIONS:
                        return {
                            "success": False,
                            "error": f"Function '{func_name}' not allowed",
                            "expression": expression
                        }
            
            # Evaluate using safe namespace
            result = eval(expression, {"__builtins__": {}}, self.SAFE_FUNCTIONS)
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "result_type": type(result).__name__
            }
            
        except ZeroDivisionError:
            return {
                "success": False,
                "error": "Division by zero",
                "expression": expression
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    def calculate_multiple(self, expressions: list) -> list:
        """Calculate multiple expressions"""
        return [self.calculate(expr) for expr in expressions]

