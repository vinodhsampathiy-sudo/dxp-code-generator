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
        block_details (dict): Output from Agent 1 (extracted block requirements).
        block_content_output (dict): Output from Agent 2 (JS, CSS, Markdown, HTML).
        final_output (dict): Final assembled JSON output.
    """
    user_request: str
    block_details: Dict[str, Any]
    block_content_output: Dict[str, Any]
    final_output: Dict[str, Any]

def extract_node(state: AgentState) -> AgentState:
    """
    Agent 1: Extracts block name, style, and functionality description from user input.
    """
    """
    block_list = HelperUtils.get_eds_block_list("/blocks/")
    if not block_list:
        block_list = DEFAULT_BLOCKS_LIST
    block_list = block_list.get("folders", [])
    logger.info(f"block_list: {block_list}")
    """
    user_prompt = HelperUtils.build_eds_prompt("extract_agent_prompt.txt",{})
    prompt = [
        ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT_EXTRACT_AGENT),
        ChatCompletionUserMessageParam(role="user", content=user_prompt),
        ChatCompletionUserMessageParam(role="user", content=f"**User Request**\n{state['user_request']}")
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
