import os, requests, re, json, logging
from datetime import datetime
from typing import Dict, Any

import httpx
from bs4 import BeautifulSoup
from fastapi.logger import logger

from app.utils.Constants import MODEL_SELECTOR, AEM_BLOCK_COLLECTION_URL
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI
from typing import List, Union

env = Environment(loader=FileSystemLoader("app/templates"))

from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam, ChatCompletion,
)

Message = Union[
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
]

class HelperUtils:
    """Common helper utility functions."""

    @staticmethod
    def setup_logger(name: str = "app_logger", level=logging.INFO) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(level)
        return logger

    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """Reads a JSON file and returns a dictionary."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def write_json(data: Dict[str, Any], file_path: str) -> None:
        """Writes a dictionary to a JSON file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def read_file(file_path: str) -> str:
        """Reads the contents of a text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def write_file(content: str, file_path: str) -> None:
        """Writes string content to a text file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def get_env_var(key: str, default: Any = None) -> Any:
        """Get an environment variable or default."""
        return os.getenv(key, default)

    @staticmethod
    def timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Returns current timestamp formatted."""
        return datetime.now().strftime(fmt)

    @staticmethod
    def snake_to_camel(snake_str: str) -> str:
        """Converts snake_case to camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def camel_to_snake(camel_str: str) -> str:
        """Converts camelCase to snake_case."""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


    @staticmethod
    def call_openai(
            messages:List[Message],
            model: str = MODEL_SELECTOR.get("GPT_4o"),  # Default to cost-effective GPT-4o
            temperature: float = 0.7,
            max_tokens: int = 1000
    ) -> ChatCompletion:
        """Calls OpenAI chat completion using the new OpenAI client SDK."""

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        client = OpenAI(api_key=api_key)

        try:
            # GPT-5 doesn't support temperature parameter, only pass it for other models
            if model == "gpt-5":
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens
                )
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            return response
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")

    @staticmethod
    def sanitize_content(text_content: str) -> str:
        text_content = re.sub(r'^\s*/\*[\s\S]*?\*/', '', text_content, flags=re.MULTILINE)

        # Remove single-line comments at the top (// ...)
        text_content = re.sub(r'^\s*//.*$', '', text_content, flags=re.MULTILINE)

        # Remove extra blank lines and leading/trailing whitespace
        lines = [line.strip() for line in text_content.splitlines() if line.strip()]
        return ' '.join(lines)

    @staticmethod
    def fetch_content_from_url(url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch content from URL {url}: {e}")
            return ""

    @staticmethod
    def build_eds_prompt(prompt_name: str, input_data: dict) -> str:
        with open(f"app/prompts/eds/{prompt_name}", "r") as f:
            template = env.from_string(f.read())
            return template.render(**input_data)

    @staticmethod
    def parse_chat_response_to_json(response_txt: str):
        """
        Extracts and parses JSON from a Markdown-formatted code block.
        """
        # Remove ```json and ``` markers
        json_str = re.sub(r"^```json\n", "", response_txt)
        json_str = re.sub(r"\n```$", "", json_str)

        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.info("Failed to parse JSON:", e)
            return {}

        if isinstance(json_data, list):
            return json_data
        elif isinstance(json_data, dict):
            return json_data
        else:
            return {}

    @staticmethod
    def get_eds_block_list(folder_name: str) -> Dict[str, List[str]]:
        url = f"{AEM_BLOCK_COLLECTION_URL}{folder_name}"
        folders: List[str] = []
        files: List[str] = []

        try:
            html = HelperUtils.fetch_content_from_url(url)
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.select('div.listing tr a'):
                path = link.get('href') or ''
                if path.startswith("/gh"):
                    parts = [p for p in path.split('/') if p]
                    if path.endswith('/'):
                        block_name = parts[-1] if parts else None
                        if block_name:
                            folders.append(block_name)
                    else:
                        file_name = parts[-1] if parts else None
                        if file_name:
                            files.append(file_name)
        except Exception as e:
            logger.info('Error fetching data:', e)

        return {"folders": folders, "files": files}

