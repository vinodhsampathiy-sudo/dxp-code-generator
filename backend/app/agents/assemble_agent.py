import os, re, json, base64, tempfile, zipfile
from typing import TypedDict, Dict, Any

from starlette.responses import JSONResponse

from app.utils.helper_utils import HelperUtils

logger = HelperUtils.setup_logger("assemble_agent")

class AgentState(TypedDict):
    user_request: str
    block_details: Dict[str, Any]
    block_content_output: Dict[str, Any]
    final_output: Dict[str, Any]


def assemble_json(output):
    pass

    block_name = output["block_name"]
    css_code = output["css_code"]
    js_code = output["js_code"]
    mkd_table = output["markdown_table"]

    with tempfile.TemporaryDirectory() as tmpdir:
        block_dir = os.path.join(tmpdir, block_name)
        os.makedirs(block_dir, exist_ok=True)

        css_path = os.path.join(block_dir, f"{block_name}.css")
        with open(css_path, "w") as f:
            f.write(css_code)

        if js_code:
            js_path = os.path.join(block_dir, f"{block_name}.js")
            with open(js_path, "w") as f:
                f.write(js_code)

        zip_path = os.path.join(tmpdir, f"{block_name}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in os.listdir(block_dir):
                zipf.write(os.path.join(block_dir, filename), arcname=f"{block_name}/{filename}")

        zip_bytes = open(zip_path, 'rb').read()

        zip_base64 = base64.b64encode(zip_bytes).decode('utf-8')

        return {
            "zip_base64": zip_base64,
            "css": css_code,
            "js": js_code,
            "mkd_table": mkd_table,
            "file_name": f"{block_name}.zip"
        }

def assemble_node(state: AgentState) -> AgentState:
    output = state['block_content_output']
    state["final_output"] = assemble_json(output)
    return state
