import base64
import os
import json
import re
import shutil
import subprocess
import time
from io import BytesIO
from urllib.request import Request
from datetime import datetime
from typing import Dict, Any, Coroutine, Optional, List, cast, Tuple

from openai import OpenAI
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from dotenv import load_dotenv
import asyncio

import logging
import sys

import anthropic
from concurrent.futures import ThreadPoolExecutor

from ..chatStorage.chat_model import ChatStorage, ChatSession, ChatMessage, GeneratedComponent
from .complexity_analyzer import ComplexityAnalyzer
from .model_selector import ModelSelector, ModelType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger('app.services.component_service')
logger.setLevel(logging.INFO)

# Global progress tracking
PROGRESS_STORE = {}

class ProgressTracker:
    def __init__(self, session_id: str, total_steps: int = 7):
        self.session_id = session_id
        self.total_steps = total_steps
        self.current_step = 0
        self.step_messages = []
        self.start_time = datetime.now()
        PROGRESS_STORE[session_id] = self
    
    def update_step(self, step: int, message: str):
        self.current_step = step
        self.step_messages.append({
            'step': step,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'progress': (step / self.total_steps) * 100
        })
        PROGRESS_STORE[self.session_id] = self
        logger.info(f"Progress Update [{step}/{self.total_steps}]: {message}")
    
    def get_progress(self):
        return {
            'session_id': self.session_id,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'progress': (self.current_step / self.total_steps) * 100,
            'messages': self.step_messages,
            'elapsed_time': (datetime.now() - self.start_time).total_seconds()
        }

class ComponentService:
    def __init__(self):
        logger.info("In ComponentService")
        load_dotenv()
        self.chat_storage = ChatStorage()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.model_selector = ModelSelector()
        
        # Initialize AI clients
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.gemini_client = genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Set default provider
        self.default_provider = "openai"  # Default to OpenAI
        
        # Initialize executor for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Component generation settings
        self.enable_caching = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
        self.parallel_processing = os.getenv('PARALLEL_PROCESSING', 'true').lower() == 'true'
        self.auto_optimize = os.getenv('AUTO_OPTIMIZE', 'true').lower() == 'true'
        
        # Cache for common patterns and snippets
        self.pattern_cache = {}
        self.progress_trackers = {}

    def get_progress(self, session_id: str) -> Dict[str, Any]:
        """Get progress for a specific session"""
        if session_id in PROGRESS_STORE:
            return PROGRESS_STORE[session_id].get_progress()
        return {
            'session_id': session_id,
            'current_step': 0,
            'total_steps': 7,
            'progress': 0,
            'messages': [],
            'elapsed_time': 0
        }

    def cleanup_progress(self, session_id: str):
        """Clean up progress tracking for completed sessions"""
        if session_id in PROGRESS_STORE:
            del PROGRESS_STORE[session_id]

    def select_model_for_component(self, user_prompt: str, model_preference: str = "auto") -> str:
        """
        Smart model selection based on component complexity and user preference.
        
        Args:
            user_prompt: The user's component description
            model_preference: "auto", "simple", "complex", "gpt-4o", "gpt-5", etc.
            
        Returns:
            Model name to use
        """
        # Direct model selection
        if model_preference in ["gpt-4o", "gpt-5", "gpt-4o-mini"]:
            return model_preference
            
        # Analyze complexity
        complexity_keywords = {
            'simple': ['card', 'button', 'text', 'image', 'basic', 'simple'],
            'complex': ['hero', 'banner', 'carousel', 'slider', 'dynamic', 'interactive', 
                       'animation', 'multi-step', 'advanced', 'configuration', 'dialog',
                       'custom styling', 'theme', 'responsive', 'positioning']
        }
        
        prompt_lower = user_prompt.lower()
        simple_score = sum(1 for keyword in complexity_keywords['simple'] if keyword in prompt_lower)
        complex_score = sum(1 for keyword in complexity_keywords['complex'] if keyword in prompt_lower)
        
        # Model selection logic
        if model_preference == "simple" or (model_preference == "auto" and simple_score > complex_score and len(user_prompt) < 100):
            return "gpt-4o"  # Cost-effective for simple components
        elif model_preference == "complex" or (model_preference == "auto" and (complex_score > simple_score or len(user_prompt) > 200)):
            return "gpt-5"   # Better consistency for complex components
        else:
            return "gpt-4o"  # Default to cost-effective option

        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def create_chat_session(self, session_title: str, user_id: Optional[str] = None, model_provider: Optional[str] = None) -> str:
        """Create a new chat session (removed app_id and package)"""
        return self.chat_storage.create_chat_session(
            session_title=session_title,
            user_id=user_id,
            model_provider=(model_provider or self.default_provider)
        )

    def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        return self.chat_storage.get_chat_session(session_id)

    def get_user_chat_sessions(self, user_id: Optional[str] = None, limit: int = 20) -> List[ChatSession]:
        """Get chat sessions for a user"""
        return self.chat_storage.get_user_chat_sessions(user_id, limit)

    def add_message_to_session(self, session_id: str, message_type: str, content: str,
                               image_data: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a message to a chat session"""
        message = ChatMessage(
            message_type=message_type,
            content=content,
            image_data=image_data,
            metadata=metadata
        )
        return self.chat_storage.add_message_to_session(session_id, message)

    def search_chat_sessions(self, search_term: str, user_id: Optional[str] = None) -> List[ChatSession]:
        """Search chat sessions"""
        return self.chat_storage.search_chat_sessions(search_term, user_id)

    def delete_chat_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        return self.chat_storage.delete_chat_session(session_id)

    def parse_json_response(self, response: str, agent_name: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            clean_response = response.replace('```json', '').replace('```', '').strip()
            start_index = clean_response.find('{')
            last_index = clean_response.rfind('}')

            if start_index == -1 or last_index == -1:
                raise ValueError('No valid JSON found in response')

            json_string = clean_response[start_index:last_index + 1]
            return json.loads(json_string)
        except Exception as error:
            logger.error(f"{agent_name} JSON Parse Error: {error}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Failed to parse JSON response from {agent_name}: {error}")

    async def call_openai_image(self, prompt: str, system_prompt: str, data_url=None, model_name: Optional[str] = None, temperature: float = 1.0):
        logger.info(f"in call_openai_image with data_url")
        messages: List[Dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{system_prompt}\n\n{prompt}"},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ]
        if not self.openai_client:
            raise ValueError("OpenAI client not configured")
        
        # GPT-5 doesn't support temperature parameter
        model_to_use = model_name or "gpt-5"
        if model_to_use == "gpt-5":
            return self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=cast(Any, messages)
            )
        else:
            return self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=cast(Any, messages),
                temperature=temperature
            )

    async def call_openai(self, prompt: str, system_prompt: str, model_name: Optional[str] = None, temperature: float = 1.0):
        logger.info(f"in call_openai without data_url")
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        if not self.openai_client:
            raise ValueError("OpenAI client not configured")
        
        # GPT-5 doesn't support temperature parameter
        model_to_use = model_name or "gpt-5"
        if model_to_use == "gpt-5":
            return self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=cast(Any, messages)
            )
        else:
            return self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=cast(Any, messages),
                temperature=temperature
            )

    async def call_openai_with_history(self, prompt: str, system_prompt: str,
                                       chat_history: Optional[List[ChatMessage]], model_name: Optional[str] = None, 
                                       temperature: float = 1.0, data_url=None):
        """Call OpenAI with chat history for refinement"""
        logger.info(f"in call_openai_with_history")

        messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

        # Add chat history
        if chat_history:
            for msg in chat_history[-10:]:  # Last 10 messages for context
                if msg.message_type == "user":
                    content = msg.content
                    if msg.image_data:
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": content}
                            ],
                        })
                    else:
                        messages.append({"role": "user", "content": content})
                else:
                    messages.append({"role": "assistant", "content": msg.content})

        # Add current prompt
        if data_url:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            })
        else:
            messages.append({"role": "user", "content": prompt})

        if not self.openai_client:
            raise ValueError("OpenAI client not configured")
        
        # GPT-5 doesn't support temperature parameter
        model_to_use = model_name or "gpt-5"
        if model_to_use == "gpt-5":
            return self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=cast(Any, messages)
            )
        else:
            return self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=cast(Any, messages),
                temperature=temperature
            )

    async def call_gemini(self, prompt: str, system_prompt: str, image_file=None, model_name: Optional[str] = None):
        if not self.gemini_configured:
            raise ValueError("Gemini model not configured")
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        # Create model lazily per call to avoid stale state in SDK
        mdl_name = model_name or os.getenv("GEMINI_MODEL", "gemini-pro")
        GenModel = getattr(genai, "GenerativeModel", None)
        if not callable(GenModel):
            raise ValueError("Gemini SDK missing GenerativeModel; please upgrade google-generativeai package")
        model = GenModel(mdl_name)
        gen_fn = getattr(model, "generate_content", None)
        if not callable(gen_fn):
            raise ValueError("Gemini model missing generate_content; please upgrade SDK")
        return gen_fn(full_prompt)

    async def call_anthropic(self, prompt: str, system_prompt: str = '', image: Optional[bytes] = None,
                             chat_history: Optional[List[ChatMessage]] = None,
                             model_name: Optional[str] = None, temperature: float = 1.0):
        if not self.anthropic_client:
            raise ValueError("Anthropic client not configured")

        # Build messages array. Anthropic supports a single system string and user messages with optional image blocks.
        content_blocks: List[Dict[str, Any]] = []
        if image is not None:
            base64_image = base64.b64encode(image).decode("utf-8")
            content_blocks.append({
                "type": "input_image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64_image,
                },
            })
        # Put the prompt as text after any image blocks
        content_blocks.append({"type": "text", "text": prompt})

        # For now, we trim history to last few user/assistant turns as plain text for additional context.
        # Anthropic messages API expects a list of messages with role and content blocks.
        messages: List[Dict[str, Any]] = []
        if chat_history:
            # Only include a small window to keep prompt size sensible
            for msg in chat_history[-6:]:
                role = "user" if msg.message_type == "user" else "assistant"
                messages.append({"role": role, "content": [{"type": "text", "text": msg.content}]})

        # Append the current user message last
        messages.append({"role": "user", "content": content_blocks})

        model = model_name or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
        # Use NOT_GIVEN when no system prompt is provided
        sys_param = system_prompt if system_prompt else anthropic.NOT_GIVEN
        return self.anthropic_client.messages.create(
            model=model,
            max_tokens=4096,
            system=cast(Any, sys_param),
            messages=cast(Any, messages),
            temperature=temperature,
        )

    async def call_groq(self, prompt: str, system_prompt: str = '',
                         chat_history: Optional[List[ChatMessage]] = None,
                         model_name: Optional[str] = None, temperature: float = 1.0):
        if not self.groq_client:
            raise ValueError("Groq client not configured")

        messages: List[Dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if chat_history:
            for msg in chat_history[-10:]:
                role = "user" if msg.message_type == "user" else "assistant"
                messages.append({"role": role, "content": msg.content})

        messages.append({"role": "user", "content": prompt})

        model = model_name or os.getenv("GROQ_MODEL", "llama3-70b-8192")
        # Groq uses an OpenAI-compatible chat.completions API
        return self.groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

    async def call_llm(self, prompt: str, system_prompt: str = '', image: Optional[bytes] = None,
                       chat_history: Optional[List[ChatMessage]] = None,
                       provider: Optional[str] = None, model_name: Optional[str] = None, 
                       temperature: float = 1.0):
        """Enhanced LLM call with optional chat history"""
        try:
            provider = (provider or self.default_provider).lower()
            
            # Handle temperature restrictions for newer OpenAI models
            if model_name in ["gpt-5"] and temperature != 1.0:
                temperature = 1.0
                logger.info(f"Adjusted temperature to 1.0 for {model_name} model")
            elif model_name in ["gpt-4o", "gpt-4o-mini"] and temperature not in [0.7, 1.0]:
                # Try default temperature for GPT-4o models if having issues
                temperature = 1.0
                logger.info(f"Adjusted temperature to 1.0 for {model_name} model compatibility")
            
            if provider == "openai":
                if image:
                    base64_image = base64.b64encode(image).decode("utf-8")
                    image_url = f"data:image/png;base64,{base64_image}"
                    logger.info(f"image_url: {image_url[:50]}")
                    return await self.call_openai_image(prompt, system_prompt, image_url, model_name, temperature)
                else:
                    if chat_history:
                        return await self.call_openai_with_history(prompt, system_prompt, chat_history, model_name, temperature)
                    else:
                        return await self.call_openai(prompt, system_prompt, model_name, temperature)
            elif provider == "gemini":
                return await self.call_gemini(prompt, system_prompt, None, model_name)
            elif provider in ("anthropic", "claude"):
                return await self.call_anthropic(prompt, system_prompt, image, chat_history, model_name, temperature)
            elif provider in ("llama", "groq"):
                if image is not None:
                    raise NotImplementedError("Llama via Groq does not support images in this build")
                return await self.call_groq(prompt, system_prompt, chat_history, model_name, temperature)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise e

    def extract_and_format_response(self, response_obj, require_html_code=False):
        """Extract JSON from provider responses and validate when needed."""
        try:
            # Coerce text content from various provider response shapes
            content = None
            try:
                # OpenAI/Groq
                if hasattr(response_obj, 'choices'):
                    content = response_obj.choices[0].message.content
                # Gemini
                elif hasattr(response_obj, 'text'):
                    content = response_obj.text  # google-generativeai response
                # Anthropic messages
                elif hasattr(response_obj, 'content') and isinstance(response_obj.content, list):
                    blocks = []
                    for block in response_obj.content:
                        if isinstance(block, dict):
                            if block.get('type') == 'text' and 'text' in block:
                                blocks.append(block['text'])
                        else:
                            # SDK models may provide objects with .type/.text
                            t = getattr(block, 'type', None)
                            txt = getattr(block, 'text', None)
                            if t == 'text' and txt:
                                blocks.append(txt)
                    content = "\n".join(blocks) if blocks else str(response_obj)
                else:
                    content = str(response_obj)
            except Exception:
                content = str(response_obj)

            logger.debug(f"in extract_and_format_response fetched content :: {content[:500]}")

            # Try to extract JSON fenced in code blocks first
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                data = json.loads(json_content)
            else:
                # Otherwise, attempt to parse entire content as JSON
                data = json.loads(content)

            if require_html_code:
                html_code = data.get('htmlCode', '')
                if not html_code:
                    raise ValueError("No htmlCode found in the JSON")

            output_data = {"data": data}
            return output_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error processing response: {e}")

    def validate_dialog_xml(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix dialog XML structure if needed"""
        try:
            if 'dialog' in response and '_cq_dialog/.content.xml' in response['dialog']:
                dialog_xml = response['dialog']['_cq_dialog/.content.xml']
                
                # Check for incorrect primary type
                if 'jcr:primaryType="nt:unstructured"' in dialog_xml and 'jcr:primaryType="cq:Dialog"' not in dialog_xml:
                    logger.warning("⚠️ Detected incorrect dialog primary type - fixing automatically")
                    # Fix the primary type
                    dialog_xml = dialog_xml.replace(
                        'jcr:primaryType="nt:unstructured"',
                        'jcr:primaryType="cq:Dialog"',
                        1  # Only replace the first occurrence (root node)
                    )
                    response['dialog']['_cq_dialog/.content.xml'] = dialog_xml
                    logger.info("✅ Fixed dialog primary type to cq:Dialog")
                
                elif 'jcr:primaryType="cq:Dialog"' in dialog_xml:
                    logger.info("✅ Dialog XML has correct primary type")
                else:
                    logger.warning("⚠️ Dialog XML structure unclear - manual review recommended")
            
            return response
        except Exception as e:
            logger.error(f"Error validating dialog XML: {e}")
            return response  # Return original response if validation fails

    async def image_agent_generate_html(self, user_prompt: str, image, chat_history: Optional[List[ChatMessage]] = None, 
                                       model_name: str = "gpt-4o", temperature: float = 1.0) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "aem" / "image_agent.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        prompt = f"""USER REQUIREMENT: {user_prompt}
        Analyze the provided image and generate HTML/CSS code."""

        # Use selected model for image analysis
        response = await self.call_llm(prompt, system_prompt, image, chat_history, 
                                     model_name=model_name, temperature=temperature)
        response = self.extract_and_format_response(response, require_html_code=True)
        return response['data'] if 'data' in response else response

    async def text_agent_generate_html(self, user_prompt: str, chat_history: Optional[List[ChatMessage]] = None, 
                                      model_name: str = "gpt-4o", temperature: float = 1.0) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "aem" / "text_agent.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        prompt = f"""USER REQUIREMENT: {user_prompt}
        Generate HTML/CSS code based on the text description."""

        # Use selected model for text-based HTML generation
        response = await self.call_llm(prompt, system_prompt, None, chat_history, 
                                     model_name=model_name, temperature=temperature)
        response = self.extract_and_format_response(response, require_html_code=True)
        return response['data'] if 'data' in response else response

    async def text_agent_generate_html(self, user_prompt: str, chat_history: Optional[List[ChatMessage]] = None, 
                                      model_name: str = "gpt-4o", temperature: float = 1.0) -> Dict[str, Any]:
        """Generate HTML/CSS from text requirements when no image is provided."""
        prompt_file = Path(__file__).parent.parent / "prompts" / "aem" / "text_prompt.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        prompt = f"""USER REQUIREMENT: {user_prompt}
        Generate clean, accessible, responsive HTML and CSS. Return JSON with keys htmlCode and cssCode as specified."""

        logger.info("Generating HTML/CSS from text requirements")
        response = await self.call_llm(prompt, system_prompt, None, chat_history)
        response = self.extract_and_format_response(response, require_html_code=True)
        return response['data'] if 'data' in response else response

    async def agent1_requirements_and_sling_model(self, user_prompt: str, chat_history: Optional[List[ChatMessage]] = None, 
                                                 model_name: str = "gpt-4o", temperature: float = 1.0) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "aem" / "agent_1.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        prompt = f"""USER REQUIREMENT: {user_prompt}
        Generate the complete analysis and Sling Model as specified."""

        # Use selected model for complex analysis
        response = await self.call_llm(prompt, system_prompt, None, chat_history, 
                                     model_name=model_name, temperature=temperature)
        logger.debug(f"in agent1_requirements_and_sling_model fetching response :: {response}")
        response = self.extract_and_format_response(response, require_html_code=False)
        logger.debug(f"in agent1_requirements_and_sling_model fetching response after extraction :: {response}")
        return response['data'] if 'data' in response else response

    async def agent2_htl_generator(self, shared_context: Dict[str, Any], sling_model: str, chat_history: Optional[List[ChatMessage]] = None, 
                                 model_name: str = "gpt-4o", temperature: float = 1.0) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "aem" /  "agent_2.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        prompt = f"""SHARED CONTEXT: {json.dumps(shared_context, indent=2)}
        SLING MODEL REFERENCE: {sling_model}
        
        CRITICAL: Ensure type-safe HTL expressions and proper BEM CSS classes.
        
        Generate the complete HTL template as specified.
        Given an AI agent has analyzed the design and provided the html and css code, generate the HTL template for the AEM component."""

        # Use selected model for HTL template generation
        response = await self.call_llm(prompt, system_prompt, None, chat_history, 
                                     model_name=model_name, temperature=temperature)
        response = self.extract_and_format_response(response, require_html_code=False)
        return response['data'] if 'data' in response else response

    async def agent3_dialog_generator(self, shared_context: Dict[str, Any], sling_model: str, chat_history: Optional[List[ChatMessage]] = None, 
                                     model_name: str = "gpt-4o", temperature: float = 1.0) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "aem" / "agent_3.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        prompt = f"""SHARED CONTEXT: {json.dumps(shared_context, indent=2)}
        SLING MODEL REFERENCE: {sling_model}
        
        ⚠️ CRITICAL REMINDER: Dialog root MUST use jcr:primaryType="cq:Dialog" (NOT nt:unstructured)
        
        Generate the complete dialog configuration as specified."""

        # Use selected model for dialog generation
        response = await self.call_llm(prompt, system_prompt, None, chat_history, 
                                     model_name=model_name, temperature=temperature)
        response = self.extract_and_format_response(response, require_html_code=False)
        
        # Validate dialog XML structure
        validated_response = self.validate_dialog_xml(response)
        return validated_response['data'] if 'data' in validated_response else validated_response

    async def agent4_client_lib_generator(self, shared_context: Dict[str, Any], htl: str, chat_history: Optional[List[ChatMessage]] = None, 
                                         model_name: str = "gpt-4o", temperature: float = 1.0) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "aem" / "agent_4.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        prompt = f"""SHARED CONTEXT: {json.dumps(shared_context, indent=2)}
        HTL REFERENCE: {htl}
        
        CRITICAL: Generate CSS classes that match HTL template exactly. Include responsive design.
        
        Generate the complete client library structure as specified."""

        # Use GPT-4o-mini for CSS generation - it's excellent at CSS and much faster
        # Use selected model for client library generation  
        response = await self.call_llm(prompt, system_prompt, None, chat_history, 
                                     model_name=model_name, temperature=temperature)
        response = self.extract_and_format_response(response, require_html_code=False)
        return response['data'] if 'data' in response else response

    async def generate_aem_component(self, user_prompt: str, image, session_id: Optional[str] = None, model_preference: str = "auto") -> Dict[str, Any]:
        """Main orchestrator method with chat history support and progress tracking"""
        import time
        start_time = time.time()
        
        # Initialize progress tracker
        if not session_id:
            session_id = f"temp_{int(time.time())}"
        
        progress = ProgressTracker(session_id, total_steps=7)
        progress.update_step(1, "🚀 Starting AEM Component Generation...")
        
        logger.info('🚀 Starting AEM Component Generation...')
        
        # Smart model selection based on complexity and preference
        selected_model = self.select_model_for_component(user_prompt, model_preference)
        logger.info(f'📊 Selected model: {selected_model} (preference: {model_preference})')
        
        # Set temperature to 1.0 for all models to ensure compatibility
        temperature = 1.0

        # Get chat history if session_id is provided
        chat_history = []
        if session_id and session_id != f"temp_{int(time.time())}":
            session = self.get_chat_session(session_id)
            if session:
                chat_history = session.messages

        try:
            # Image/Text Agent (if needed)
            progress.update_step(2, "📝 Processing input and analyzing requirements...")
            image_gen_start = time.time()
            image_gen_result = None
            if image:
                logger.info('🖼️  Image Agent: Processing image input...')
                image_gen_result = await self.image_agent_generate_html(user_prompt, image, chat_history, selected_model, temperature)
                logger.debug(f"Image generation result: {image_gen_result}")
            else:
                logger.info('📝 Text Agent: Processing text input...')
                image_gen_result = await self.text_agent_generate_html(user_prompt, chat_history, selected_model, temperature)
                logger.debug(f"Text-based HTML/CSS generation result: {image_gen_result}")
            
            image_gen_time = time.time() - image_gen_start
            logger.info(f'⏱️  Image/Text Agent completed in {image_gen_time:.2f}s')

            # Agent 1: Requirements Analysis & Sling Model
            progress.update_step(3, "🧠 Agent 1: Analyzing requirements and generating Sling Model...")
            agent1_start = time.time()
            logger.info('🔍 Agent 1: Analyzing requirements and generating Sling Model...')
            agent1_result = await self.agent1_requirements_and_sling_model(user_prompt, chat_history, selected_model, temperature)
            logger.debug(f'Agent 1: fetching agent1_result{agent1_result}')
            
            agent1_time = time.time() - agent1_start
            logger.info(f'⏱️  Agent 1 completed in {agent1_time:.2f}s')

            if 'sharedContext' not in agent1_result or 'slingModel' not in agent1_result:
                raise ValueError('Agent 1 failed to generate required outputs')

            # If image was provided, merge its results into shared context
            if image_gen_result:
                agent1_result['sharedContext'].update(image_gen_result)

            shared_content = agent1_result['sharedContext']

            # Agents 2 & 3: Run in parallel for maximum speed
            progress.update_step(4, "⚡ Agents 2&3: Generating HTL and Dialog in parallel...")
            parallel_start = time.time()
            logger.info('⚡ Agent 2 & 3: Generating HTL and Dialog in parallel....')
            agent2_task = self.agent2_htl_generator(agent1_result['sharedContext'], agent1_result['slingModel'], chat_history, selected_model, temperature)
            agent3_task = self.agent3_dialog_generator(agent1_result['sharedContext'], agent1_result['slingModel'], chat_history, selected_model, temperature)

            agent2_result, agent3_result = await asyncio.gather(agent2_task, agent3_task)
            
            parallel_time = time.time() - parallel_start
            logger.info(f'⏱️  Agents 2 & 3 completed in parallel in {parallel_time:.2f}s')

            logger.debug(f'Agent 3: fetching agent3_result{agent3_result}')

            if 'htl' not in agent2_result or 'dialog' not in agent3_result:
                raise ValueError('Agent 2 or 3 failed to generate required outputs')

            # Agent 4: Client Library (needs HTL from Agent 2)
            progress.update_step(5, "🎨 Agent 4: Generating Client Libraries...")
            agent4_start = time.time()
            logger.info('🎨 Agent 4: Generating Client Library...')
            agent4_result = await self.agent4_client_lib_generator(
                agent1_result['sharedContext'],
                agent2_result['htl'],
                chat_history,
                selected_model,
                temperature
            )
            
            agent4_time = time.time() - agent4_start
            logger.info(f'⏱️  Agent 4 completed in {agent4_time:.2f}s')

            if 'clientLib' not in agent4_result:
                raise ValueError('Agent 4 failed to generate required outputs')

            # Final assembly
            progress.update_step(6, "📁 Creating component files and structure...")
            
            # Combine final results
            final_result = {
                'htl': agent2_result['htl'],
                'slingModel': agent1_result['slingModel'],
                'dialog': agent3_result['dialog'],
                'content_xml': agent3_result['.content.xml'],
                'clientLib': agent4_result['clientLib'],
                'slingModelName': shared_content['slingModelName'],
                'componentName': shared_content['componentName']
            }

            progress.update_step(7, "✅ Component generation complete!")
            total_time = time.time() - start_time
            logger.info(f'✅ AEM Component Generation completed successfully in {total_time:.2f}s!')
            logger.info(f'📊 Timing breakdown: Image/Text: {image_gen_time:.1f}s, Agent1: {agent1_time:.1f}s, Agents2&3: {parallel_time:.1f}s, Agent4: {agent4_time:.1f}s')
            
            return final_result

        except Exception as error:
            total_time = time.time() - start_time
            progress.update_step(-1, f"❌ Generation failed: {str(error)}")
            logger.error(f'❌ AEM Component Generation failed after {total_time:.2f}s: {error}')
            raise error

    async def generate_component(self, prompt: str, image,
                                 session_id: Optional[str] = None, user_id: Optional[str] = None, 
                                 model_preference: str = "auto", image_url: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced generate_component with chat history support (removed app_id/package)"""
        logger.info(f"In ComponentService generate_component :: {prompt}")

        # Create or get session
        if not session_id:
            session_title = prompt[:50] + "..." if len(prompt) > 50 else prompt
            session_id = self.create_chat_session(session_title, user_id)

        # Add user message to session
        image_data = None
        if image:
            if isinstance(image, bytes):
                image_data = base64.b64encode(image).decode('utf-8')
                image_data = f"data:image/png;base64,{image_data}"
            elif isinstance(image, str) and image.startswith('data:'):
                image_data = image

        # Store image_url in message metadata if present
        msg_metadata = {"image_url": image_url} if image_url else None
        self.add_message_to_session(session_id, "user", prompt, image_data, msg_metadata)

        try:
            component_data = await self.generate_aem_component(prompt, image, session_id, model_preference)

            logger.debug(f"In ComponentService ai_output :: {component_data}")

            try:
                logger.debug(f"In ComponentService parsed component_data :: {component_data}")

                if not all(key in component_data for key in ['slingModel', 'htl', 'dialog']):
                    raise ValueError('Incomplete AI output keys received')

            except (json.JSONDecodeError, ValueError) as json_err:
                logger.error(f"❌ Failed to parse AI response as JSON. Content was: {component_data}")
                raise json_err

            # Generate sanitized component name
            sanitized_component_name = re.sub(r'[^a-z0-9]', '', component_data['componentName'].lower().replace(' ', ''))

            # Handle dialog data - check if it's the new structure or old structure
            dialog_content = component_data['dialog']
            if isinstance(dialog_content, dict):
                # New structure: dialog is a dict with "_cq_dialog/.content.xml" key
                if '_cq_dialog/.content.xml' in dialog_content:
                    dialog_code = dialog_content['_cq_dialog/.content.xml']
                else:
                    # Fallback: take the first value if the key is different
                    dialog_code = next(iter(dialog_content.values()))
            else:
                # Old structure: dialog is a string
                dialog_code = dialog_content

            # Create GeneratedComponent object and save to session
            generated_component = GeneratedComponent(
                component_name=component_data['componentName'],
                sling_model_name=component_data['slingModelName'],
                htl_code=component_data['htl'],
                sling_model_code=component_data['slingModel'],
                dialog_code=dialog_code,
                content_xml=component_data['content_xml'],
                client_lib=component_data['clientLib'],
                generation_metadata={
                    'sanitized_name': sanitized_component_name
                }
            )

            # Add component to session
            self.chat_storage.add_component_to_session(session_id, generated_component)

            # Add AI response message to session
            ai_response = f"Component '{component_data['componentName']}' generated successfully!"
            ai_metadata = {
                'component_id': generated_component.component_id,
                'component_name': component_data['componentName']
            }
            if image_url:
                ai_metadata['image_url'] = image_url
            self.add_message_to_session(session_id, "ai", ai_response, None, ai_metadata)

            # Create actual files in the output directory
            # Use default values for app_id and package since they're handled in prompts
            output_dirs = self._create_component_files(
                component_data,
                "myapp",  # Default app_id - can be made configurable
                "com.mycompany.myapp",  # Default package - can be made configurable
                sanitized_component_name,
                component_data['slingModelName']
            )

            return {
                "success": True,
                "message": "✅ Component generated successfully.",
                "session_id": session_id,
                "component_id": generated_component.component_id,
                "outputDirs": output_dirs,
                "structure": self._create_folder_structure("myapp", sanitized_component_name),  # Use default
                "aiOutput": component_data,
                "image_url": image_url
            }

        except Exception as e:
            # Add error message to session
            error_message = f"Failed to generate component: {str(e)}"
            self.add_message_to_session(session_id, "ai", error_message)

            logger.error(f"Component generation failed: {str(e)}")
            return {
                "success": False,
                "error": "Component generation failed.",
                "details": str(e),
                "session_id": session_id
            }

    async def refine_component(self, session_id: str, component_id: str, refinement_prompt: str,
                               user_id: Optional[str] = None) -> Dict[str, Any]:
        """Refine an existing component based on user feedback"""
        logger.info(f"Refining component {component_id} in session {session_id}")

        # Get the session and component
        session = self.get_chat_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        component = self.chat_storage.get_component_by_id(session_id, component_id)
        if not component:
            return {"success": False, "error": "Component not found"}

        # Add refinement message to session
        self.add_message_to_session(session_id, "user", refinement_prompt, None, {
            'action': 'refine',
            'component_id': component_id
        })

        try:
            # Create refinement context with existing component
            refinement_context = f"""
            REFINEMENT REQUEST: {refinement_prompt}
            
            EXISTING COMPONENT TO REFINE:
            Component Name: {component.component_name}
            Sling Model Name: {component.sling_model_name}
            
            CURRENT HTL CODE:
            {component.htl_code}
            
            CURRENT SLING MODEL CODE:
            {component.sling_model_code}
            
            CURRENT DIALOG CODE:
            {component.dialog_code}
            
            CURRENT CLIENT LIB:
            {json.dumps(component.client_lib, indent=2)}
            
            Please refine the component based on the user's request while maintaining the existing structure and improving upon it.
            """

            # Generate refined component
            refined_data = await self.generate_aem_component(refinement_context, None, session_id)

            # Handle dialog data - check if it's the new structure or old structure
            dialog_content = refined_data['dialog']
            if isinstance(dialog_content, dict):
                # New structure: dialog is a dict with "_cq_dialog/.content.xml" key
                if '_cq_dialog/.content.xml' in dialog_content:
                    dialog_code = dialog_content['_cq_dialog/.content.xml']
                else:
                    # Fallback: take the first value if the key is different
                    dialog_code = next(iter(dialog_content.values()))
            else:
                # Old structure: dialog is a string
                dialog_code = dialog_content

            # Create new refined component
            refined_component = GeneratedComponent(
                component_name=refined_data.get('componentName', component.component_name),
                sling_model_name=refined_data.get('slingModelName', component.sling_model_name),
                htl_code=refined_data['htl'],
                sling_model_code=refined_data['slingModel'],
                dialog_code=dialog_code,
                content_xml=refined_data['content_xml'],
                client_lib=refined_data['clientLib'],
                generation_metadata={
                    'action': 'refinement',
                    'original_component_id': component_id,
                    'refinement_prompt': refinement_prompt
                }
            )

            # Add refined component to session
            self.chat_storage.add_component_to_session(session_id, refined_component)

            # Add AI response
            ai_response = f"Component refined successfully based on your request!"
            self.add_message_to_session(session_id, "ai", ai_response, None, {
                'component_id': refined_component.component_id,
                'action': 'refinement_complete'
            })

            # Generate sanitized component name
            sanitized_name = re.sub(r'[^a-z0-9]', '', refined_component.component_name.lower().replace(' ', ''))

            # Create files for refined component
            session_metadata = session.dict()
            output_dirs = self._create_component_files(
                refined_data,
                session_metadata.get('app_id', 'myapp'),
                session_metadata.get('package', 'com.mycompany.myapp'),
                sanitized_name,
                refined_component.sling_model_name
            )

            return {
                "success": True,
                "message": "✅ Component refined successfully.",
                "session_id": session_id,
                "component_id": refined_component.component_id,
                "original_component_id": component_id,
                "outputDirs": output_dirs,
                "aiOutput": refined_data
            }

        except Exception as e:
            error_message = f"Failed to refine component: {str(e)}"
            self.add_message_to_session(session_id, "ai", error_message)

            logger.error(f"Component refinement failed: {str(e)}")
            return {
                "success": False,
                "error": "Component refinement failed.",
                "details": str(e),
                "session_id": session_id
            }

    def get_session_components(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all components from a session"""
        session = self.get_chat_session(session_id)
        if not session:
            return []

        components = []
        for component in session.generated_components:
            components.append({
                'component_id': component.component_id,
                'component_name': component.component_name,
                'sling_model_name': component.sling_model_name,
                'generation_timestamp': component.generation_timestamp.isoformat(),
                'metadata': component.generation_metadata
            })

        return components

    def _create_component_files(self, component_data: Dict, app_id: str, package: str, component_name: str, slingModelName: str) -> Dict[str, str]:
        """Create actual files in the filesystem similar to JavaScript version"""

        # Prepare sanitized names and paths
        pkg_path = package.replace(".", "/")

        # Define output paths aligned with Maven archetype structure
        base_output_dir = Path(__file__).parent.parent.parent.parent / "project_code"

        sling_model_dir = base_output_dir / "core/src/main/java/com/adobe/aem/guides/wknd/core/models"

        # Check if ui_apps_dir exists and update component_name if needed
        # initial_ui_apps_dir = base_output_dir / "ui.apps/src/main/content/jcr_root/apps/wknd/components" / component_name
        # if initial_ui_apps_dir.exists():
        #     component_name = component_name + "aiComponent"

        ui_apps_dir = base_output_dir / "ui.apps/src/main/content/jcr_root/apps/wknd/components" / component_name
        ui_apps_clientlib_dir = ui_apps_dir / "clientlib"
        ui_apps_clientlib_js_dir = ui_apps_clientlib_dir / "js"
        ui_apps_clientlib_css_dir = ui_apps_clientlib_dir / "css"

        # Ensure all directories exist
        base_output_dir.mkdir(parents=True, exist_ok=True)
        sling_model_dir.mkdir(parents=True, exist_ok=True)
        ui_apps_dir.mkdir(parents=True, exist_ok=True)
        ui_apps_clientlib_dir.mkdir(parents=True, exist_ok=True)
        ui_apps_clientlib_js_dir.mkdir(parents=True, exist_ok=True)
        ui_apps_clientlib_css_dir.mkdir(parents=True, exist_ok=True)

        # Helper function to process content and convert escaped newlines to actual newlines
        def process_file_content(content: str) -> str:
            """Convert escaped newlines and other escape sequences to actual characters"""
            if isinstance(content, str):
                content = content.replace('\\n', '\n')
                content = content.replace('\\t', '\t')
                content = content.replace('\\"', '"')
                content = content.replace("\\'", "'")
                content = content.replace('\\\\', '\\')
            return content

        # Write Sling Model Java class directly from AI output
        java_file_path = sling_model_dir / f"{slingModelName}.java"
        with open(java_file_path, 'w', encoding='utf-8') as f:
            f.write(process_file_content(component_data['slingModel']))

        # Write .content.xml file directly from AI output
        content_xml_file_path = ui_apps_dir / f".content.xml"
        with open(content_xml_file_path, 'w', encoding='utf-8') as f:
            f.write(process_file_content(component_data['content_xml']))

        htl_file_path = ui_apps_dir / f"{component_name}.html"
        with open(htl_file_path, 'w', encoding='utf-8') as f:
            f.write(process_file_content(component_data['htl']))

        # Handle dialog data - check if it's the new structure or old structure
        dialog_content = component_data['dialog']
        if isinstance(dialog_content, dict):
            # New structure: dialog is a dict with "_cq_dialog/.content.xml" key
            if '_cq_dialog/.content.xml' in dialog_content:
                dialog_code = dialog_content['_cq_dialog/.content.xml']
            else:
                # Fallback: take the first value if the key is different
                dialog_code = next(iter(dialog_content.values()))
        else:
            # Old structure: dialog is a string
            dialog_code = dialog_content

        dialog_file_path = ui_apps_dir / "_cq_dialog.xml"
        with open(dialog_file_path, 'w', encoding='utf-8') as f:
            f.write(process_file_content(dialog_code))

        # Handle clientlib files with consistent format
        if 'clientLib' in component_data:
            logger.info("found clientLib in component_data")
            clientlib_data = component_data['clientLib']
            logger.debug(f"after fetching clientLib data :: {clientlib_data}")

            # Handle each file in clientLib
            for file_path, file_data in clientlib_data.items():
                # Extract file content based on structure
                if isinstance(file_data, dict) and 'fileContents' in file_data:
                    content = file_data['fileContents']
                elif isinstance(file_data, str):
                    content = file_data
                else:
                    logger.warning(f"Unexpected file data format for {file_path}: {file_data}")
                    continue

                # Process content to convert escaped characters
                content = process_file_content(content)

                # Determine target directory and write file
                if file_path == 'js.txt':
                    target_path = ui_apps_clientlib_dir / "js.txt"
                elif file_path == 'css.txt':
                    target_path = ui_apps_clientlib_dir / "css.txt"
                elif file_path == '.content.xml':
                    target_path = ui_apps_clientlib_dir / ".content.xml"
                elif file_path.startswith('js/') and file_path.endswith('.js'):
                    filename = file_path.split('/')[-1]
                    target_path = ui_apps_clientlib_js_dir / filename
                elif file_path.startswith('css/') and file_path.endswith('.css'):
                    filename = file_path.split('/')[-1]
                    target_path = ui_apps_clientlib_css_dir / filename
                elif file_path.endswith('.js'):
                    target_path = ui_apps_clientlib_js_dir / file_path
                elif file_path.endswith('.css'):
                    target_path = ui_apps_clientlib_css_dir / file_path
                else:
                    logger.warning(f"Unknown file type: {file_path}")
                    continue

                # Write the file
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created file: {target_path}")

        logger.debug(f"✅ Files created successfully in {base_output_dir}")

        return {
            "coreJavaDir": str(sling_model_dir),
            "uiAppsDir": str(ui_apps_dir)
        }

    def _create_folder_structure(self, app_id: str, component_name: str) -> Dict[str, Any]:
        """Create folder structure (app_id used only for display)"""
        return {
            "name": f"output/{app_id}",
            "type": "folder",
            "children": [
                {
                    "name": "core",
                    "type": "folder",
                    "children": [
                        {
                            "name": "src/main/java",
                            "type": "folder",
                            "children": [
                                {
                                    "name": f"{component_name}.java",
                                    "type": "file"
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "ui.apps",
                    "type": "folder",
                    "children": [
                        {
                            "name": f"src/main/content/jcr_root/apps/{app_id}/components/{component_name}",
                            "type": "folder",
                            "children": [
                                {"name": "component.html", "type": "file"},
                                {"name": "_cq_dialog.xml", "type": "file"}
                            ]
                        }
                    ]
                }
            ]
        }

    def __del__(self):
        """Cleanup MongoDB connection when service is destroyed"""
        if hasattr(self, 'chat_storage'):
            self.chat_storage.close_connection()