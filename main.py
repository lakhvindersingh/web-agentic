"""Main entry point for the agent."""
import sys
from agentic import Config, create_agent, run_agent


def main():
    """Main function to run the agent."""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create agent
    print("Initializing agent...")
    agent = create_agent()
    print("Agent ready!")
    print()
    
    # Interactive loop
    print("Agent is ready. Type your questions or 'quit' to exit.")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\nAgent: ", end="", flush=True)
            response = run_agent(agent, user_input, max_steps=10)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

