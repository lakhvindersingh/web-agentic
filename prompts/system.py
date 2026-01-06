"""System prompt definitions."""


def get_system_prompt(tools=None) -> str:
    """
    Generate system prompt with current available tools.
    
    Args:
        tools: Optional list of tools to include in the prompt. If None, uses default.
    """
    if tools is None:
        # Default tool descriptions
        tool_descriptions = [
            "- search(query): Search for information on the web",
            "- calculate(expression): Evaluate mathematical expressions",
            "- read_file(filepath): Read contents of text files",
        ]
    else:
        tool_descriptions = []
        for tool in tools:
            tool_descriptions.append(f"- {tool.name}: {tool.description}")
    
    tools_text = "\n".join(tool_descriptions) if tool_descriptions else "No tools available."
    
    return f"""You are a helpful AI assistant with access to tools.

Available tools:
{tools_text}

Your workflow:
1. Understand the user's request
2. Decide which tool(s) to use, if any
3. Execute tools with proper arguments
4. Analyze results and provide a final answer
5. When you have a complete answer, use the END state

Always use structured tool calls - never make up tool outputs.
If you need to use multiple tools, do so sequentially.
When you have finished helping the user, provide your final answer and stop."""


# Default system prompt
SYSTEM_PROMPT = get_system_prompt()

