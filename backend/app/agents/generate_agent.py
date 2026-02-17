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
    image_url: str
    design_analysis: Dict[str, Any]
    block_details: Dict[str, Any]
    block_content_output: Dict[str, Any]
    final_output: Dict[str, Any]

def generate_content_node(state: AgentState) -> AgentState:
    """
    Agent 2: Generates CSS, JS, markdown table, and input HTML for the block.
    Uses design analysis data if available to generate pixel-perfect CSS.
    """
    block_details = state['block_details']
    if not block_details:
        raise ValueError("Block details are missing in the state")

    aem_methods_formatted = "\n".join([f"- {m['name']}" for m in AEM_EXPORTED_METHODS])
    block_type = block_details.get("blockType", "custom")
    
    # Build base prompt
    prompt_vars = {
        "block_name": block_details.get("blockName", "unknown"),
        "block_type": block_type,
        "block_style": block_details.get("blockStyle", "default"),
        "functionality_description": block_details.get("functionalityDescription", ""),
        "aem_methods": aem_methods_formatted
    }
    
    prompt = HelperUtils.build_eds_prompt("generate_agent_prompt.txt", prompt_vars)
    
    # Add design analysis data if available
    design_context = ""
    if state.get('design_analysis') and state['design_analysis']:
        design_data = state['design_analysis']
        logger.info("Using design analysis data in generate agent for accurate styling")
        
        design_context = "\n\n**Design Tokens from Visual Analysis:**\n"
        
        # Add color palette
        if design_data.get('colorPalette'):
            design_context += "\n**Colors:**\n"
            for color_name, color_value in design_data['colorPalette'].items():
                design_context += f"- {color_name}: {color_value}\n"
        
        # Add typography
        if design_data.get('typography'):
            design_context += "\n**Typography:**\n"
            for typo_name, typo_value in design_data['typography'].items():
                design_context += f"- {typo_name}: {typo_value}\n"
        
        # Add spacing
        if design_data.get('spacing'):
            design_context += "\n**Spacing:**\n"
            for spacing_name, spacing_value in design_data['spacing'].items():
                design_context += f"- {spacing_name}: {spacing_value}\n"
        
        # Add layout pattern
        if design_data.get('layoutPattern'):
            design_context += f"\n**Layout Pattern:** {design_data['layoutPattern']}\n"
        
        design_context += "\n**IMPORTANT:** Use these exact design tokens in your CSS. Match colors, fonts, and spacing precisely."
    
    user_prompt = [
        ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT_GENERATE_AGENT),
        ChatCompletionUserMessageParam(role="user", content=prompt + design_context),
        ChatCompletionUserMessageParam(role="user", content=f"**Block Details**\n{json.dumps(block_details, indent=2)}")
    ]

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