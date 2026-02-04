"""
Automated Skill Orchestrator for Clawstr AI Framework

Core engine for discovering, analyzing, consolidating, and publishing skills.
Manages skill clustering, duplicate detection, and automated Git operations.

Registered as an OpenClaw skill for integration with the Clawstr agent framework.
"""

import os
import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime
import yaml

from utils.nlp_helper import NLPHelper
from utils.git_manager import GitManager

try:
    from openclaw import Skill, SkillResult
    from clawstr import Agent
    OPENCLAW_AVAILABLE = True
except ImportError:
    OPENCLAW_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("OpenClaw not installed. Registering as a Clawstr skill requires 'pip install openclaw clawstr'")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SkillOrchestratorConfig:
    """Configuration for the orchestrator."""
    
    def __init__(self):
        self.similarity_threshold = 0.6  # For clustering
        self.duplicate_threshold = 0.85  # For identifying duplicates
        self.archive_dir = "archive"
        self.skills_dir = "skills"
        self.auto_commit = True
        self.auto_push = False


class SkillOrchestrator:
    """
    Main orchestrator class for managing and consolidating skills.
    
    Workflow:
    1. Discover: Scan for SKILL.md files
    2. Parse: Extract YAML frontmatter
    3. Cluster: Group similar skills
    4. Consolidate: Merge overlapping skills
    5. Archive: Move originals to archive
    6. Publish: Update version and commit
    """
    
    def __init__(
        self,
        repo_path: str,
        config: Optional[SkillOrchestratorConfig] = None,
        enable_git: bool = True
    ):
        """
        Initialize the orchestrator.
        
        Args:
            repo_path: Path to the target repository.
            config: Configuration object (uses defaults if None).
            enable_git: Whether to enable Git operations.
        """
        self.repo_path = Path(repo_path)
        self.config = config or SkillOrchestratorConfig()
        self.nlp_helper = NLPHelper()
        
        self.git_manager = None
        if enable_git:
            try:
                self.git_manager = GitManager(str(self.repo_path))
                logger.info(f"Git manager initialized for {repo_path}")
            except ValueError as e:
                logger.warning(f"Git initialization failed: {e}")
        
        self.discovered_skills = []
        self.clusters = {}
    
    # ===================== DISCOVERY PHASE =====================
    
    def discover_skills(self, target_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover all SKILL.md files in the target directory.
        
        Args:
            target_dir: Directory to scan (uses config.skills_dir if None).
            
        Returns:
            List of discovered skill dicts.
        """
        target_dir = target_dir or self.config.skills_dir
        target_path = self.repo_path / target_dir
        
        if not target_path.exists():
            logger.warning(f"Skills directory not found: {target_path}")
            return []
        
        self.discovered_skills = []
        
        for skill_file in target_path.glob("**/*.md"):
            try:
                skill_data = self._parse_skill_file(skill_file)
                if skill_data:
                    self.discovered_skills.append(skill_data)
                    logger.info(f"Discovered skill: {skill_data['name']} ({skill_file})")
            except Exception as e:
                logger.error(f"Failed to parse {skill_file}: {e}")
        
        logger.info(f"Total skills discovered: {len(self.discovered_skills)}")
        return self.discovered_skills
    
    def _parse_skill_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a SKILL.md file and extract YAML frontmatter.
        
        Expected format:
        ---
        name: Skill Name
        description: Skill description
        version: 1.0.0
        author: Author Name
        category: Category
        ---
        # Markdown content...
        
        Args:
            file_path: Path to the SKILL.md file.
            
        Returns:
            Dictionary with parsed skill data, or None if parsing fails.
        """
        content = file_path.read_text(encoding="utf-8")
        
        # Extract YAML frontmatter
        pattern = r"^---\n(.*?)\n---\n(.*)"
        match = re.match(pattern, content, re.DOTALL)
        
        if not match:
            logger.warning(f"No YAML frontmatter found in {file_path}")
            return None
        
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2).strip()
            
            # Ensure required fields
            if not frontmatter.get("name"):
                logger.warning(f"Skill missing 'name' field: {file_path}")
                return None
            
            return {
                "name": frontmatter.get("name"),
                "description": frontmatter.get("description", ""),
                "version": frontmatter.get("version", "1.0.0"),
                "author": frontmatter.get("author", "Unknown"),
                "category": frontmatter.get("category", "uncategorized"),
                "tags": frontmatter.get("tags", []),
                "metadata": frontmatter,
                "body": body,
                "file_path": str(file_path)
            }
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {file_path}: {e}")
            return None
    
    # ===================== CLUSTERING PHASE =====================
    
    def cluster_skills(self, threshold: Optional[float] = None) -> Dict[str, List[Dict]]:
        """
        Cluster discovered skills based on semantic similarity.
        
        Args:
            threshold: Similarity threshold (uses config if None).
            
        Returns:
            Dictionary mapping cluster IDs to skill lists.
        """
        if not self.discovered_skills:
            logger.warning("No skills to cluster. Run discover_skills() first.")
            return {}
        
        threshold = threshold or self.config.similarity_threshold
        
        self.clusters = self.nlp_helper.cluster_skills(
            self.discovered_skills,
            threshold=threshold
        )
        
        logger.info(f"Clustered {len(self.discovered_skills)} skills into {len(self.clusters)} groups")
        
        for cluster_id, skills in self.clusters.items():
            names = [s["name"] for s in skills]
            logger.info(f"{cluster_id}: {names}")
        
        return self.clusters
    
    # ===================== CONSOLIDATION PHASE =====================
    
    def consolidate_cluster(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """
        Consolidate skills in a cluster into a single master skill.
        
        Strategy:
        - Master skill name = first skill's name + "_Master"
        - Description = merged descriptions with deduplication
        - Body = consolidated workflow steps
        - Version = incremented from max version
        
        Args:
            cluster_id: ID of the cluster to consolidate.
            
        Returns:
            Consolidated skill dict, or None if consolidation fails.
        """
        if cluster_id not in self.clusters:
            logger.error(f"Cluster not found: {cluster_id}")
            return None
        
        skills = self.clusters[cluster_id]
        
        if len(skills) <= 1:
            logger.info(f"Skipping {cluster_id}: only 1 skill")
            return None
        
        logger.info(f"Consolidating {len(skills)} skills in {cluster_id}")
        
        # Create master skill metadata
        master_name = f"{skills[0]['name']}_Master"
        master_version = self._increment_version(
            max((s.get("version", "1.0.0") for s in skills), default="1.0.0")
        )
        
        master_skill = {
            "name": master_name,
            "description": self._merge_descriptions(skills),
            "version": master_version,
            "author": "Clawstr Orchestrator",
            "category": skills[0].get("category", "uncategorized"),
            "tags": list(set(tag for s in skills for tag in s.get("tags", []))),
            "merged_from": [s["name"] for s in skills],
            "consolidated_at": datetime.now().isoformat(),
            "body": self._merge_bodies(skills),
            "metadata": {
                "name": master_name,
                "description": self._merge_descriptions(skills),
                "version": master_version,
                "author": "Clawstr Orchestrator",
                "category": skills[0].get("category", "uncategorized"),
                "tags": list(set(tag for s in skills for tag in s.get("tags", []))),
                "merged_from": [s["name"] for s in skills],
            }
        }
        
        return master_skill
    
    def _merge_descriptions(self, skills: List[Dict[str, Any]]) -> str:
        """Merge descriptions from multiple skills."""
        descriptions = [s.get("description", "").strip() for s in skills if s.get("description")]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_descriptions = []
        for desc in descriptions:
            if desc and desc not in seen:
                seen.add(desc)
                unique_descriptions.append(desc)
        
        return " ".join(unique_descriptions)
    
    def _merge_bodies(self, skills: List[Dict[str, Any]]) -> str:
        """
        Merge Markdown bodies from multiple skills.
        
        Strategy:
        - Extract workflow steps from each skill
        - Remove duplicate steps
        - Combine into a unified workflow
        """
        bodies = [s.get("body", "") for s in skills if s.get("body")]
        
        if not bodies:
            return "# Consolidated Workflow\n\nNo body content found."
        
        merged_content = "# Consolidated Workflow\n\n"
        
        all_sections = []
        for body in bodies:
            # Extract headers and content
            sections = re.split(r"\n(?=#+\s)", body)
            all_sections.extend([s.strip() for s in sections if s.strip()])
        
        # Deduplicate sections
        seen_sections = set()
        unique_sections = []
        for section in all_sections:
            if section not in seen_sections:
                seen_sections.add(section)
                unique_sections.append(section)
        
        merged_content += "\n\n".join(unique_sections)
        
        return merged_content
    
    def _increment_version(self, version_str: str) -> str:
        """
        Increment a semantic version string.
        
        Args:
            version_str: Version in format "major.minor.patch"
            
        Returns:
            Incremented version with patch bumped.
        """
        try:
            parts = version_str.split(".")
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            patch += 1
            return f"{major}.{minor}.{patch}"
        except Exception:
            return "1.0.1"
    
    # ===================== PUBLISHING PHASE =====================
    
    def publish_consolidated_skill(
        self,
        consolidated_skill: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> Optional[Path]:
        """
        Write consolidated skill to a SKILL.md file.
        
        Args:
            consolidated_skill: The consolidated skill dict.
            output_dir: Output directory (uses config.skills_dir if None).
            
        Returns:
            Path to the written file, or None if writing fails.
        """
        output_dir = output_dir or self.config.skills_dir
        output_path = self.repo_path / output_dir
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create SKILL.md filename
        skill_filename = output_path / f"{consolidated_skill['name']}.md"
        
        # Build YAML frontmatter
        metadata = consolidated_skill["metadata"]
        yaml_content = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        
        # Build complete file content
        file_content = f"---\n{yaml_content}---\n\n{consolidated_skill['body']}\n"
        
        try:
            skill_filename.write_text(file_content, encoding="utf-8")
            logger.info(f"Published consolidated skill: {skill_filename}")
            return skill_filename
        except Exception as e:
            logger.error(f"Failed to write skill file {skill_filename}: {e}")
            return None
    
    def archive_original_skills(self, skill_names: List[str]) -> List[Path]:
        """
        Move original skill files to the archive directory.
        
        Args:
            skill_names: List of skill names to archive.
            
        Returns:
            List of archived file paths.
        """
        archive_path = self.repo_path / self.config.archive_dir
        archive_path.mkdir(parents=True, exist_ok=True)
        
        archived = []
        
        for skill in self.discovered_skills:
            if skill["name"] in skill_names:
                src = Path(skill["file_path"])
                if src.exists():
                    dest = archive_path / src.name
                    src.rename(dest)
                    archived.append(dest)
                    logger.info(f"Archived: {src} -> {dest}")
        
        return archived
    
    # ===================== GIT OPERATIONS =====================
    
    def commit_changes(self, message: str) -> Optional[str]:
        """
        Commit orchestrator changes to Git.
        
        Args:
            message: Commit message.
            
        Returns:
            Commit hash, or None if not using Git.
        """
        if not self.git_manager or not self.config.auto_commit:
            return None
        
        try:
            # Stage all changes
            self.git_manager.add_files(["skills/", "archive/"])
            commit_hash = self.git_manager.commit(message)
            logger.info(f"Changes committed: {commit_hash}")
            return commit_hash
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            return None
    
    def push_changes(self, remote: str = "origin", branch: Optional[str] = None) -> bool:
        """
        Push changes to remote repository.
        
        Args:
            remote: Remote name (default: origin).
            branch: Branch name (default: current branch).
            
        Returns:
            True if push succeeded, False otherwise.
        """
        if not self.git_manager or not self.config.auto_push:
            return False
        
        try:
            self.git_manager.push(remote, branch)
            logger.info("Changes pushed to remote")
            return True
        except Exception as e:
            logger.error(f"Failed to push changes: {e}")
            return False
    
    # ===================== FULL WORKFLOW =====================
    
    def run_full_orchestration(
        self,
        target_dir: Optional[str] = None,
        auto_commit: bool = True,
        auto_push: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the complete orchestration workflow.
        
        Args:
            target_dir: Directory containing skills.
            auto_commit: Whether to commit changes.
            auto_push: Whether to push changes.
            
        Returns:
            Summary of orchestration results.
        """
        self.config.auto_commit = auto_commit
        self.config.auto_push = auto_push
        
        logger.info("=" * 60)
        logger.info("STARTING SKILL ORCHESTRATION")
        logger.info("=" * 60)
        
        # Phase 1: Discovery
        logger.info("\n[Phase 1] Discovering skills...")
        skills = self.discover_skills(target_dir)
        
        if not skills:
            logger.warning("No skills discovered. Exiting.")
            return {"status": "no_skills_found", "skills_discovered": 0}
        
        # Phase 2: Clustering
        logger.info("\n[Phase 2] Clustering skills...")
        clusters = self.cluster_skills()
        
        # Phase 3: Consolidation
        logger.info("\n[Phase 3] Consolidating clusters...")
        consolidated = []
        archivable_skills = []
        
        for cluster_id, cluster_skills in clusters.items():
            if len(cluster_skills) > 1:
                master = self.consolidate_cluster(cluster_id)
                if master:
                    consolidated.append(master)
                    archivable_skills.extend([s["name"] for s in cluster_skills])
        
        # Phase 4: Publishing
        logger.info("\n[Phase 4] Publishing consolidated skills...")
        published = []
        for skill in consolidated:
            result = self.publish_consolidated_skill(skill)
            if result:
                published.append(str(result))
        
        # Phase 5: Archiving
        logger.info("\n[Phase 5] Archiving original skills...")
        archived = self.archive_original_skills(archivable_skills)
        
        # Phase 6: Git operations
        if auto_commit:
            logger.info("\n[Phase 6] Committing changes...")
            self.commit_changes(
                f"Orchestration: Consolidated {len(consolidated)} skill clusters"
            )
        
        if auto_push:
            logger.info("\n[Phase 7] Pushing changes...")
            self.push_changes()
        
        logger.info("\n" + "=" * 60)
        logger.info("ORCHESTRATION COMPLETE")
        logger.info("=" * 60)
        
        return {
            "status": "success",
            "skills_discovered": len(skills),
            "clusters_created": len(clusters),
            "skills_consolidated": len(consolidated),
            "skills_published": len(published),
            "skills_archived": len(archived),
            "published_files": published,
            "archived_files": [str(f) for f in archived]
        }
