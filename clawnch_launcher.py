"""
Clawnch Launcher for Token Deployment

Handles posting Kind 1 events to launch tokens on Clawnch.
Ensures token launch logic only triggers once upon initial setup.
"""

import os
import json
import time
import logging
from typing import Optional
from pathlib import Path
from datetime import datetime

from nostr.key import PrivateKey
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClawnchLauncher:
    """
    Handles token launching on Clawnch via Nostr Kind 1 posts.

    Posts a formatted message that Clawnch scanners will detect to deploy
    the token on the Base network automatically.
    """

    def __init__(self):
        """Initialize Clawnch launcher with configuration."""
        self.nsec = os.getenv('NOSTR_NSEC')
        self.relay_url = os.getenv('NOSTR_RELAY', 'wss://lightningrelay.com')
        self.token_ticker = os.getenv('TOKEN_TICKER', 'SKILL')
        self.agent_name = os.getenv('AGENT_NAME', 'MasterOrchestrator')

        if not self.nsec:
            raise ValueError("NOSTR_NSEC environment variable is required")

        self.private_key = PrivateKey.from_nsec(self.nsec)
        self.public_key = self.private_key.public_key

        # Track if token has been launched
        self.launch_file = Path('.clawnch_launched')
        self._launched = self.launch_file.exists()

    def is_launched(self) -> bool:
        """Check if token has already been launched."""
        return self._launched

    def launch_token(self) -> bool:
        """
        Launch token on Clawnch by posting Kind 1 event.

        Returns True if successful, False if already launched or failed.
        """
        if self.is_launched():
            logger.info("Token already launched. Skipping.")
            return False

        try:
            # Create the launch message
            message = f'I am launching ${self.token_ticker} token. Total supply 1B. Purpose: Governance for the {self.agent_name}. @clawnch_world'

            # Create Kind 1 event
            event = Event(
                public_key=self.public_key.hex(),
                content=message,
                kind=EventKind.TEXT_NOTE,
                created_at=int(time.time())
            )

            # Sign the event
            event.sign(self.private_key.hex())

            # Connect to relay and publish
            relay_manager = RelayManager()
            relay_manager.add_relay(self.relay_url)
            relay_manager.open_connections()

            # Wait for connections
            time.sleep(2)

            # Publish the event
            relay_manager.publish_event(event)

            # Wait for publication
            time.sleep(2)

            # Close connections
            relay_manager.close_connections()

            # Mark as launched
            self.launch_file.touch()
            self._launched = True

            logger.info(f"Token ${self.token_ticker} launched successfully on Clawnch")
            return True

        except Exception as e:
            logger.error(f"Failed to launch token: {e}")
            return False

    def reset_launch_status(self):
        """Reset launch status (for testing/debugging)."""
        if self.launch_file.exists():
            self.launch_file.unlink()
            self._launched = False
            logger.info("Launch status reset")