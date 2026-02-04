"""
OpenClaw Integration Module

Provides integration with the OpenClaw agent framework and Clawstr registration.
Allows the Skill Orchestrator to be registered as a skill in the Clawstr agent.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from openclaw import Skill, SkillResult, SkillContext
    OPENCLAW_AVAILABLE = True
except ImportError:
    OPENCLAW_AVAILABLE = False


class SkillOrchestratorAsOpenClawSkill:
    """
    Wraps the SkillOrchestrator as an OpenClaw-compatible skill.
    
    This allows the orchestrator to be registered with a Clawstr agent
    and executed as a native skill within the agent's workflow.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the OpenClaw skill wrapper.
        
        Args:
            repo_path: Path to the target repository.
        """
        if not OPENCLAW_AVAILABLE:
            raise ImportError(
                "OpenClaw is not installed. "
                "Install it with: pip install openclaw clawstr"
            )
        
        self.repo_path = Path(repo_path)
        self.skill_metadata = {
            "name": "SkillOrchestrator",
            "description": (
                "Automated skill orchestrator that discovers, clusters, "
                "consolidates, and publishes AI skills with semantic analysis"
            ),
            "version": "1.0.0",
            "author": "Clawstr Team",
            "tags": ["automation", "skill-management", "consolidation"],
        }
    
    def execute(
        self,
        target_dir: Optional[str] = None,
        similarity_threshold: float = 0.6,
        auto_commit: bool = True,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute the skill orchestration workflow.
        
        Args:
            target_dir: Directory containing skills (defaults to 'skills').
            similarity_threshold: Threshold for clustering similar skills.
            auto_commit: Whether to auto-commit changes to git.
            dry_run: If True, simulate without making changes.
            
        Returns:
            Result dict with execution status and metrics.
        """
        from orchestrator import SkillOrchestrator, SkillOrchestratorConfig
        
        logger.info(f"Starting OpenClaw skill: SkillOrchestrator")
        
        config = SkillOrchestratorConfig()
        config.similarity_threshold = similarity_threshold
        config.auto_commit = auto_commit
        
        try:
            orchestrator = SkillOrchestrator(
                str(self.repo_path),
                config=config,
                enable_git=not dry_run
            )
            
            # Execute orchestration workflow
            logger.info("Phase 1: Discovering skills...")
            skills = orchestrator.discover_skills(target_dir)
            
            if not skills:
                return {
                    "status": "success",
                    "message": "No skills found to orchestrate",
                    "skills_discovered": 0,
                    "clusters": 0,
                    "consolidated": 0,
                }
            
            logger.info(f"Phase 2: Clustering {len(skills)} skills...")
            orchestrator.cluster_skills(similarity_threshold)
            
            consolidated_count = 0
            for cluster_id, cluster_skills in orchestrator.clusters.items():
                if len(cluster_skills) > 1:
                    logger.info(
                        f"Phase 3: Consolidating cluster '{cluster_id}' "
                        f"with {len(cluster_skills)} skills..."
                    )
                    
                    if not dry_run:
                        consolidated_count += orchestrator.consolidate_cluster(
                            cluster_id
                        )
            
            # Publish changes
            if not dry_run and consolidated_count > 0:
                logger.info("Phase 4: Publishing consolidated skills...")
                orchestrator.publish_changes(
                    auto_commit=auto_commit
                )
            
            return {
                "status": "success",
                "message": "Skill orchestration completed successfully",
                "skills_discovered": len(skills),
                "clusters": len(orchestrator.clusters),
                "consolidated": consolidated_count,
                "dry_run": dry_run,
            }
        
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Orchestration failed: {str(e)}",
                "error_type": type(e).__name__,
            }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return skill metadata for Clawstr registration."""
        return self.skill_metadata


def register_with_clawstr(agent: Optional[Any] = None) -> Optional[Any]:
    """
    Register the SkillOrchestrator as a skill with a Clawstr agent.
    
    Usage:
        from utils.openclaw_integration import register_with_clawstr
        from clawstr import Agent
        
        agent = Agent()
        register_with_clawstr(agent)
    
    Args:
        agent: Clawstr Agent instance (optional, creates one if not provided).
        
    Returns:
        The registered skill or agent instance.
    """
    if not OPENCLAW_AVAILABLE:
        logger.error(
            "Cannot register with Clawstr: OpenClaw is not installed. "
            "Install with: pip install openclaw clawstr"
        )
        return None
    
    try:
        if agent is None:
            from clawstr import Agent
            agent = Agent()
        
        orchestrator_skill = SkillOrchestratorAsOpenClawSkill(".")
        
        # Register the skill with the agent
        agent.register_skill(
            name=orchestrator_skill.skill_metadata["name"],
            description=orchestrator_skill.skill_metadata["description"],
            execute=orchestrator_skill.execute,
            metadata=orchestrator_skill.get_metadata(),
        )
        
        logger.info(
            f"Successfully registered '{orchestrator_skill.skill_metadata['name']}' "
            "with Clawstr agent"
        )
        return agent
    
    except Exception as e:
        logger.error(f"Failed to register skill with Clawstr: {str(e)}")
        return None
