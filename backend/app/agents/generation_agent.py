from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage

llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert frontend engineer. Based on the input below, generate a clean, reusable UI component using best practices."),
    ("human", "User Prompt: {prompt}\nImage Context: {image_context}\nExamples: {examples}")
])

def generate_component_code(prompt: str, image_context: str = "", examples: str = "") -> str:
    final_prompt = template.format_messages(prompt=prompt, image_context=image_context, examples=examples)
    result = llm.invoke(final_prompt)
    return result.content