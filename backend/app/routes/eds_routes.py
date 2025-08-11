from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..services.git_service import GitService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/eds", tags=["EDS"])

class PushToGitRequest(BaseModel):
    block_name: str
    files: Dict[str, str]  # html, css, js, etc.
    metadata: Optional[Dict[str, Any]] = {}
    create_pr: bool = True

class PushToGitResponse(BaseModel):
    success: bool
    message: str
    block_name: str
    sanitized_name: str
    branch_name: str
    commit_sha: str
    commit_url: str
    branch_url: str
    pull_request_url: Optional[str] = None
    pull_request_number: Optional[int] = None
    files_written: list
    pr_error: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow extra fields from git service

@router.post("/push-to-git", response_model=PushToGitResponse)
async def push_eds_block_to_git(request: PushToGitRequest):
    """
    Push EDS block files to the configured Git repository
    
    This endpoint:
    1. Creates a new branch in the target repository
    2. Writes the EDS block files (HTML, CSS, JS) to the blocks/ directory
    3. Commits and pushes the changes
    4. Optionally creates a Pull Request
    
    Required environment variables:
    - GITHUB_TOKEN: Personal access token with repo permissions
    - GIT_REPO_URL: Target repository URL (default: https://github.com/Vinodh-Projects/EDS.git)
    """
    try:
        git_service = GitService()
        
        # Validate required files
        if not request.files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if not request.block_name or not request.block_name.strip():
            raise HTTPException(status_code=400, detail="Block name is required")
        
        # Add session metadata if available
        metadata = request.metadata or {}
        metadata.update({
            'author': metadata.get('author', 'DXP Component Generator'),
            'generated_at': metadata.get('generated_at', 'now')
        })
        
        logger.info(f"Pushing EDS block '{request.block_name}' to Git")
        
        # Push to Git
        result = await git_service.push_eds_block(
            block_name=request.block_name,
            files=request.files,
            metadata=metadata,
            create_pr=request.create_pr
        )
        
        # Format response - build it manually to avoid field conflicts
        response_data = {
            "success": result.get("success", True),
            "message": f"EDS block '{request.block_name}' successfully pushed to Git",
            "block_name": result.get("block_name", request.block_name),
            "sanitized_name": result.get("sanitized_name", ""),
            "branch_name": result.get("branch_name", ""),
            "commit_sha": result.get("commit_sha", ""),
            "commit_url": result.get("commit_url", ""),
            "branch_url": result.get("branch_url", ""),
            "pull_request_url": result.get("pull_request_url"),
            "pull_request_number": result.get("pull_request_number"),
            "files_written": result.get("files_written", []),
            "pr_error": result.get("pr_error")
        }
        
        response = PushToGitResponse(**response_data)
        
        logger.info(f"Successfully pushed EDS block to branch: {result['branch_name']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error pushing EDS block to Git: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to push EDS block to Git: {str(e)}"
        )

@router.get("/git-config")
async def get_git_config():
    """
    Get current Git configuration (for debugging/validation)
    """
    try:
        git_service = GitService()
        
        return {
            "configured": bool(git_service.github_token),
            "repo_url": git_service.repo_url,
            "base_branch": git_service.base_branch,
            "branch_prefix": git_service.branch_prefix,
            "author_name": git_service.author_name,
            "author_email": git_service.author_email,
            # Don't expose the actual token
            "has_github_token": bool(git_service.github_token),
            "has_github_client": bool(git_service.github_client)
        }
    except Exception as e:
        logger.error(f"Error getting Git config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Git config: {str(e)}")
