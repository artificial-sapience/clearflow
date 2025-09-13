#!/usr/bin/env python
"""Simple chat application using message-driven architecture."""

import asyncio
import os
import sys

from dotenv import load_dotenv

from examples.chat_message_driven.chat_flow import create_chat_flow
from examples.chat_message_driven.messages import StartChat
from tests.conftest_message import create_flow_id


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
        run_id=create_flow_id(),
        system_prompt="You are a helpful, friendly assistant.",
    )

    try:
        # Run the flow - it will handle the entire conversation
        result = await flow.process(start_command)
        print(f"\nChat ended: {result.reason}")

    except (KeyboardInterrupt, EOFError):
        print("\nChat interrupted by user")
    except (OSError, RuntimeError) as e:
        print(f"\nError occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
