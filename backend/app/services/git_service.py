import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from git import Repo
from github import Github
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class GitService:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_url = os.getenv('GIT_REPO_URL', 'https://github.com/Vinodh-Projects/EDS.git')
        self.base_branch = os.getenv('GIT_BASE_BRANCH', 'main')
        self.branch_prefix = os.getenv('GIT_BRANCH_PREFIX', 'eds/')
        self.author_name = os.getenv('GIT_AUTHOR_NAME', 'DXP Bot')
        self.author_email = os.getenv('GIT_AUTHOR_EMAIL', 'dxp-bot@example.com')
        
        if not self.github_token:
            logger.warning("GITHUB_TOKEN not configured - Git push will not work")
        
        # Initialize GitHub client
        self.github_client = Github(self.github_token) if self.github_token else None
    
    def sanitize_block_name(self, name: str) -> str:
        """Convert block name to kebab-case for safe file/folder names"""
        import re
        # Replace spaces and special chars with hyphens, convert to lowercase
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '-', name.lower())
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip('-')
    
    def create_branch_name(self, block_name: str) -> str:
        """Generate unique branch name with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        sanitized_name = self.sanitize_block_name(block_name)
        return f"{self.branch_prefix}{sanitized_name}-{timestamp}"
    
    def get_repo_info(self) -> Dict[str, str]:
        """Extract owner and repo name from URL"""
        if 'github.com/' in self.repo_url:
            # Extract from https://github.com/owner/repo.git or git@github.com:owner/repo.git
            if self.repo_url.startswith('https://'):
                path = self.repo_url.replace('https://github.com/', '').replace('.git', '')
            else:
                path = self.repo_url.split(':')[1].replace('.git', '')
            
            parts = path.split('/')
            return {'owner': parts[0], 'repo': parts[1]}
        
        raise ValueError(f"Cannot parse GitHub repo from URL: {self.repo_url}")
    
    async def push_eds_block(
        self, 
        block_name: str, 
        files: Dict[str, str], 
        metadata: Dict[str, Any],
        create_pr: bool = True
    ) -> Dict[str, Any]:
        """
        Push EDS block files to GitHub repository
        
        Args:
            block_name: Name of the EDS block
            files: Dict with file contents (html, css, js, etc.)
            metadata: Additional metadata (author, description, etc.)
            create_pr: Whether to create a Pull Request
            
        Returns:
            Dict with commit info, branch name, URLs
        """
        if not self.github_token:
            raise HTTPException(status_code=500, detail="GitHub token not configured")
        
        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='eds_push_')
            logger.info(f"Working in temp directory: {temp_dir}")
            
            # Build authenticated repo URL
            repo_info = self.get_repo_info()
            auth_url = f"https://{self.github_token}@github.com/{repo_info['owner']}/{repo_info['repo']}.git"
            
            # Clone repository (shallow clone for speed)
            logger.info(f"Cloning repository: {repo_info['owner']}/{repo_info['repo']}")
            repo = Repo.clone_from(
                auth_url, 
                temp_dir, 
                depth=1, 
                branch=self.base_branch
            )
            
            # Create new branch
            branch_name = self.create_branch_name(block_name)
            logger.info(f"Creating branch: {branch_name}")
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            # Prepare file paths
            sanitized_name = self.sanitize_block_name(block_name)
            block_dir = Path(temp_dir) / 'blocks' / sanitized_name
            block_dir.mkdir(parents=True, exist_ok=True)
            
            # Write files
            files_written = []
            
            # Main EDS block files
            if 'html' in files:
                html_file = block_dir / 'index.html'
                html_file.write_text(files['html'], encoding='utf-8')
                files_written.append(str(html_file.relative_to(temp_dir)))
            
            if 'css' in files:
                css_file = block_dir / 'styles.css'
                css_file.write_text(files['css'], encoding='utf-8')
                files_written.append(str(css_file.relative_to(temp_dir)))
            
            if 'js' in files:
                js_file = block_dir / 'script.js'
                js_file.write_text(files['js'], encoding='utf-8')
                files_written.append(str(js_file.relative_to(temp_dir)))
            
            # Create README with metadata
            readme_content = self.generate_readme(block_name, metadata, files)
            readme_file = block_dir / 'README.md'
            readme_file.write_text(readme_content, encoding='utf-8')
            files_written.append(str(readme_file.relative_to(temp_dir)))
            
            # Stage files
            repo.index.add(files_written)
            
            # Configure git user
            with repo.config_writer() as git_config:
                git_config.set_value("user", "name", self.author_name)
                git_config.set_value("user", "email", self.author_email)
            
            # Commit
            commit_message = f"Add EDS block: {block_name}\n\nGenerated by DXP Component Generator\nSession ID: {metadata.get('sessionId', 'unknown')}"
            commit = repo.index.commit(commit_message)
            
            # Push to remote
            logger.info(f"Pushing branch {branch_name} to remote")
            origin = repo.remote('origin')
            origin.push(branch_name)
            
            # Prepare result
            result = {
                'success': True,
                'block_name': block_name,
                'sanitized_name': sanitized_name,
                'branch_name': branch_name,
                'commit_sha': commit.hexsha,
                'commit_message': commit_message,
                'files_written': files_written,
                'commit_url': f"https://github.com/{repo_info['owner']}/{repo_info['repo']}/commit/{commit.hexsha}",
                'branch_url': f"https://github.com/{repo_info['owner']}/{repo_info['repo']}/tree/{branch_name}"
            }
            
            # Create Pull Request if requested
            if create_pr and self.github_client:
                try:
                    pr = await self.create_pull_request(
                        repo_info, 
                        branch_name, 
                        block_name, 
                        metadata
                    )
                    result['pull_request_url'] = pr.html_url
                    result['pull_request_number'] = pr.number
                except Exception as e:
                    logger.warning(f"Failed to create PR: {e}")
                    result['pr_error'] = str(e)
            
            return result
            
        except Exception as e:
            logger.error(f"Error pushing EDS block: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to push to Git: {str(e)}")
        
        finally:
            # Cleanup temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory {temp_dir}: {e}")
    
    async def create_pull_request(
        self, 
        repo_info: Dict[str, str], 
        branch_name: str, 
        block_name: str, 
        metadata: Dict[str, Any]
    ):
        """Create a Pull Request using GitHub API"""
        github_repo = self.github_client.get_repo(f"{repo_info['owner']}/{repo_info['repo']}")
        
        pr_title = f"Add EDS Block: {block_name}"
        pr_body = f"""
## New EDS Block: {block_name}

**Generated by DXP Component Generator**

### Details
- **Block Name**: {block_name}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Session ID**: {metadata.get('sessionId', 'N/A')}
- **Author**: {metadata.get('author', 'DXP Bot')}

### Description
{metadata.get('description', 'EDS block generated from user requirements.')}

### Files Added
- `blocks/{self.sanitize_block_name(block_name)}/index.html` - Main HTML structure
- `blocks/{self.sanitize_block_name(block_name)}/styles.css` - Block styles
- `blocks/{self.sanitize_block_name(block_name)}/script.js` - Block JavaScript
- `blocks/{self.sanitize_block_name(block_name)}/README.md` - Documentation

---
*This PR was auto-generated by the DXP Component Generator. Please review the generated code before merging.*
        """.strip()
        
        return github_repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base=self.base_branch
        )
    
    def generate_readme(self, block_name: str, metadata: Dict[str, Any], files: Dict[str, str]) -> str:
        """Generate README.md content for the EDS block"""
        sanitized_name = self.sanitize_block_name(block_name)
        
        readme = f"""# {block_name}

An EDS (Edge Delivery Services) block generated by DXP Component Generator.

## Overview
{metadata.get('description', 'Custom EDS block for enhanced web experiences.')}

## Usage

### HTML Structure
Add the block to your EDS page:

```html
<div class="{sanitized_name}">
  <!-- Your content here -->
</div>
```

### Files
- `index.html` - Block markup and structure
- `styles.css` - Block-specific styles
- `script.js` - Block behavior and interactions

## Generated Details
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Session ID**: {metadata.get('sessionId', 'N/A')}
- **Author**: {metadata.get('author', 'DXP Bot')}

## Implementation
1. Copy the block files to your EDS project's `/blocks/{sanitized_name}/` directory
2. Reference the block in your content using the class name `{sanitized_name}`
3. The block will be automatically loaded by EDS

---
*Generated by [DXP Component Generator](https://github.com/Vinodh-Projects/DXP-GEN-STUDIO)*
"""
        return readme
