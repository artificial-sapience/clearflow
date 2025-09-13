#!/usr/bin/env python
"""Main entry point for the message-driven chat application."""

import asyncio
import os
import sys

from dotenv import load_dotenv

from examples.chat_message_driven.chat_flow import create_message_driven_chat_flow
from examples.chat_message_driven.messages import UserInputCommand
from tests.conftest_message import create_flow_id


async def main() -> None:
    """Run the message-driven chat application."""
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    # Welcome message
    print("Welcome to ClearFlow Message-Driven Chat!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("-" * 50)

    try:
        # Create message-driven flow
        flow = create_message_driven_chat_flow()

        # Start with initial command
        initial_command = UserInputCommand(
            triggered_by_id=None,
            flow_id=create_flow_id(),
            messages=(),
        )

        # Process the flow until completion
        result = await flow.process(initial_command)

        print(f"\\nConversation completed with {len(result.final_messages)} messages.")

    except (KeyboardInterrupt, EOFError):
        # User interrupted - exit gracefully
        print("\\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
