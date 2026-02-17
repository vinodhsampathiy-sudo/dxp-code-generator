import os
import re
import requests
from typing import Optional, Dict, Any
from app.utils.helper_utils import HelperUtils
from app.schemas.image_schemas import FigmaParseResponse, DesignAnalysis

logger = HelperUtils.setup_logger("figma_service")

class FigmaService:
    """Service for Figma API integration"""
    
    def __init__(self):
        self.api_token = os.getenv("FIGMA_API_TOKEN")
        self.base_url = "https://api.figma.com/v1"

    def parse_url(self, url: str) -> Dict[str, str]:
        """
        Parse Figma URL to extract file ID and node ID
        
        Example URL: https://www.figma.com/file/ABC123xyz/My-File?node-id=1-2
        """
        # Extract file ID (the part after /file/)
        file_id_match = re.search(r"/file/([^/]+)", url)
        if not file_id_match:
            raise ValueError("Invalid Figma URL: Could not find file ID")
        file_id = file_id_match.group(1)
        
        # Extract node ID if present (node-id parameter)
        node_id_match = re.search(r"node-id=([^&]+)", url)
        node_id = node_id_match.group(1) if node_id_match else None
        
        # Figma uses colon in node IDs for API but URL usually uses hyphen
        # We need to normalize it if it's hyphenated but contains only digits/hyphens
        if node_id:
            node_id = node_id.replace("-", ":")
            
        return {"fileId": file_id, "nodeId": node_id}

    async def get_design_data(self, figma_url: str, user_token: Optional[str] = None) -> FigmaParseResponse:
        """
        Fetch design data from Figma and return rendered image URL and metadata
        """
        token = user_token or self.api_token
        if not token:
            raise ValueError("Figma API token is required. Set FIGMA_API_TOKEN or provide it in the request.")
            
        parsed = self.parse_url(figma_url)
        file_id = parsed["fileId"]
        node_id = parsed["nodeId"]
        
        headers = {"X-Figma-Token": token}
        
        # 1. Fetch file/node info
        # If node_id is provided, we fetch just that node
        url = f"{self.base_url}/files/{file_id}"
        if node_id:
            url += f"/nodes?ids={node_id}"
            
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Figma API error: {response.status_code} - {response.text}")
            raise Exception(f"Failed to fetch Figma data: {response.text}")
            
        data = response.json()
        file_name = data.get("name") if not node_id else data.get("nodes", {}).get(node_id, {}).get("document", {}).get("name")
        
        # 2. Get rendered image URL
        img_id = node_id if node_id else "0:1" # Default to first node if no ID
        img_url = f"{self.base_url}/images/{file_id}?ids={img_id}&format=png"
        img_response = requests.get(img_url, headers=headers)
        
        render_url = ""
        if img_response.status_code == 200:
            # Figma returns { "images": { "node_id": "url" } }
            images = img_response.json().get("images", {})
            render_url = images.get(img_id, "")
            
        # 3. Extract basic design tokens (simplified for now)
        # In a real implementation, we'd traverse the JSON tree to find colors etc.
        design_tokens = self._extract_basic_tokens(data, node_id)
        
        return FigmaParseResponse(
            fileId=file_id,
            nodeId=node_id,
            imageUrl=render_url,
            designTokens=design_tokens,
            fileName=file_name
        )

    def _extract_basic_tokens(self, data: Dict[str, Any], node_id: Optional[str]) -> DesignAnalysis:
        """Extract basic design tokens from Figma JSON data"""
        # This is a placeholder for more complex logic
        # For now, we return an empty DesignAnalysis that will be populated by Vision later
        return DesignAnalysis(
            colorPalette={},
            typography={},
            spacing={},
            interactiveElements=[]
        )
