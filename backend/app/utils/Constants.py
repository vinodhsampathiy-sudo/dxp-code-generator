from app.prompts.eds.block_prompt import DEFAULT_BLOCKS_CODE

# Simple mapping: short keys to enum members
# Note: GPT-4.1 doesn't exist. Available models: gpt-4, gpt-4o, gpt-4-turbo
MODEL_SELECTOR = {
    "GPT_3": "gpt-3.5-turbo",
    "GPT_4": "gpt-4",
    "GPT_4o": "gpt-4o",  # Recommended: Faster, more capable than gpt-4
    "GPT_4_TURBO": "gpt-4-turbo",  # Alternative: Good balance of speed and capability
    "O1_PREVIEW": "o1-preview",  # For complex reasoning (slower, more expensive)
    "O1_MINI": "o1-mini",  # Faster version of o1-preview
    "CLAUDE_3_5_SONNET": "claude-3.5-sonnet",
    "GEMINI_1_5_PRO": "gemini-1.5-pro"
}

AEM_BLOCK_COLLECTION_URL = "https://cdn.jsdelivr.net/gh/adobe/aem-block-collection@main"

DEFAULT_BLOCKS_LIST = "accordion,cards,carousel,columns,embed,footer,form,fragment,header,hero,modal,quote,search,table,tabs,video"