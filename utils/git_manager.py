"""
Git Manager Module for Automated Repository Operations

Handles automated commits, pushes, and repository management for the orchestrator.
"""

import os
import logging
from typing import Optional, List
from pathlib import Path
from git import Repo, GitCommandError


logger = logging.getLogger(__name__)


class GitManager:
    """Manages Git operations for the skill orchestrator."""
    
    def __init__(self, repo_path: str):
        """
        Initialize Git manager with a repository path.
        
        Args:
            repo_path: Path to the Git repository.
            
        Raises:
            ValueError: If the path is not a valid Git repository.
        """
        self.repo_path = Path(repo_path)
        
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a valid Git repository: {repo_path}")
        
        self.repo = Repo(str(self.repo_path))
        
        # Get current user config or use defaults
        try:
            self.user_name = self.repo.config_reader().get_value("user", "name")
            self.user_email = self.repo.config_reader().get_value("user", "email")
        except Exception:
            self.user_name = "Clawstr Orchestrator"
            self.user_email = "orchestrator@clawstr.ai"
    
    def add_files(self, file_paths: List[str]) -> None:
        """
        Stage files for commit.
        
        Args:
            file_paths: List of file paths (relative to repo root) to stage.
        """
        for file_path in file_paths:
            self.repo.index.add([file_path])
            logger.info(f"Staged: {file_path}")
    
    def remove_files(self, file_paths: List[str]) -> None:
        """
        Remove files from the repository.
        
        Args:
            file_paths: List of file paths to remove.
        """
        for file_path in file_paths:
            if (self.repo_path / file_path).exists():
                self.repo.index.remove([file_path])
                logger.info(f"Removed: {file_path}")
    
    def commit(self, message: str, author_name: Optional[str] = None,
               author_email: Optional[str] = None) -> Optional[str]:
        """
        Create a commit with the staged changes.
        
        Args:
            message: Commit message.
            author_name: Author name (uses config default if not provided).
            author_email: Author email (uses config default if not provided).
            
        Returns:
            Commit hash, or None if there are no changes to commit.
        """
        if not self.repo.index.diff("HEAD"):
            logger.info("No changes to commit")
            return None
        
        author_name = author_name or self.user_name
        author_email = author_email or self.user_email
        
        try:
            commit = self.repo.index.commit(
                message,
                author=f"{author_name} <{author_email}>"
            )
            logger.info(f"Committed: {commit.hexsha[:8]} - {message}")
            return commit.hexsha
        except GitCommandError as e:
            logger.error(f"Commit failed: {e}")
            raise
    
    def push(self, remote: str = "origin", branch: Optional[str] = None) -> None:
        """
        Push commits to remote repository.
        
        Args:
            remote: Remote repository name (default: origin).
            branch: Branch name to push (default: current branch).
            
        Raises:
            GitCommandError: If push fails.
        """
        if branch is None:
            branch = self.repo.active_branch.name
        
        try:
            self.repo.remote(remote).push(branch)
            logger.info(f"Pushed to {remote}/{branch}")
        except GitCommandError as e:
            logger.error(f"Push failed: {e}")
            raise
    
    def get_current_branch(self) -> str:
        """
        Get the current branch name.
        
        Returns:
            Current branch name.
        """
        return self.repo.active_branch.name
    
    def get_status(self) -> dict:
        """
        Get repository status.
        
        Returns:
            Dictionary with staged, unstaged, and untracked files.
        """
        return {
            "staged": self.repo.index.diff("HEAD"),
            "unstaged": self.repo.index.diff(),
            "untracked": self.repo.untracked_files
        }
    
    def create_branch(self, branch_name: str) -> None:
        """
        Create and checkout a new branch.
        
        Args:
            branch_name: Name of the new branch.
        """
        self.repo.create_head(branch_name)
        self.repo.heads[branch_name].checkout()
        logger.info(f"Created and checked out branch: {branch_name}")
    
    def checkout_branch(self, branch_name: str) -> None:
        """
        Checkout an existing branch.
        
        Args:
            branch_name: Name of the branch to checkout.
        """
        self.repo.heads[branch_name].checkout()
        logger.info(f"Checked out branch: {branch_name}")
    
    def get_file_history(self, file_path: str, max_count: int = 5) -> List[dict]:
        """
        Get commit history for a specific file.
        
        Args:
            file_path: Path to the file.
            max_count: Maximum number of commits to retrieve.
            
        Returns:
            List of commit info dicts.
        """
        commits = list(self.repo.iter_commits(paths=file_path, max_count=max_count))
        return [
            {
                "hash": commit.hexsha[:8],
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
                "message": commit.message.strip()
            }
            for commit in commits
        ]
