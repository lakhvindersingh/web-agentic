"""LangGraph agent implementation."""
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END

from core.state import AgentState
from llm import create_llm
from tools.registry import get_all_tools
from prompts.system import get_system_prompt


def create_agent():
    """Create and return a configured LangGraph agent."""
    
    # Initialize LLM with tools
    llm = create_llm()
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Node: Decision point
    def should_continue(state: AgentState) -> Literal["call_tool", "end"]:
        """Decide whether to call tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if we've exceeded max steps
        if state.get("step_count", 0) >= state.get("max_steps", 10):
            return "end"
        
        # If the last message is an AI message with tool calls, execute them
        if isinstance(last_message, AIMessage):
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "call_tool"
            # If no tool calls, we have a final answer - end
            return "end"
        
        # If last message is a tool result, continue to generate
        # This shouldn't happen due to graph structure, but handle it
        return "end"
    
    # Node: Call tools
    def call_tool(state: AgentState) -> AgentState:
        """Execute tool calls and return results."""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_messages = []
        tools_map = {tool.name: tool for tool in tools}
        
        # Execute each tool call
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Find the tool
                if tool_name in tools_map:
                    result = tools_map[tool_name].invoke(tool_args)
                    tool_messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"],
                        )
                    )
        
        return {
            "messages": tool_messages,
            "step_count": state.get("step_count", 0) + 1,
        }
    
    # Node: Generate response
    def generate_response(state: AgentState) -> AgentState:
        """Generate AI response using LLM."""
        messages = state["messages"]
        
        # Prepend system prompt only if not already present
        has_system = any(isinstance(msg, SystemMessage) for msg in messages)
        if not has_system:
            # Generate system prompt with current tools
            system_prompt = get_system_prompt(tools=tools)
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = llm_with_tools.invoke(messages)
        
        return {
            "messages": [response],
            "step_count": state.get("step_count", 0),
        }
    
    # Add nodes
    workflow.add_node("generate", generate_response)
    workflow.add_node("tool", call_tool)
    
    # Set entry point
    workflow.set_entry_point("generate")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "generate",
        should_continue,
        {
            "call_tool": "tool",
            "end": END,
        },
    )
    
    # After tool execution, go back to generate
    workflow.add_edge("tool", "generate")
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def run_agent(agent, user_input: str, previous_messages: list = None, max_steps: int = 10) -> tuple[str, list]:
    """
    Run the agent with user input and return the final response and updated conversation.
    
    Args:
        agent: The compiled LangGraph agent
        user_input: User's query or request
        previous_messages: Previous conversation messages for context
        max_steps: Maximum number of tool-calling steps
        
    Returns:
        Tuple of (response_string, updated_messages_list)
    """
    # Start with previous messages or empty list
    messages = list(previous_messages) if previous_messages else []
    
    # Add the new user message
    messages.append(HumanMessage(content=user_input))
    
    initial_state = {
        "messages": messages,
        "step_count": 0,
        "max_steps": max_steps,
    }
    
    # Run the agent
    final_state = agent.invoke(initial_state)
    
    # Extract the final AI message (last AIMessage without tool calls)
    updated_messages = final_state["messages"]
    response = "No response generated."
    
    for message in reversed(updated_messages):
        if isinstance(message, AIMessage):
            # Return the first AI message that has content and no pending tool calls
            if message.content:
                response = message.content
                break
    
    # Return both the response and the full conversation history
    return response, updated_messages

