#!/usr/bin/env python
"""Simple chat application using message-driven architecture."""

import asyncio
import os
import sys

from dotenv import load_dotenv

from examples.chat.flow import create_chat_flow
from examples.chat.messages import ChatCompleted, StartChat
from tests.conftest import create_run_id


async def main() -> None:
    """Run the chat application."""
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    print("Welcome to ClearFlow Chat!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("-" * 50)

    # Create the chat flow
    flow = create_chat_flow()

    # Start the chat
    start_command = StartChat(
        triggered_by_id=None,
        run_id=create_run_id(),
        system_prompt="You are a helpful, friendly assistant.",
    )

    try:
        # Run the flow - it will handle the entire conversation
        result = await flow.process(start_command)
        # Check if it's ChatCompleted (flow can also terminate with UserMessageReceived)
        if isinstance(result, ChatCompleted):
            print(f"\nChat ended: {result.reason}")
        else:
            # UserMessageReceived - shouldn't happen in normal flow but handle gracefully
            print("\nChat ended unexpectedly")

    except (KeyboardInterrupt, EOFError):
        print("\nChat interrupted by user")
    except (OSError, RuntimeError) as e:
        print(f"\nError occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
