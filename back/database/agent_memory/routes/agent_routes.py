from fastapi import APIRouter
from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import re

OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama API endpoint
LLM_MODEL_NAME = 'qwen3:1.7b'


agent_bp = APIRouter(prefix="/agent")

def get_llm():
    return ChatOllama(base_url=OLLAMA_BASE_URL, model=LLM_MODEL_NAME, temperature=0.0)



@agent_bp.get("/invoke")
def test():
    llm = get_llm()
    response = llm.invoke([SystemMessage('Your name is Jafar') , HumanMessage('Hi, My name is Masoud, what is your name? and how your are trained ?')])
    
    match = re.search(r'<think>(.*?)</think>(.*)', response.content, re.DOTALL)
    think_text = match.group(1).strip() if match else ''
    response_text = match.group(2).strip() if match else ''

    
    x = f'llm thinks that: {think_text} \n the response is {response_text}'
    return {"response": response_text, 'think': think_text}