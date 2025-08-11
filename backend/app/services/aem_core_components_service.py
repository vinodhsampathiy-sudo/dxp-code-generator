import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AEMCoreComponentsService:
    """
    Service to fetch and analyze AEM Core Components from GitHub
    to enhance AI prompts with real-world examples and patterns
    """
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = "adobe"
        self.repo_name = "aem-core-wcm-components"
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.cache_dir = Path("/app/cache/aem_components")
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Component categories for better organization
        self.component_categories = {
            "content": ["text", "title", "image", "button", "teaser"],
            "layout": ["container", "carousel", "tabs", "accordion"],
            "navigation": ["breadcrumb", "navigation", "languagenavigation"],
            "form": ["form", "formtext", "formbutton", "formoptions"],
            "media": ["image", "video", "download"],
            "social": ["sharing", "embed"]
        }
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for a given key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file exists and is not expired"""
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(data.get('cached_at', ''))
                return datetime.now() - cached_time < self.cache_duration
        except (json.JSONDecodeError, ValueError, KeyError):
            return False
    
    def _save_to_cache(self, cache_key: str, data: Any):
        """Save data to cache with timestamp"""
        cache_file = self._get_cache_file(cache_key)
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache for {cache_key}: {e}")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Any]:
        """Load data from cache if valid"""
        cache_file = self._get_cache_file(cache_key)
        
        if not self._is_cache_valid(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data.get('data')
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    async def _github_request(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        """Make authenticated GitHub API request"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'DXP-Component-Generator'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 403:
                    logger.warning("GitHub API rate limit exceeded")
                    return None
                else:
                    logger.warning(f"GitHub API request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"GitHub API request error: {e}")
            return None
    
    async def fetch_component_list(self) -> List[Dict]:
        """Fetch list of core components from GitHub"""
        cache_key = "component_list"
        cached_data = self._load_from_cache(cache_key)
        
        if cached_data:
            logger.info("Using cached component list")
            return cached_data
        
        logger.info("Fetching component list from GitHub")
        
        async with aiohttp.ClientSession() as session:
            # Get content of the main components directory
            url = f"{self.base_url}/contents/content/src/content/jcr_root/apps/core/wcm/components"
            response = await self._github_request(session, url)
            
            if not response:
                logger.error("Failed to fetch component list")
                return []
            
            components = []
            for item in response:
                if item['type'] == 'dir':
                    component_name = item['name']
                    components.append({
                        'name': component_name,
                        'path': item['path'],
                        'url': item['url'],
                        'category': self._categorize_component(component_name)
                    })
            
            self._save_to_cache(cache_key, components)
            logger.info(f"Found {len(components)} core components")
            return components
    
    def _categorize_component(self, component_name: str) -> str:
        """Categorize component based on name"""
        component_lower = component_name.lower()
        
        for category, keywords in self.component_categories.items():
            if any(keyword in component_lower for keyword in keywords):
                return category
        
        return "other"
    
    async def fetch_component_details(self, component_name: str) -> Optional[Dict]:
        """Fetch detailed information about a specific component"""
        cache_key = f"component_{component_name}"
        cached_data = self._load_from_cache(cache_key)
        
        if cached_data:
            logger.info(f"Using cached data for component: {component_name}")
            return cached_data
        
        logger.info(f"Fetching details for component: {component_name}")
        
        async with aiohttp.ClientSession() as session:
            component_details = {
                'name': component_name,
                'htl_template': None,
                'sling_model': None,
                'dialog': None,
                'clientlib': None,
                'readme': None
            }
            
            # Base path for the component
            base_path = f"content/src/content/jcr_root/apps/core/wcm/components/{component_name}/v1/{component_name}"
            
            # Fetch HTL template
            htl_url = f"{self.base_url}/contents/{base_path}.html"
            htl_content = await self._fetch_file_content(session, htl_url)
            if htl_content:
                component_details['htl_template'] = htl_content
            
            # Fetch dialog configuration
            dialog_url = f"{self.base_url}/contents/{base_path}/cq:dialog/.content.xml"
            dialog_content = await self._fetch_file_content(session, dialog_url)
            if dialog_content:
                component_details['dialog'] = dialog_content
            
            # Try to find Sling model (Java files)
            java_files = await self._find_java_files(session, component_name)
            if java_files:
                component_details['sling_model'] = java_files[0]  # Take the first/main model
            
            # Look for README or documentation
            readme_url = f"{self.base_url}/contents/content/src/content/jcr_root/apps/core/wcm/components/{component_name}/README.md"
            readme_content = await self._fetch_file_content(session, readme_url)
            if readme_content:
                component_details['readme'] = readme_content
            
            self._save_to_cache(cache_key, component_details)
            return component_details
    
    async def _fetch_file_content(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch content of a file from GitHub API"""
        response = await self._github_request(session, url)
        
        if response and 'content' in response:
            try:
                import base64
                content = base64.b64decode(response['content']).decode('utf-8')
                return content
            except Exception as e:
                logger.warning(f"Failed to decode file content: {e}")
        
        return None
    
    async def _find_java_files(self, session: aiohttp.ClientSession, component_name: str) -> List[str]:
        """Find Java Sling model files for a component"""
        # Look in the bundles/core directory for Java files
        search_paths = [
            f"bundles/core/src/main/java/com/adobe/cq/wcm/core/components/models/{component_name}",
            f"bundles/core/src/main/java/com/adobe/cq/wcm/core/components/models"
        ]
        
        java_files = []
        
        for search_path in search_paths:
            url = f"{self.base_url}/contents/{search_path}"
            response = await self._github_request(session, url)
            
            if response and isinstance(response, list):
                for item in response:
                    if item['name'].endswith('.java') and component_name.lower() in item['name'].lower():
                        file_content = await self._fetch_file_content(session, item['url'])
                        if file_content:
                            java_files.append(file_content)
        
        return java_files
    
    async def get_relevant_examples(self, user_description: str, component_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get relevant AEM Core Component examples based on user description
        """
        logger.info(f"Finding relevant examples for: {user_description}")
        
        # Get component list
        components = await self.fetch_component_list()
        
        # Score components based on relevance
        relevant_components = self._score_components(user_description, components, component_type)
        
        # Fetch details for top 3 most relevant components
        examples = {}
        for component in relevant_components[:3]:
            details = await self.fetch_component_details(component['name'])
            if details:
                examples[component['name']] = {
                    'category': component['category'],
                    'relevance_score': component['score'],
                    'htl_template': details['htl_template'],
                    'sling_model': details['sling_model'],
                    'dialog': details['dialog'],
                    'readme': details['readme']
                }
        
        return examples
    
    def _score_components(self, description: str, components: List[Dict], component_type: Optional[str] = None) -> List[Dict]:
        """Score components based on relevance to user description"""
        description_lower = description.lower()
        scored_components = []
        
        # Keywords that indicate specific component types
        keywords_map = {
            'text': ['text', 'paragraph', 'content', 'article', 'description'],
            'title': ['title', 'heading', 'header', 'h1', 'h2', 'h3'],
            'image': ['image', 'picture', 'photo', 'gallery', 'visual'],
            'button': ['button', 'cta', 'call to action', 'link', 'action'],
            'teaser': ['teaser', 'card', 'preview', 'summary'],
            'carousel': ['carousel', 'slider', 'slideshow', 'gallery'],
            'container': ['container', 'wrapper', 'layout', 'section'],
            'navigation': ['navigation', 'nav', 'menu', 'breadcrumb'],
            'form': ['form', 'input', 'field', 'submit', 'contact'],
            'tabs': ['tabs', 'tabbed', 'tab'],
            'accordion': ['accordion', 'collapsible', 'expandable']
        }
        
        for component in components:
            score = 0
            component_name = component['name'].lower()
            
            # Direct name match
            if component_name in description_lower:
                score += 10
            
            # Keyword matching
            if component_name in keywords_map:
                keywords = keywords_map[component_name]
                for keyword in keywords:
                    if keyword in description_lower:
                        score += 5
            
            # Category match
            if component_type and component['category'] == component_type:
                score += 3
            
            # Partial name match
            if any(part in description_lower for part in component_name.split('-')):
                score += 2
            
            scored_components.append({
                **component,
                'score': score
            })
        
        # Sort by score (highest first)
        return sorted(scored_components, key=lambda x: x['score'], reverse=True)
    
    def format_examples_for_prompt(self, examples: Dict[str, Any]) -> str:
        """Format examples for inclusion in AI prompts"""
        if not examples:
            return ""
        
        prompt_section = "\n## AEM Core Component Examples for Reference\n\n"
        prompt_section += "Below are relevant examples from Adobe's official AEM Core Components that you should use as reference for patterns, structure, and best practices:\n\n"
        
        for component_name, details in examples.items():
            prompt_section += f"### {component_name.title()} Component (Category: {details['category']})\n"
            
            if details.get('readme'):
                prompt_section += f"**Purpose**: {self._extract_purpose_from_readme(details['readme'])}\n\n"
            
            if details.get('htl_template'):
                prompt_section += "**HTL Template Pattern**:\n```html\n"
                prompt_section += self._truncate_content(details['htl_template'], 500)
                prompt_section += "\n```\n\n"
            
            if details.get('sling_model'):
                prompt_section += "**Sling Model Pattern**:\n```java\n"
                prompt_section += self._extract_sling_model_key_parts(details['sling_model'])
                prompt_section += "\n```\n\n"
            
            if details.get('dialog'):
                prompt_section += "**Dialog Structure Pattern**:\n```xml\n"
                prompt_section += self._truncate_content(details['dialog'], 300)
                prompt_section += "\n```\n\n"
            
            prompt_section += "---\n\n"
        
        prompt_section += "**Instructions**: Use these examples as reference for:\n"
        prompt_section += "- HTL structure and data-sly patterns\n"
        prompt_section += "- Sling Model interfaces and annotations\n"
        prompt_section += "- Dialog field configurations\n"
        prompt_section += "- Component naming conventions\n"
        prompt_section += "- CSS class naming patterns\n"
        prompt_section += "- Accessibility and semantic HTML practices\n\n"
        
        return prompt_section
    
    def _extract_purpose_from_readme(self, readme_content: str) -> str:
        """Extract component purpose from README"""
        lines = readme_content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.strip() and not line.startswith('#') and not line.startswith('The'):
                return line.strip()
        return "AEM Core Component"
    
    def _extract_sling_model_key_parts(self, java_content: str) -> str:
        """Extract key parts of Sling model (interface, annotations)"""
        lines = java_content.split('\n')
        key_parts = []
        in_interface = False
        brace_count = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Include package and imports
            if stripped.startswith('package ') or stripped.startswith('import '):
                key_parts.append(line)
            
            # Include class/interface declaration and annotations
            elif '@' in stripped or 'interface ' in stripped or 'class ' in stripped:
                key_parts.append(line)
                if 'interface ' in stripped or 'class ' in stripped:
                    in_interface = True
            
            # Include method signatures in interface
            elif in_interface and ('(' in stripped and ')' in stripped):
                key_parts.append(line)
            
            # Track braces to know when interface ends
            if in_interface:
                brace_count += stripped.count('{') - stripped.count('}')
                if brace_count <= 0 and '}' in stripped:
                    key_parts.append(line)
                    break
        
        return '\n'.join(key_parts[:30])  # Limit to 30 lines
    
    def _truncate_content(self, content: str, max_chars: int) -> str:
        """Truncate content to specified character limit"""
        if len(content) <= max_chars:
            return content
        
        truncated = content[:max_chars]
        # Try to break at a newline
        last_newline = truncated.rfind('\n')
        if last_newline > max_chars * 0.8:  # If newline is reasonably close to end
            truncated = truncated[:last_newline]
        
        return truncated + "\n... (truncated)"

# Singleton instance
aem_core_components_service = AEMCoreComponentsService()
