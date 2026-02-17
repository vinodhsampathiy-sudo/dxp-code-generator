from typing import TypedDict, Dict, Any

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from app.prompts.eds.block_prompt import SYSTEM_PROMPT_EXTRACT_AGENT
from app.utils.Constants import DEFAULT_BLOCKS_LIST
from app.utils.helper_utils import HelperUtils

logger = HelperUtils.setup_logger("extract_agent")

# --- Define LangGraph Agent State ---
class AgentState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        user_request (str): The initial request from the user.
        image_url (str): Optional URL to design image.
        design_analysis (dict): Optional pre-analyzed design data.
        block_details (dict): Output from Agent 1 (extracted block requirements).
        block_content_output (dict): Output from Agent 2 (JS, CSS, Markdown, HTML).
        final_output (dict): Final assembled JSON output.
    """
    user_request: str
    image_url: str
    design_analysis: Dict[str, Any]
    block_details: Dict[str, Any]
    block_content_output: Dict[str, Any]
    final_output: Dict[str, Any]

def extract_node(state: AgentState) -> AgentState:
    """
    Agent 1: Extracts block name, style, and functionality description from user input.
    If design_analysis is provided, it will be used to enhance the extraction.
    """
    user_prompt = HelperUtils.build_eds_prompt("extract_agent_prompt.txt",{})
    
    # Build the prompt with user request
    user_content = f"**User Request**\n{state['user_request']}"
    
    # If design analysis is available, include it
    if state.get('design_analysis') and state['design_analysis']:
        design_data = state['design_analysis']
        logger.info(f"Using design analysis data in extract agent")
        
        # Add design analysis to the prompt
        user_content += f"\n\n**Design Analysis from Image:**\n"
        user_content += f"- Detected Block Type: {design_data.get('blockType', 'N/A')}\n"
        user_content += f"- Functionality: {design_data.get('functionalityDescription', 'N/A')}\n"
        user_content += f"- Interactive Elements: {', '.join(design_data.get('interactiveElements', []))}\n"
        user_content += f"- Layout Pattern: {design_data.get('layoutPattern', 'N/A')}\n"
        user_content += f"\nUse this visual analysis to inform your extraction. The block name and functionality should align with what was detected in the design."
    
    prompt = [
        ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT_EXTRACT_AGENT),
        ChatCompletionUserMessageParam(role="user", content=user_prompt),
        ChatCompletionUserMessageParam(role="user", content=user_content)
    ]
    logger.info(f"Extract Agent prompt: {prompt} \n\n")
    
    # Call OpenAI API to extract block details
    response = HelperUtils.call_openai(prompt)

    if not response:
        raise ValueError("Extraction failed")
    block_details = response.choices[0].message.content

    state['block_details'] = HelperUtils.parse_chat_response_to_json(block_details)
    logger.info(f"Extracted block details: {state['block_details']}")
    return state
