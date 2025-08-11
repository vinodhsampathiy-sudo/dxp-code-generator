import json
from random import sample

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from starlette.responses import JSONResponse

from app.prompts.eds.block_prompt import AEM_EXPORTED_METHODS, SYSTEM_PROMPT_GENERATE_AGENT
from app.utils.Constants import AEM_BLOCK_COLLECTION_URL
from app.utils.helper_utils import HelperUtils
from typing import Dict, Any, TypedDict

logger = HelperUtils.setup_logger("generate_agent")

class AgentState(TypedDict):
    user_request: str
    block_details: Dict[str, Any]
    block_content_output: Dict[str, Any]
    final_output: Dict[str, Any]

def generate_content_node(state: AgentState) -> AgentState:
    """
    Agent 2: Generates CSS, JS, markdown table, and input HTML for the block.
    """
    block_details = state['block_details']
    if not block_details:
        raise ValueError("Block details are missing in the state")

    aem_methods_formatted = "\n".join([f"- {m['name']}" for m in AEM_EXPORTED_METHODS])
    #logger.info(f"Generating content for block: {block_details.get('blockName', 'unknown')} with style {block_details.get('blockStyle', 'default')}")
    block_type = block_details.get("blockType", "custom")
    prompt = HelperUtils.build_eds_prompt("generate_agent_prompt.txt",{
        "block_name": block_details.get("blockName", "unknown"),
        "block_type": block_type,
        "block_style": block_details.get("blockStyle", "default"),
        "functionality_description": block_details.get("functionalityDescription", ""),
        "aem_methods": aem_methods_formatted
    })
    #logger.info(f"Generated prompt for content generation: {prompt}")
    user_prompt = [
        ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT_GENERATE_AGENT),
        ChatCompletionUserMessageParam(role="user", content=prompt),
        ChatCompletionUserMessageParam(role="user", content=f"**Block Details**\n{json.dumps(block_details, indent=2)}")
    ]

    """
    if block_type != "custom":
        url = f"{AEM_BLOCK_COLLECTION_URL}/blocks/{block_type}/{block_type}.js"
        sample_block_code = HelperUtils.fetch_content_from_url(url)
        if sample_block_code:
            logger.info(f"Using sample block code for type '{block_type}'")
            user_prompt.append(ChatCompletionUserMessageParam(role="user", content=f"**Relevant Block code**\n{sample_block_code}"))
        else:
            logger.warning(f"No sample block code found for type '{block_type}', proceeding without it")
    else:
        logger.info("No sample block code provided, proceeding with custom block generation")
    """
    logger.info(f"User prompt for content generation: {user_prompt}")
    
    # Call OpenAI API to extract block details
    response = HelperUtils.call_openai(user_prompt)

    if not response:
        raise ValueError("Extraction failed")
    block_content_details = response.choices[0].message.content
    logger.info(f"Received block content response: {block_content_details}")
    json_data = HelperUtils.parse_chat_response_to_json(block_content_details)

    json_content_data = {
        "block_name" : block_details.get("blockName", ""),
        "css_code" : json_data['cssFile']['content'],
        "js_code" : json_data['javascriptFile']['content'],
        "markdown_table" : json_data['markdownTable'],
    }

    state['block_content_output'] = json_content_data
    return state