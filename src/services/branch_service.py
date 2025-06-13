"""Branch management service."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

from ..api import GitLabClient
from ..models import Branch, BranchOperation, BranchOperationType
from ..utils.logger import OperationLogger
from ..utils import ProgressTracker


logger = logging.getLogger(__name__)


class BranchService:
    """Service for managing GitLab branches."""
    
    def __init__(self, client: GitLabClient):
        """Initialize branch service.
        
        Args:
            client: GitLab API client
        """
        self.client = client
        self.operations_log: List[BranchOperation] = []
    
    def rename_branches_bulk(
        self,
        projects: List[Dict[str, Any]],
        old_branch: str,
        new_branch: str,
        dry_run: bool = False,
        skip_protected: bool = True,
        update_merge_requests: bool = False
    ) -> Dict[str, Any]:
        """Rename branches across multiple projects.
        
        Args:
            projects: List of project dictionaries
            old_branch: Current branch name
            new_branch: New branch name
            dry_run: Preview without making changes
            skip_protected: Skip protected branches
            update_merge_requests: Update MR target branches
            
        Returns:
            Operation summary
        """
        results = {
            'total': len(projects),
            'renamed': 0,
            'skipped': 0,
            'failed': 0,
            'operations': []
        }
        
        progress = ProgressTracker(
            projects,
            total=len(projects),
            description="Renaming branches",
            unit="projects"
        )
        
        for project in progress:
            operation = self.rename_branch_in_project(
                project,
                old_branch,
                new_branch,
                dry_run,
                skip_protected,
                update_merge_requests
            )
            
            self.operations_log.append(operation)
            results['operations'].append(operation)
            
            if operation.success:
                results['renamed'] += 1
            elif operation.error_message and 'not found' in operation.error_message:
                results['skipped'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    def rename_branch_in_project(
        self,
        project: Dict[str, Any],
        old_branch: str,
        new_branch: str,
        dry_run: bool = False,
        skip_protected: bool = True,
        update_merge_requests: bool = False
    ) -> BranchOperation:
        """Rename branch in a single project.
        
        Args:
            project: Project dictionary
            old_branch: Current branch name
            new_branch: New branch name
            dry_run: Preview without making changes
            skip_protected: Skip protected branches
            update_merge_requests: Update MR target branches
            
        Returns:
            Operation result
        """
        operation = BranchOperation(
            operation_type=BranchOperationType.RENAME,
            project_id=project['id'],
            project_name=project['name'],
            source_branch=old_branch,
            target_branch=new_branch,
            dry_run=dry_run
        )
        
        with OperationLogger(logger, "rename branch", project=project['name']):
            try:
                # Check if old branch exists
                if not self.client.branch_exists(project['id'], old_branch):
                    operation.error_message = f"Branch '{old_branch}' not found"
                    logger.info(operation.error_message)
                    return operation
                
                # Check if new branch already exists
                if self.client.branch_exists(project['id'], new_branch):
                    operation.error_message = f"Branch '{new_branch}' already exists"
                    logger.info(operation.error_message)
                    return operation
                
                # Get branch details
                if skip_protected:
                    branch_data = self.client.get_branch(project['id'], old_branch)
                    branch = Branch.from_gitlab_response(branch_data)
                    
                    if branch.protected:
                        operation.error_message = f"Branch '{old_branch}' is protected"
                        logger.warning(operation.error_message)
                        return operation
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would rename '{old_branch}' to '{new_branch}'")
                    operation.success = True
                    return operation
                
                # Perform rename
                success = self.client.rename_branch(
                    project['id'],
                    old_branch,
                    new_branch,
                    update_default=True
                )
                
                if success:
                    operation.success = True
                    logger.info(f"Successfully renamed '{old_branch}' to '{new_branch}'")
                    
                    # Update merge requests if requested
                    if update_merge_requests:
                        self._update_merge_requests(
                            project['id'],
                            old_branch,
                            new_branch
                        )
                else:
                    operation.error_message = "Rename operation failed"
                    
            except Exception as e:
                operation.error_message = str(e)
                logger.error(f"Failed to rename branch: {e}")
        
        return operation
    
    def _update_merge_requests(
        self,
        project_id: int,
        old_branch: str,
        new_branch: str
    ):
        """Update merge requests targeting the old branch.
        
        Args:
            project_id: Project ID
            old_branch: Old branch name
            new_branch: New branch name
        """
        try:
            # Get open MRs targeting the old branch
            mrs = list(self.client._paginated_get(
                f'projects/{project_id}/merge_requests',
                state='opened',
                target_branch=old_branch
            ))
            
            for mr in mrs:
                try:
                    self.client._request(
                        'PUT',
                        f'projects/{project_id}/merge_requests/{mr["iid"]}',
                        json={'target_branch': new_branch}
                    )
                    logger.info(f"Updated MR !{mr['iid']} target branch to '{new_branch}'")
                except Exception as e:
                    logger.warning(f"Failed to update MR !{mr['iid']}: {e}")
                    
        except Exception as e:
            logger.warning(f"Failed to update merge requests: {e}")
    
    def create_branch(
        self,
        project_id: Union[int, str],
        branch_name: str,
        ref: str = 'main',
        dry_run: bool = False
    ) -> BranchOperation:
        """Create a new branch.
        
        Args:
            project_id: Project ID or path
            branch_name: New branch name
            ref: Reference branch/commit
            dry_run: Preview without creating
            
        Returns:
            Operation result
        """
        operation = BranchOperation(
            operation_type=BranchOperationType.CREATE,
            project_id=project_id,
            project_name=str(project_id),
            target_branch=branch_name,
            dry_run=dry_run
        )
        
        try:
            if self.client.branch_exists(project_id, branch_name):
                operation.error_message = f"Branch '{branch_name}' already exists"
                return operation
            
            if dry_run:
                logger.info(f"[DRY RUN] Would create branch '{branch_name}' from '{ref}'")
                operation.success = True
                return operation
            
            self.client.create_branch(project_id, branch_name, ref)
            operation.success = True
            logger.info(f"Created branch '{branch_name}' from '{ref}'")
            
        except Exception as e:
            operation.error_message = str(e)
            logger.error(f"Failed to create branch: {e}")
        
        return operation
    
    def protect_branch(
        self,
        project_id: Union[int, str],
        branch_name: str,
        push_access_level: int = 40,  # Maintainer
        merge_access_level: int = 30,  # Developer
        dry_run: bool = False
    ) -> BranchOperation:
        """Protect a branch.
        
        Args:
            project_id: Project ID or path
            branch_name: Branch to protect
            push_access_level: Access level for push (0=No one, 30=Developer, 40=Maintainer)
            merge_access_level: Access level for merge
            dry_run: Preview without protecting
            
        Returns:
            Operation result
        """
        operation = BranchOperation(
            operation_type=BranchOperationType.PROTECT,
            project_id=project_id,
            project_name=str(project_id),
            target_branch=branch_name,
            dry_run=dry_run
        )
        
        try:
            if not self.client.branch_exists(project_id, branch_name):
                operation.error_message = f"Branch '{branch_name}' not found"
                return operation
            
            if dry_run:
                logger.info(f"[DRY RUN] Would protect branch '{branch_name}'")
                operation.success = True
                return operation
            
            self.client._request(
                'POST',
                f'projects/{project_id}/protected_branches',
                json={
                    'name': branch_name,
                    'push_access_level': push_access_level,
                    'merge_access_level': merge_access_level
                }
            )
            
            operation.success = True
            logger.info(f"Protected branch '{branch_name}'")
            
        except Exception as e:
            operation.error_message = str(e)
            logger.error(f"Failed to protect branch: {e}")
        
        return operation
    
    def get_stale_branches(
        self,
        project_id: Union[int, str],
        days_inactive: int = 90,
        exclude_patterns: List[str] = None
    ) -> List[Branch]:
        """Get branches that haven't been updated recently.
        
        Args:
            project_id: Project ID or path
            days_inactive: Number of days to consider a branch stale
            exclude_patterns: Branch name patterns to exclude
            
        Returns:
            List of stale branches
        """
        exclude_patterns = exclude_patterns or ['main', 'master', 'develop', 'release/*']
        stale_branches = []
        
        branches = self.client.get_branches(project_id)
        cutoff_date = datetime.now().timestamp() - (days_inactive * 86400)
        
        for branch_data in branches:
            branch = Branch.from_gitlab_response(branch_data)
            
            # Skip protected branches
            if branch.protected:
                continue
            
            # Skip excluded patterns
            if any(
                pattern in branch.name or 
                (pattern.endswith('*') and branch.name.startswith(pattern[:-1]))
                for pattern in exclude_patterns
            ):
                continue
            
            # Check last commit date
            if branch.last_commit_date:
                if branch.last_commit_date.timestamp() < cutoff_date:
                    stale_branches.append(branch)
        
        return stale_branches
    
    def save_operations_log(self, file_path: Union[str, Path]):
        """Save operations log to file.
        
        Args:
            file_path: Path to save log file
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'operations': [op.to_dict() for op in self.operations_log]
        }
        
        with open(path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"Saved operations log to {path}")