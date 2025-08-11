import os
import json
import re
import shutil
import subprocess
from pathlib import Path

from typing import Dict, Any, Coroutine
from dotenv import load_dotenv

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Console output
        logging.FileHandler('app.log')     # File output
    ]
)

# Set logger for your specific module
logger = logging.getLogger('app.services.project_service')
logger.setLevel(logging.INFO)

model = os.getenv("MODEL_PROVIDER", "gemini")  # Default to OpenAI if not set

class ProjectService:
    def __init__(self):
        # Load environment variables first
        load_dotenv()

        logger.info(f"In ProjectService")
    async def generate_project_structure(self, payload: str) -> dict[str, str] | dict[str, bool | str]:

        logger.info(f"In ComponentService generate_component :: payload :: {payload}")

        try:
            data = json.loads(payload)

            # Extract parameters from payload
            aem_version = data.get('aemVersion', 'cloud')
            archetype_version = data.get('archetypeVersion', '42')
            app_title = data.get('appTitle', 'My AEM Project')
            app_id = data.get('appId', 'myapp')
            group_id = data.get('groupId', 'com.mycompany')
            artifact_id = data.get('artifactId', 'myapp-project')
            package = data.get('package', 'com.mycompany.myapp')
            version = data.get('version', '0.0.1-SNAPSHOT')

            # Maven archetype command
            mvn_cmd = [
                'mvn', 'archetype:generate',
                '-DarchetypeGroupId=com.adobe.aem',
                '-DarchetypeArtifactId=aem-project-archetype',
                f'-DarchetypeVersion={archetype_version}',
                f'-DgroupId={group_id}',
                f'-DartifactId={artifact_id}',
                f'-Dversion={version}',
                f'-Dpackage={package}',
                f'-DappTitle={app_title}',
                f'-DappId={app_id}',
                f'-DaemVersion={aem_version}',
                '-DinteractiveMode=false'
            ]

            output_base = Path(__file__).parent.parent.parent.parent / "output"

            project_output_dir = os.path.join(output_base, artifact_id)

            # Remove existing directory if it exists
            if os.path.exists(project_output_dir):
                shutil.rmtree(project_output_dir)

            # Execute Maven command in output directory
            result = subprocess.run(
                mvn_cmd,
                cwd=output_base,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                return {
                    'error': 'Maven archetype generation failed',
                    'details': result.stderr
                }

            return {
                'success': True,
                'outputDir': project_output_dir,
                'message': 'AEM project generated successfully'
            }

        except Exception as e:
            logger.error(f"Project generation failed: {str(e)}")
            return {"success": False, "error": "Project generation failed.", "details": str(e)}