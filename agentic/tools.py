"""Tool definitions for the agent."""
from langchain_core.tools import tool
import math


@tool
def search(query: str) -> str:
    """
    Search for information using a web search query.
    
    Args:
        query: The search query string
        
    Returns:
        Search results as a string
    """
    # Note: For production, integrate with a real search API (Serper, Tavily, etc.)
    # This is a placeholder that returns mock results
    return f"Search results for '{query}': [Mock result 1: Information about {query}, Mock result 2: Related content]"


@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    
    Args:
        expression: A mathematical expression (e.g., "2 + 2", "sqrt(16)")
        
    Returns:
        The result of the calculation as a string
    """
    # Safe evaluation using only math module functions
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("__")
    }
    
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool
def read_file(filepath: str) -> str:
    """
    Read the contents of a text file.
    
    Args:
        filepath: Path to the file to read (relative to current working directory)
        
    Returns:
        The file contents as a string
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found."
    except PermissionError:
        return f"Error: Permission denied reading '{filepath}'."
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"


# Export all tools as a list
TOOLS = [search, calculate, read_file]

