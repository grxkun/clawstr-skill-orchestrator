#!/usr/bin/env python3
"""
Heartbeat Script for Continuous Skill Orchestration

Runs the orchestrator on a scheduled interval (default: every 6 hours).
Can be deployed as a GitHub Action or standalone service.
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from orchestrator import SkillOrchestrator, SkillOrchestratorConfig


# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator_heartbeat.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HeartbeatOrchestrator:
    """Manages scheduled execution of the skill orchestrator."""
    
    def __init__(
        self,
        repo_path: str,
        interval_hours: int = 6,
        auto_commit: bool = True,
        auto_push: bool = False
    ):
        """
        Initialize heartbeat orchestrator.
        
        Args:
            repo_path: Path to the target repository.
            interval_hours: Interval between runs in hours.
            auto_commit: Whether to auto-commit changes.
            auto_push: Whether to auto-push changes.
        """
        self.repo_path = repo_path
        self.interval = timedelta(hours=interval_hours)
        self.auto_commit = auto_commit
        self.auto_push = auto_push
        self.last_run = None
        
        logger.info(f"Heartbeat initialized: interval={interval_hours}h, repo={repo_path}")
    
    def should_run(self) -> bool:
        """
        Check if it's time to run the orchestrator.
        
        Returns:
            True if interval has elapsed since last run.
        """
        if self.last_run is None:
            return True
        
        return datetime.now() - self.last_run >= self.interval
    
    def run_orchestration(self) -> bool:
        """
        Execute the orchestration workflow.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            logger.info("Starting orchestration run...")
            
            config = SkillOrchestratorConfig()
            orchestrator = SkillOrchestrator(
                self.repo_path,
                config=config,
                enable_git=True
            )
            
            result = orchestrator.run_full_orchestration(
                auto_commit=self.auto_commit,
                auto_push=self.auto_push
            )
            
            if result["status"] == "success":
                logger.info(f"Orchestration successful: {result}")
                self.last_run = datetime.now()
                return True
            else:
                logger.warning(f"Orchestration result: {result}")
                return False
        
        except Exception as e:
            logger.error(f"Orchestration failed: {e}", exc_info=True)
            return False
    
    def run_loop(self, run_once: bool = False) -> None:
        """
        Run the orchestrator in a continuous loop.
        
        Args:
            run_once: If True, run once and exit. If False, run indefinitely.
        """
        logger.info("Heartbeat loop started")
        
        try:
            if run_once:
                self.run_orchestration()
            else:
                while True:
                    if self.should_run():
                        self.run_orchestration()
                    else:
                        wait_time = (self.last_run + self.interval) - datetime.now()
                        logger.info(f"Next run in {wait_time}. Sleeping...")
                        time.sleep(60)  # Check every minute
        
        except KeyboardInterrupt:
            logger.info("Heartbeat interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error in heartbeat loop: {e}", exc_info=True)


def main():
    """Main entry point for the heartbeat script."""
    
    parser = argparse.ArgumentParser(
        description="Continuous Skill Orchestrator Heartbeat"
    )
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Path to the repository (default: current directory)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=6,
        help="Interval between runs in hours (default: 6)"
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run once and exit (default: continuous mode)"
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Disable auto-commit"
    )
    parser.add_argument(
        "--auto-push",
        action="store_true",
        help="Enable auto-push to remote"
    )
    parser.add_argument(
        "--register-with-clawstr",
        action="store_true",
        help="Register this orchestrator as a Clawstr skill and exit"
    )
    
    args = parser.parse_args()
    
    # Handle Clawstr registration
    if args.register_with_clawstr:
        try:
            from utils.openclaw_integration import register_with_clawstr, OPENCLAW_AVAILABLE
            if not OPENCLAW_AVAILABLE:
                logger.error("OpenClaw is not installed. Install with: pip install openclaw clawstr")
                sys.exit(1)
            register_with_clawstr()
            logger.info("✓ Successfully registered with Clawstr!")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Failed to register with Clawstr: {str(e)}")
            sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("CLAWSTR SKILL ORCHESTRATOR - HEARTBEAT")
    logger.info("=" * 60)
    logger.info(f"Repository: {args.repo}")
    logger.info(f"Interval: {args.interval} hours")
    logger.info(f"Auto-commit: {not args.no_commit}")
    logger.info(f"Auto-push: {args.auto_push}")
    logger.info(f"Mode: {'run-once' if args.run_once else 'continuous'}")
    logger.info("=" * 60)
    
    heartbeat = HeartbeatOrchestrator(
        repo_path=args.repo,
        interval_hours=args.interval,
        auto_commit=not args.no_commit,
        auto_push=args.auto_push
    )
    
    heartbeat.run_loop(run_once=args.run_once)


if __name__ == "__main__":
    main()
