from typing import TypedDict, Dict, Any

from fastapi.logger import logger
from langgraph.constants import END
from langgraph.graph import StateGraph
from starlette.responses import JSONResponse
from app.agents.assemble_agent import assemble_node
from app.agents.extract_agent import extract_node
from app.agents.generate_agent import generate_content_node


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

class EDSBlockService:
    def run_workflow(self, description):
        pass
        logger.info(f"Running EDS block generation workflow for description: {description}")
        # Placeholder for the actual workflow logic
        # This would typically involve calling various methods to generate the block files
        # For now, we return a mock response
        # --- Build the LangGraph ---
        workflow = StateGraph(AgentState)
        # Add nodes for each agent
        workflow.add_node("extract_requirements", extract_node)
        workflow.add_node("generate_content", generate_content_node)
        workflow.add_node("assemble_json", assemble_node)
        # Define the flow (edges)
        workflow.set_entry_point("extract_requirements")
        workflow.add_edge("extract_requirements", "generate_content")
        workflow.add_edge("generate_content", "assemble_json")
        workflow.add_edge("assemble_json", END)

        # Compile the graph
        app = workflow.compile()

        # Initial state for the graph
        initial_state = {
            "user_request": description,
            "block_details": {},
            "block_content_output": {},
            "final_output": {}
        }

        try:
            # Run the workflow with the initial state
            # Invoke the graph
            final_state = app.invoke(initial_state)
            return final_state['final_output']
        except Exception  as e:
            logger.error(f"Error generating EDS block: {str(e)}")
            return JSONResponse(content={})