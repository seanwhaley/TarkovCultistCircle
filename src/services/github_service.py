"""GitHub service for issue management."""
import os
import logging
from typing import Dict, Any, List, Optional
from github import Github
from github.PaginatedList import PaginatedList
from github.GitRelease import GitRelease
from github.GithubObject import GitHubObject

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for interacting with GitHub."""
    
    def __init__(self):
        self._client = None
        self._repo = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize GitHub client."""
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            logger.warning("GITHUB_TOKEN not set - GitHub integration disabled")
            return
            
        try:
            self._client = Github(token)
            repo_name = os.getenv('GITHUB_REPO')
            if repo_name:
                self._repo = self._client.get_repo(repo_name)
        except Exception as e:
            logger.error(f"Failed to initialize GitHub client: {str(e)}")
            self._client = None
            self._repo = None
    
    def create_task_issues(self, action_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create GitHub issues from action plan tasks."""
        if not self._client or not self._repo:
            logger.warning("GitHub integration not available - skipping issue creation")
            return []
            
        created_issues = []
        actions = action_plan.get('actions', [])
        
        for action in actions:
            tasks = action.get('tasks', [])
            for task in tasks:
                try:
                    issue = self._create_issue_from_task(action, task)
                    created_issues.append({
                        'number': issue.number,
                        'url': issue.html_url,
                        'title': issue.title,
                        'task_id': task.get('task_id')
                    })
                except Exception as e:
                    logger.error(f"Failed to create issue for task {task.get('task_id')}: {str(e)}")
        
        return created_issues
    
    def _create_issue_from_task(self, action: Dict[str, Any], task: Dict[str, Any]) -> Issue:
        """Create a GitHub issue for a specific task."""
        title = f"[{task['task_id']}] {task['description']}"
        
        body = f"""## Task Details
{task['description']}

## Related Requirements
{chr(10).join(f'- {req}' for req in action.get('related_requirements', []))}

## Implementation Details
- Action: {action['action']}
- Priority: {action['priority']}
- Code Location: {task.get('code_location', 'TBD')}
- Estimated Time: {task.get('estimated_time', 'TBD')}

## Dependencies
{chr(10).join(f'- {dep}' for dep in task.get('dependencies', []))}
"""
        
        labels = [
            f"priority-{action['priority'].lower()}",
            "ai-ready",
            f"type-{action['action'].lower().split()[0]}"
        ]
        
        return self._repo.create_issue(
            title=title,
            body=body,
            labels=labels
        )

# Global instance
github_service = GitHubService()