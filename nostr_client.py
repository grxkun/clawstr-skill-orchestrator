"""
Nostr Client for Clawstr Skill Indexing

Handles broadcasting of agent metadata and skill updates to Nostr relays.
Specifically designed for integration with the Clawstr ecosystem and Clawnch token launches.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from nostr.key import PrivateKey
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.filter import Filter, Filters
from nostr.subscription import Subscription

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NostrClient:
    """
    Nostr client for broadcasting agent metadata and skill updates.

    Handles:
    - Kind 0: Agent metadata (name, bio, website)
    - Kind 30023: Long-form content for skill publishing
    - Connection to wss://lightningrelay.com
    """

    def __init__(self):
        """Initialize Nostr client with private key and relay."""
        self.nsec = os.getenv('NOSTR_NSEC')
        self.relay_url = os.getenv('NOSTR_RELAY', 'wss://lightningrelay.com')
        self.agent_name = os.getenv('AGENT_NAME', 'MasterOrchestrator')

        if not self.nsec:
            raise ValueError("NOSTR_NSEC environment variable is required")

        # Initialize private key
        self.private_key = PrivateKey.from_nsec(self.nsec)
        self.public_key = self.private_key.public_key

        # Initialize relay manager
        self.relay_manager = RelayManager()
        self.relay_manager.add_relay(self.relay_url)

        logger.info(f"Initialized Nostr client for {self.agent_name}")

    def connect(self):
        """Connect to the Nostr relay."""
        self.relay_manager.open_connections()
        time.sleep(2)  # Allow connection to establish
        logger.info(f"Connected to relay: {self.relay_url}")

    def disconnect(self):
        """Disconnect from the relay."""
        self.relay_manager.close_connections()
        logger.info("Disconnected from relay")

    def broadcast_metadata(self):
        """
        Broadcast Kind 0 (Metadata) event for agent profile.

        Sets the agent's name, bio, and GitHub repo link.
        """
        metadata = {
            "name": self.agent_name,
            "about": "Autonomous Master Orchestrator for Clawstr ecosystem. Manages skill consolidation, versioning, and token launches.",
            "website": "https://github.com/grxkun/clawstr-skill-orchestrator"
        }

        event = Event(
            public_key=self.public_key.hex(),
            content=json.dumps(metadata),
            kind=EventKind.SET_METADATA,
            created_at=int(time.time())
        )

        event.sign(self.private_key.hex())

        message = json.dumps([ClientMessageType.EVENT, event.to_json_object()])
        self.relay_manager.publish_message(message)

        logger.info(f"Broadcasted metadata event: {event.id}")
        return event.id

    def publish_skill(self, skill_data: Dict[str, Any], category: str):
        """
        Broadcast Kind 30023 (Long-form Content) event for skill updates.

        Args:
            skill_data: Dictionary containing skill information
            category: Skill category for tagging
        """
        # Create content with skill details
        content = f"""# {skill_data.get('title', 'Skill Update')}

{skill_data.get('description', '')}

## Version
{skill_data.get('version', '1.0.0')}

## Instructions
{skill_data.get('instructions', '')}

## Tool Calls
{json.dumps(skill_data.get('tool_calls', []), indent=2)}

---
Published by {self.agent_name} - Autonomous Skill Orchestrator
"""

        # Create tags
        tags = [
            ["d", skill_data.get('identifier', f"skill-{int(time.time())}")],
            ["title", skill_data.get('title', 'Skill Update')],
            ["t", category],
            ["t", "skill"],
            ["t", "orchestrator"]
        ]

        event = Event(
            public_key=self.public_key.hex(),
            content=content,
            kind=EventKind.LONG_FORM_CONTENT,
            tags=tags,
            created_at=int(time.time())
        )

        event.sign(self.private_key.hex())

        message = json.dumps([ClientMessageType.EVENT, event.to_json_object()])
        self.relay_manager.publish_message(message)

        logger.info(f"Published skill event: {event.id} - {skill_data.get('title')}")
        return event.id

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def main():
    """Main function for testing the Nostr client."""
    try:
        with NostrClient() as client:
            # Broadcast metadata
            client.broadcast_metadata()

            # Example skill publication
            example_skill = {
                "title": "Test Skill",
                "description": "A test skill for demonstration",
                "version": "1.0.0",
                "instructions": "Test instructions",
                "tool_calls": ["test_call"],
                "identifier": "test-skill-001"
            }

            client.publish_skill(example_skill, "testing")

    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()