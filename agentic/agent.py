"""Agent implementation using LangGraph with explicit state and control loop."""
from typing import TypedDict, Literal, Annotated
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from agentic.config import Config
from agentic.tools import TOOLS


# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.

Available tools:
- search(query): Search for information on the web
- calculate(expression): Evaluate mathematical expressions
- read_file(filepath): Read contents of text files

Your workflow:
1. Understand the user's request
2. Decide which tool(s) to use, if any
3. Execute tools with proper arguments
4. Analyze results and provide a final answer
5. When you have a complete answer, use the END state

Always use structured tool calls - never make up tool outputs.
If you need to use multiple tools, do so sequentially.
When you have finished helping the user, provide your final answer and stop."""


class AgentState(TypedDict):
    """Agent state definition."""
    messages: Annotated[list, add_messages]
    step_count: int
    max_steps: int


def create_llm() -> BaseChatModel:
    """Create and return the appropriate LLM based on configuration."""
    llm_type = Config.LLM_TYPE
    model_name = Config.get_model_name()
    
    if llm_type == "gpt" or llm_type == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            api_key=Config.OPENAI_API_KEY,
            temperature=0,
        )
    elif llm_type == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0,
            )
        except ImportError:
            raise ImportError(
                "langchain-google-genai package is required for Gemini. "
                "Install it with: pip install langchain-google-genai"
            )
    else:
        raise ValueError(f"Unsupported LLM_TYPE: {llm_type}")


def create_agent():
    """Create and return a configured LangGraph agent."""
    
    # Initialize LLM with tools
    llm = create_llm()
    llm_with_tools = llm.bind_tools(TOOLS)
    
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
        
        # Execute each tool call
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Find the tool
                tool_map = {tool.name: tool for tool in TOOLS}
                if tool_name in tool_map:
                    result = tool_map[tool_name].invoke(tool_args)
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
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
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

