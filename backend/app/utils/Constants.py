from app.prompts.eds.block_prompt import DEFAULT_BLOCKS_CODE

# Simple mapping: short keys to model names with cost and capability info
MODEL_SELECTOR = {
    "GPT_3": "gpt-3.5-turbo",        # Cheapest, basic tasks
    "GPT_4": "gpt-4",                # Standard reasoning
    "GPT_4o": "gpt-4o",              # Fast, capable, cost-effective ($5/$15 per 1M tokens)
    "GPT_4o_MINI": "gpt-4o-mini",    # Fastest, cheapest for simple tasks ($0.15/$0.60 per 1M tokens)
    "GPT_4_TURBO": "gpt-4-turbo",    # Good balance of speed and capability
    "GPT_5": "gpt-5",                # Best reasoning, most expensive ($10/$30 per 1M tokens)
    "O1_PREVIEW": "o1-preview",       # For complex reasoning (slower, more expensive)
    "O1_MINI": "o1-mini",            # Faster version of o1-preview
    "CLAUDE_3_5_SONNET": "claude-3.5-sonnet",
    "GEMINI_1_5_PRO": "gemini-1.5-pro"
}

AEM_BLOCK_COLLECTION_URL = "https://cdn.jsdelivr.net/gh/adobe/aem-block-collection@main"

DEFAULT_BLOCKS_LIST = "accordion,cards,carousel,columns,embed,footer,form,fragment,header,hero,modal,quote,search,table,tabs,video"