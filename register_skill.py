#!/usr/bin/env python3
"""
Clawstr Registration Script

Register the SkillOrchestrator as a skill with your Clawstr agent.
Run this script to add the orchestrator to your agent's skill set.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Register the SkillOrchestrator with Clawstr."""
    logger.info("=" * 60)
    logger.info("Clawstr Skill Orchestrator Registration")
    logger.info("=" * 60)
    
    try:
        from utils.openclaw_integration import register_with_clawstr, OPENCLAW_AVAILABLE
        
        if not OPENCLAW_AVAILABLE:
            logger.error(
                "OpenClaw is not installed. Install dependencies with:\n"
                "  pip install -r requirements.txt"
            )
            return 1
        
        # Register with Clawstr
        agent = register_with_clawstr()
        
        if agent is None:
            logger.error("Failed to register with Clawstr.")
            return 1
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Registration successful!")
        logger.info("=" * 60)
        logger.info(
            "\nThe SkillOrchestrator is now registered with your Clawstr agent."
        )
        logger.info("\nYou can now call it from your agent with:")
        logger.info("  agent.execute_skill('SkillOrchestrator', {...})")
        logger.info("\nAvailable parameters:")
        logger.info("  - target_dir: Directory containing skills")
        logger.info("  - similarity_threshold: Clustering threshold (0-1)")
        logger.info("  - auto_commit: Auto-commit changes to git")
        logger.info("  - dry_run: Simulate without making changes")
        
        return 0
    
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error("Make sure all dependencies are installed:")
        logger.error("  pip install -r requirements.txt")
        return 1
    
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
