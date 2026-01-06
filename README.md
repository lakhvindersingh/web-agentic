# LangGraph Agent

A minimal, production-ready agent built with LangGraph and GPT that demonstrates explicit state management, structured tool invocation, and deterministic control flow.

> **Project Name Suggestions:**
> - `langgraph-agent` (recommended) - Descriptive, clear about tech stack
> - `structured-agent` - Emphasizes structured tool calling
> - `agentic-ai` - Generic but matches package name
> 
> The package itself is named `agentic` and can be used as-is or renamed to match your project name.

## Features

- **Explicit State Management**: Clear AgentState with messages, step count, and max steps
- **Control Loop**: Explicit decision points (generate → decide → tool → generate → end)
- **Structured Tools**: Three real tools with typed inputs:
  - `search(query)`: Web search capability
  - `calculate(expression)`: Mathematical expression evaluation
  - `read_file(filepath)`: File reading capability
- **Deterministic Stopping**: END state with max steps protection
- **Environment-Based Configuration**: All settings loaded from environment variables

## Project Structure

```
.
├── agentic/         # Main package
│   ├── __init__.py  # Package initialization
│   ├── agent.py     # LangGraph agent implementation
│   ├── config.py    # Configuration loading
│   └── tools.py     # Tool definitions
├── main.py          # Entry point with interactive loop
├── requirements.txt # Python dependencies
├── .gitignore       # Git ignore rules
└── README.md        # This file
```

## Setup

1. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   
   Create a `.env` file in the project root:
   ```bash
   # Windows
   echo OPENAI_API_KEY=your-api-key-here > .env
   echo MODEL=gpt-4o-mini >> .env
   
   # Linux/Mac
   cat > .env << EOF
   OPENAI_API_KEY=your-api-key-here
   MODEL=gpt-4o-mini
   EOF
   ```
   
   Replace `your-api-key-here` with your actual OpenAI API key.

4. **Run the agent:**
   ```bash
   python main.py
   ```

## Usage

Once running, interact with the agent:

```
You: What is 25 * 17?
Agent: 425

You: Read the file README.md
Agent: [File contents]

You: Search for information about LangGraph
Agent: [Search results]
```

Type `quit`, `exit`, or `q` to exit.

## How It Works

### State Definition
The agent uses a typed `AgentState` that tracks:
- `messages`: Conversation history
- `step_count`: Current iteration count
- `max_steps`: Maximum allowed steps (prevents infinite loops)

### Control Flow
```
Entry → Generate → Decision → Tool (if needed) → Generate → Decision → END
```

1. **Generate**: LLM generates a response, potentially with tool calls
2. **Decision**: Determines if tools need to be called or if we can end
3. **Tool**: Executes structured tool invocations
4. **Generate**: Processes tool results and generates final response
5. **END**: Deterministic stopping point

### Tool Invocation
All tools use structured invocation with typed parameters:
- No free-text tool calls
- Type-safe arguments
- Error handling for invalid inputs

### Stopping Conditions
The agent stops when:
- No tool calls are needed and a response is generated
- Maximum step count is reached
- Explicit END state is reached

## Configuration

All configuration is loaded from environment variables:

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `MODEL` (optional): Model to use (default: `gpt-4o-mini`)

## Extending the Agent

### Adding New Tools

1. Define the tool in `agentic/tools.py`:
   ```python
   @tool
   def my_tool(param: str) -> str:
       """Tool description."""
       # Implementation
       return result
   ```

2. Add to `TOOLS` list in `agentic/tools.py`:
   ```python
   TOOLS = [search, calculate, read_file, my_tool]
   ```

### Modifying the Control Loop

Edit the `should_continue` function in `agentic/agent.py` to change decision logic.

## Production Considerations

- **Error Handling**: Tools include error handling for edge cases
- **Step Limits**: Max steps prevent infinite loops
- **Type Safety**: TypedDict for state, typed tool parameters
- **Modularity**: Clear separation of concerns
- **Configuration**: Environment-based config for easy deployment

## License

MIT

