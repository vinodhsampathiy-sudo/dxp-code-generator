from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Use GPT-4o for LangChain agents as GPT-5 has parameter restrictions
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

def preprocess_prompt(user_prompt: str, sys_prompt: str) -> dict:
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an AEM component generator."),
        ("human", "User Prompt: {prompt}")
    ])

    chain = prompt_template | llm
    full_response = chain.invoke({"prompt": user_prompt}).content

    return {
        "raw_extraction": full_response
    }